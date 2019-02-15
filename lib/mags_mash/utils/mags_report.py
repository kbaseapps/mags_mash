from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.DataFileUtilClient import DataFileUtil
from jinja2 import Environment, PackageLoader, select_autoescape
import pandas as pd
import subprocess
import uuid
import os

def get_location_markers(ids):
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
    return [
        {'name':"LBL", "lat":37.877344, "lng":-122.250694, "details":"This is Lawrence Berkeley National Laboratory."},
        {'name':"Golden Gate Bridge", "lat": 37.817060, "lng": -122.478206, "details":"This is the Golden Gate Bridge."},
        {'name':"SFO Airport", 'lat':37.616310, 'lng': -122.386793, 'details':"This is San Francisco International Airport."},
        {'name':"Mount Diablo", "lat": 37.881523, "lng": -121.914325, "details":"This is Mount Diablo."}
    ]

def get_statistics(ids, GOLD, upa=None):
    '''
    get statistics from the GOLD and statitics csvs

    ids:
    GOLD: 
    '''
    dist_compl = {}

    output = []
    currdir = os.path.dirname(__file__)
    stats_path = os.path.join(currdir, 'data', 'Stats-taxonomy.csv')
    Stats = pd.read_csv(stats_path)
    curr_stats = Stats[Stats['binid'].isin(ids.keys())]
    curr_stats = curr_stats.fillna('Unknown')
    for id_ in ids:
        curr = {}
        dist, kb_id, relatedids = ids[id_]
        if upa != None:
            curr['input_upa'] = upa
        curr['dist'] = dist
        if kb_id:
            curr['kb_id'] = kb_id
        else:
            curr['kb_id'] = ''
        id_stats = curr_stats[curr_stats.binid == id_]
        curr['completeness'] = id_stats.iloc[0]['completeness']
        curr['contamination'] = id_stats.iloc[0]['contamination']
        curr['MIMAG'] = id_stats.iloc[0]['MIMAG']
        curr['mag_id'] = id_

        if relatedids:
            for key in relatedids:
                if relatedids[key]:
                    curr[key] = relatedids[key]
                else:
                    curr[key] = 'Unknown'
        if relatedids['GOLD_Analysis_ID']:
            curr['project'] = GOLD[GOLD['GOLD Analysis Project ID'] == relatedids['GOLD_Analysis_ID']].iloc[0]['Project / Study Name']
            dist_compl[curr['project']] = (round(curr['dist'], 3), round(curr['completeness'], 2))
        else:
            curr['project'] = 'Unknown'
            dist_compl['Unknown'] = (round(curr['dist'], 3), round(curr['completeness'], 2))

        output.append(curr)

    return output, dist_compl


def ids_to_info(ids, upa=None):
    """
    """
    # fill this in when we actually have acess to GOLD data
    # we're going to use pandas to read in the csv files we have

    gold_id_to_id = {val[2]['GOLD_Analysis_ID']:key for key, val in ids.items()}
    currdir = os.path.dirname(__file__)
    gold_path = os.path.join(currdir,'data','GOLD-metadata.csv')
    # print('currdir:',currdir,os.listdir('data'))
    GOLD = pd.read_csv(gold_path)
    
    curr_GOLD = GOLD[GOLD['GOLD Analysis Project ID'].isin(gold_id_to_id.keys())]
    tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
                 'Ecosystem Type','Specific Ecosystem','Project / Study Name']

    curr_GOLD = curr_GOLD.fillna({col:"Unknown" for col in tree_cols})
    # dist_compl = dictionary from 'Project / Study Name' -> (Distance, Completeness)

    stats, dist_compl = get_statistics(ids, curr_GOLD, upa=upa)
    markers = get_location_markers(gold_id_to_id.values())

    return stats, dist_compl, markers, curr_GOLD

def ids_to_info_multi(query_results):
    """
    """
    # fill this in when we actually have acess to GOLD data
    # we're going to use pandas to read in the csv files we have

    GOLD = []
    upas = []
    dist_compl = {}
    for upa in query_results:
        id_to_dist_and_kbid_and_relatedids = query_results[key]
        upa_stats, upa_dist_compl, upa_markers, upa_GOLD = ids_to_info(id_to_dist_and_kbid_and_relatedids, upa=upa)
        for key in upa_dist_compl:
            dist_compl[key] = upa_dist_compl[key]

        stats += upa_stats
        upa_GOLD['upa'] = upa
        GOLD.append(curr_GOLD)
        upas.append(upa)

    GOLD = pd.concat(GOLD, ignore_index=True)
    tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
                'Ecosystem Type','Specific Ecosystem','Project / Study Name']

    # dist_compl = dictionary from 'Project / Study Name' -> (Distance, Completeness)
    tree = create_tree(GOLD, tree_cols, dist_compl, len(curr_GOLD), source_order=upas)
    tree_wrapper = {"name":"", "count":"({})".format(str(len(ids))), "children":tree}

    return stats, tree_wrapper, markers


name_max_len = 115

def create_tree(GOLD, tree_cols, dist_compl, max_num, source_order=None):
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
        leaf = create_tree(GOLD[GOLD[col]==t], tree_cols[1:], dist_compl, max_num)
        if leaf == []:
            if col == "Project / Study Name":
                dist, compl = dist_compl[t]
            else:
                dist, compl =  "",""
            trunc_name = GOLD[GOLD["Project / Study Name"] == t].iloc[0]['IMG Genome ID ']
            # is terminal node/actually a leaf
            tree.append({
                'truncated_name': trunc_name,
                'name' : t,
                'count': "",
                'count_num':max_num,
                'compl': str(compl),
                'dist' : str(dist)
            })
        else:           
            tree.append({
                'truncated_name':t,
                'count':count,
                'count_num':type_count[t],
                'children':leaf
            })
        if source_order!=None:
            source_count = GOLD['upa']
            sources = [source_count[s] for s in source_order]
            tree[-1]['sources'] = sources
    return tree

env = Environment(loader=PackageLoader('mags_mash','utils/templates'),
                  autoescape=select_autoescape(['html']))


def get_upa_names(cb_url, upas):
    """
    """
    dfu = DataFileUtil(cb_url)
    objs = dfu.get_objects({'object_refs':upas})['data']
    return [obj['info'][1] for obj in objs]

def htmlify(cb_url, query_results):
    """
    """
    if len(query_results) == 1:
        key = list(query_results.keys())[0]
        id_to_dist_and_kbid_and_relatedids = query_results[key]

        stats, dist_compl, markers, curr_GOLD = ids_to_info(id_to_dist_and_kbid_and_relatedids)
        tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
                    'Ecosystem Type','Specific Ecosystem','Project / Study Name']
        tree = create_tree(curr_GOLD, tree_cols, dist_compl, len(curr_GOLD))
        tree = {"name":"", "count":"({})".format(str(len(id_to_dist_and_kbid_and_relatedids))), "children":tree}

        # for now convert IDs we have to report
        template = env.get_template("index.html")
        return template.render(tree=tree, stats=stats, markers=markers), 'templates/tree_script.js'
    elif len(query_results) > 1:
        stats = []
        stats, tree, markers = ids_to_info_multi(query_results)

        sources = get_upa_names(cb_url, list(query_results.keys()))
        number_of_points = max(tree['sources'])

        template = env.get_template("index_multi.html")
        return template.render(tree=tree, stats=stats, markers=markers, number_of_points=number_of_points, sources=sources), 'templates/multi_tree_script.js'
    else:
        raise ValueError("Error in query result handling")


def generate_report(cb_url, scratch, workspace_name, query_results): # id_to_dist_and_kbid_and_relatedids):
    """
    """
    report_name = 'Mags_Mash_'+str(uuid.uuid4())
    report_file = os.path.join(scratch, report_name)
    os.mkdir(report_file)
    html_path = os.path.join(report_file, 'index.html')
    js_path = os.path.join(report_file, 'tree_script.js')

    html_output, js_output = htmlify(cb_url, query_results)

    subprocess.check_output(['cp',js_output, js_path])

    with open(html_path, 'w') as f:
        f.write(html_output)
    
    html_link = {
        'path': report_file,
        'name': 'index.html',
        'description':"MAG Mash output html report"
    }
    report = KBaseReport(cb_url)
    report_info = report.create_extended_report({
        'direct_html_link_index':0,
        'html_links':[html_link],
        'workspace_name': workspace_name,
        'report_object_name':report_name
    })
    return {
        'report_name':report_info['name'],
        'report_ref':report_info['ref']
    }
