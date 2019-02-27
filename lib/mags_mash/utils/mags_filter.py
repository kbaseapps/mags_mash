from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil

import numpy as np
import pandas as pd
import os
from scipy.cluster.hierarchy import linkage, leaves_list


def create_tree(GOLD, tree_cols, dist_compl, source_order=None):
    """
    """
    tree = []
    if len(tree_cols) == 0:
        return tree
    col = tree_cols[0]
    type_count = GOLD[col].value_counts().to_dict()

    for t in type_count:
        # if len(t) > name_max_len:
        #     name = t[:name_max_len] + '...'
        # else:
        #     name = t
        count = "({})".format(type_count[t])
        leaf = create_tree(GOLD[GOLD[col]==t], tree_cols[1:], dist_compl, source_order=source_order)
        if leaf == []:
            if col == "Project / Study Name":
                dist, compl, cont = dist_compl[t]
            else:
                dist, compl, cont =  "","", ""
            trunc_name = GOLD[GOLD["Project / Study Name"] == t].iloc[0]['IMG Genome ID ']
            # is terminal node/actually a leaf
            tree.append({
                'truncated_name': str(trunc_name),
                'name' : t,
                'count': "",
                'compl': str(compl),
                'cont' :str(cont),
                'dist' : str(dist)
            })
        else:  
            tree.append({
                'truncated_name':t,
                'count':count,
                'children':leaf
            })
        if source_order!=None:
            source_count = GOLD[GOLD[col]==t]['upa'].value_counts().to_dict()
            sources = []
            for s in source_order:
                if s in source_count:
                    sources.append(source_count[s])
                else:
                    sources.append(0)

            tree[-1]['sources'] = sources
    return tree

def get_location_markers(ids, source=None):
    '''
    For now this simply returns 1 marker with
    the location of LBL. Returns list of markers

    ids: list of ids

    marker format:
    {
        'name': name of marker
        'lat': latitude as a float
        'lng': longitude as a float
        'details': pop up details

    }
    '''
    markers = [
        {'name':"LBL", "lat":37.877344, "lng":-122.250694, "details":"This is Lawrence Berkeley National Laboratory."},
        {'name':"Golden Gate Bridge", "lat": 37.817060, "lng": -122.478206, "details":"This is the Golden Gate Bridge."},
        {'name':"SFO Airport", 'lat':37.616310, 'lng': -122.386793, 'details':"This is San Francisco International Airport."},
        {'name':"Mount Diablo", "lat": 37.881523, "lng": -121.914325, "details":"This is Mount Diablo."}
    ]
    if source!= None:
        for m in markers:
            m['source'] = "Input source:"+source

    return markers


def unwind_tree(X, tree):
    """
    """
    if tree.get('children'):
        for t in tree['children']:
            X.append(t['sources'])
            X = unwind_tree(X, t)
    return X


def remap_sources(sources, upa_order):
    new_sources = {}
    for j, i in enumerate(upa_order):
        val = sources[i]
        if val != 0:
            new_sources[j] = val
    return new_sources


def rewind_tree(tree, upa_order):
    """
    """
    for t_ix, t in enumerate(tree['children']):
        new_sources = remap_sources(t['sources'], upa_order)
        t['sources'] = new_sources
        if t.get('children'):
            t = rewind_tree(t, upa_order)
        tree['children'][t_ix] = t
    return tree


def get_source_order(tree, upa_names):
    """
    stats:
    """
    X = unwind_tree([tree['sources']], tree)
    X = np.transpose(np.array(X))
    z = linkage(X, 'ward')
    upa_order = leaves_list(z)
    return upa_order


def filter_results(ws_url, cb_url, query_results, n_max_results, max_distance, min_completeness, max_contamination):
    """
    Here we do a combiantion of getting all the relevant statistics from the data csv, filtering
    the outputs according to the provided inputs, and staging some of the outputs for the templates.
    """
    if len(query_results) > 1:
        upa_to_name = get_upa_names(ws_url, cb_url, list(query_results.keys()))
    else:
        upa_to_name = {list(query_results.keys())[0]:""}


    currdir = os.path.dirname(__file__)
    gold_path = os.path.join(currdir,'data','GOLD-metadata.csv')
    GOLD = pd.read_csv(gold_path)
    upa_names = []
    upas = []
    dist_compl = {}

    all_GOLD = []

    # id_to_inputs = defaultdict(lambda:[])

    stats = []

    for upa in query_results:
        upas.append(upa)
        upa_name = upa_to_name[upa]
        curr_GOLD = GOLD[GOLD['GOLD Analysis Project ID'].isin([val[2]['GOLD_Analysis_ID'] for key, val in query_results[upa].items()])]
        tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
                     'Ecosystem Type','Specific Ecosystem','Project / Study Name']

        curr_GOLD = curr_GOLD.fillna({col:"Unknown" for col in tree_cols})

        curr_stats = get_statistics(query_results[upa], curr_GOLD, upa_name=upa_name)
        curr_stats, curr_dist_compl = filter_stats(curr_stats, n_max_results, max_distance, min_completeness, max_contamination)

        curr_GOLD = curr_GOLD[curr_GOLD['GOLD Analysis Project ID'].isin([s['GOLD_Analysis_ID'] for s in curr_stats])]
        curr_GOLD['upa'] = upa
        all_GOLD.append(curr_GOLD)

        for key in curr_dist_compl:
            # id_to_inputs[key].append(upa_name)
            dist_compl[key] = curr_dist_compl[key]


        stats += curr_stats
        upa_names.append(upa_name)

    all_GOLD = pd.concat(all_GOLD, ignore_index=True)

    tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
                'Ecosystem Type','Specific Ecosystem','Project / Study Name']
    if len(upas) == 1:
        tree = create_tree(all_GOLD, tree_cols, dist_compl)
        count = len(query_results[upas[0]])
        tree = {"truncated_name":"", "count":"({})".format(str(count)), "count_num":count, "children":tree}
    else:
        tree = create_tree(all_GOLD, tree_cols, dist_compl, source_order=upas)
        sources = [0 for _ in range(len(upa_names))]
        for i in range(len(upa_names)):
            sources[i]+= sum([t['sources'][i] for t in tree])
        total_num = sum(sources)
        tree = {"truncated_name":"", "count":"({})".format(str(total_num)), 'count_num':total_num, 'sources':sources, "children":tree}

        upa_order = get_source_order(tree, upa_names)
        tree['sources'] = remap_sources(tree['sources'], upa_order)
        tree = rewind_tree(tree, upa_order)
        new_upa_names = []
        for i in upa_order:
            new_upa_names.append(upa_names[i])
        upa_names = new_upa_names

    # TEMPORARY MARKER SET UP
    markers = get_location_markers(set([s['mag_id'] for s in stats]))

    return stats, upa_names, tree, markers


def filter_stats(stats, n_max_results, max_distance, min_completeness, max_contamination):
    if max_distance:
        stats = [s for s in stats if s['dist'] <= max_distance]
    if min_completeness:
        stats = [s for s in stats if s['completeness'] >= min_completeness]
    if max_contamination:
        stats = [s for s in stats if s['contamination'] <= max_contamination]
    stats = sorted(stats, key=lambda s: s['dist'])
    if len(stats) > n_max_results:
        stats = stats[:n_max_results]
    dist_compl = {s['project']:(round(s['dist'], 3), round(s['completeness'], 2), round(s['contamination'], 2)) for s in stats}
    return stats, dist_compl

def get_upa_names(ws_url, cb_url, upas):
    """
    """
    ws = Workspace(ws_url)
    objs = ws.get_object_info3({
        'objects': [{'ref':upa} for upa in upas]
    })

    upa_to_name = {'/'.join([str(info[6]), str(info[0]), str(info[4])]):info[1] for info in objs['infos']}
    if len(upa_to_name)==len(upas):
        return upa_to_name

    missing_upas = list(set(upas) - set(list(upa_to_name.keys())))

    dfu = DataFileUtil(cb_url)
    objs = dfu.get_objects({'object_refs':missing_upas})['data']
    if len(objs) != len(missing_upas):
        raise ValueError("Could not find all input names. len upas: %s  len objs: %s"%(len(upas), len(objs)), upas, [obj['info'] for obj in objs])
    for obj in objs:
        info = obj['info']
        upa = '/'.join([str(info[6]), str(info[0]), str(info[4])])
        upa_to_name[upa] = info[1]
    return upa_to_name


def get_statistics(ids, GOLD, upa_name=None):
    '''
    get statistics from the GOLD and statitics csvs

    ids:
    GOLD: 
    '''
    output = []
    currdir = os.path.dirname(__file__)
    stats_path = os.path.join(currdir, 'data', 'Stats-taxonomy.csv')
    Stats = pd.read_csv(stats_path)
    curr_stats = Stats[Stats['binid'].isin(ids.keys())]
    curr_stats = curr_stats.fillna('Unknown')
    for id_ in ids:
        curr = {}
        dist, kb_id, relatedids = ids[id_]
        if upa_name != None:
            curr['input_name'] = upa_name
        curr['dist'] = dist
        # if kb_id:
        #     curr['kb_id'] = kb_id
        # else:
        #     curr['kb_id'] = ''
        id_stats = curr_stats[curr_stats.binid == id_]
        curr['completeness'] = id_stats.iloc[0]['completeness']
        curr['contamination'] = id_stats.iloc[0]['contamination']
        curr['MIMAG'] = id_stats.iloc[0]['MIMAG']
        curr['mag_id'] = id_
        curr['IMG_Genome_ID'] = id_.split('_')[0]

        img_link = "https://img.jgi.doe.gov/cgi-bin/m/main.cgi?section=MetaDetail&page=metagenomeBinScaffolds&taxon_oid=%s&bin_name=%s"%(id_.split('_')[0], id_)
        curr['IMG_link'] = img_link
        if relatedids:
            for key in relatedids:
                if relatedids[key]:
                    curr[key] = relatedids[key]
                else:
                    curr[key] = 'Unknown'
        if relatedids['GOLD_Analysis_ID']:
            curr['project'] = GOLD[GOLD['GOLD Analysis Project ID'] == relatedids['GOLD_Analysis_ID']].iloc[0]['Project / Study Name']
        else:
            curr['project'] = 'Unknown'

        output.append(curr)

    return output
