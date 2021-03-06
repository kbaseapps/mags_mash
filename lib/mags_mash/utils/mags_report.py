from installed_clients.KBaseReportClient import KBaseReport
# from installed_clients.WorkspaceClient import Workspace
# from installed_clients.DataFileUtilClient import DataFileUtil
from jinja2 import Environment, PackageLoader, select_autoescape
# import pandas as pd
import math
import uuid
import os

# def get_location_markers(ids, source=None):
#     '''
#     For now this simply returns 1 marker with
#     the location of LBL. Returns list of markers

#     ids: list of ids

#     marker format:
#     {
#         'name': name of marker
#         'lat': latitude as a float
#         'lng': longitude as a float
#         'details': pop up details

#     }
#     '''
#     markers = [
#         {'name':"LBL", "lat":37.877344, "lng":-122.250694, "details":"This is Lawrence Berkeley National Laboratory."},
#         {'name':"Golden Gate Bridge", "lat": 37.817060, "lng": -122.478206, "details":"This is the Golden Gate Bridge."},
#         {'name':"SFO Airport", 'lat':37.616310, 'lng': -122.386793, 'details':"This is San Francisco International Airport."},
#         {'name':"Mount Diablo", "lat": 37.881523, "lng": -121.914325, "details":"This is Mount Diablo."}
#     ]
#     if source!= None:
#         for m in markers:
#             m['source'] = "Input source:"+source

#     return markers


# def get_statistics(ids, GOLD, upa_name=None):
#     '''
#     get statistics from the GOLD and statitics csvs

#     ids:
#     GOLD: 
#     '''
#     dist_compl = {}

#     output = []
#     currdir = os.path.dirname(__file__)
#     stats_path = os.path.join(currdir, 'data', 'Stats-taxonomy.csv')
#     Stats = pd.read_csv(stats_path)
#     curr_stats = Stats[Stats['binid'].isin(ids.keys())]
#     curr_stats = curr_stats.fillna('Unknown')
#     for id_ in ids:
#         curr = {}
#         dist, kb_id, relatedids = ids[id_]
#         if upa_name != None:
#             curr['input_name'] = upa_name
#         curr['dist'] = dist
#         # if kb_id:
#         #     curr['kb_id'] = kb_id
#         # else:
#         #     curr['kb_id'] = ''
#         id_stats = curr_stats[curr_stats.binid == id_]
#         curr['completeness'] = id_stats.iloc[0]['completeness']
#         curr['contamination'] = id_stats.iloc[0]['contamination']
#         curr['MIMAG'] = id_stats.iloc[0]['MIMAG']
#         curr['mag_id'] = id_
#         curr['IMG_Genome_ID'] = id_.split('_')[0]

#         img_link = "https://img.jgi.doe.gov/cgi-bin/m/main.cgi?section=MetaDetail&page=metagenomeBinScaffolds&taxon_oid=%s&bin_name=%s"%(id_.split('_')[0], id_)
#         curr['IMG_link'] = img_link
#         if relatedids:
#             for key in relatedids:
#                 if relatedids[key]:
#                     curr[key] = relatedids[key]
#                 else:
#                     curr[key] = 'Unknown'
#         if relatedids['GOLD_Analysis_ID']:
#             curr['project'] = GOLD[GOLD['GOLD Analysis Project ID'] == relatedids['GOLD_Analysis_ID']].iloc[0]['Project / Study Name']
#             dist_compl[curr['project']] = (round(curr['dist'], 3), round(curr['completeness'], 2))
#         else:
#             curr['project'] = 'Unknown'
#             dist_compl['Unknown'] = (round(curr['dist'], 3), round(curr['completeness'], 2))

#         output.append(curr)

#     return output, dist_compl


# def ids_to_info(ids, upa_name=None):
#     """
#     """
#     # fill this in when we actually have acess to GOLD data
#     # we're going to use pandas to read in the csv files we have

#     gold_id_to_id = {val[2]['GOLD_Analysis_ID']:key for key, val in ids.items()}
#     currdir = os.path.dirname(__file__)
#     gold_path = os.path.join(currdir,'data','GOLD-metadata.csv')
#     # print('currdir:',currdir,os.listdir('data'))
#     GOLD = pd.read_csv(gold_path)
    
#     curr_GOLD = GOLD[GOLD['GOLD Analysis Project ID'].isin(gold_id_to_id.keys())]
#     tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
#                  'Ecosystem Type','Specific Ecosystem','Project / Study Name']

#     curr_GOLD = curr_GOLD.fillna({col:"Unknown" for col in tree_cols})
#     # dist_compl = dictionary from 'Project / Study Name' -> (Distance, Completeness)

#     stats, dist_compl = get_statistics(ids, curr_GOLD, upa_name=upa_name)
#     markers = get_location_markers(gold_id_to_id.values())

#     return stats, dist_compl, markers, curr_GOLD

# def ids_to_info_multi(query_results, upa_to_name):
#     """
#     """
#     # fill this in when we actually have acess to GOLD data
#     # we're going to use pandas to read in the csv files we have

#     GOLD = []
#     upas = []
#     stats = []
#     markers = []
#     dist_compl = {}
#     max_num = 0
#     upa_names = []
#     for upa in query_results:
#         upa_name = upa_to_name[upa]
#         upa_names.append(upa_name)

#         id_to_dist_and_kbid_and_relatedids = query_results[upa]
#         upa_stats, upa_dist_compl, upa_markers, upa_GOLD = ids_to_info(id_to_dist_and_kbid_and_relatedids, upa_name=upa_name)
#         for key in upa_dist_compl:
#             dist_compl[key] = upa_dist_compl[key]

#         stats += upa_stats
#         upa_GOLD['upa'] = upa
#         GOLD.append(upa_GOLD)
#         upas.append(upa)

#         max_num += len(id_to_dist_and_kbid_and_relatedids)
#         # for now we just set markers to upa_markers 
#         markers=upa_markers

#     GOLD = pd.concat(GOLD, ignore_index=True)
#     tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
#                 'Ecosystem Type','Specific Ecosystem','Project / Study Name']

#     # dist_compl = dictionary from 'Project / Study Name' -> (Distance, Completeness)
#     tree = create_tree(GOLD, tree_cols, dist_compl, max_num, source_order=upas)
#     sources = [0 for _ in range(len(upas))]
#     for i in range(len(upas)):
#         sources[i]+= sum([t['sources'][i] for t in tree])
#     total_num = sum(sources)
#     tree_wrapper = {"truncated_name":"", "count":"({})".format(str(total_num)), 'count_num':total_num, 'sources':sources, "children":tree}

#     return stats, tree_wrapper, markers, upa_names


# name_max_len = 115

# def create_tree(GOLD, tree_cols, dist_compl, max_num, source_order=None):
#     """
#     """
#     tree = []
#     if len(tree_cols) == 0:
#         return tree
#     col = tree_cols[0]
#     type_count = GOLD[col].value_counts().to_dict()

#     for t in type_count:
#         # if len(t) > name_max_len:
#         #     name = t[:name_max_len] + '...'
#         # else:
#         #     name = t
#         count = "({})".format(type_count[t])
#         leaf = create_tree(GOLD[GOLD[col]==t], tree_cols[1:], dist_compl, max_num, source_order=source_order)
#         if leaf == []:
#             if col == "Project / Study Name":
#                 dist, compl = dist_compl[t]
#             else:
#                 dist, compl =  "",""
#             trunc_name = GOLD[GOLD["Project / Study Name"] == t].iloc[0]['IMG Genome ID ']
#             # is terminal node/actually a leaf
#             tree.append({
#                 'truncated_name': str(trunc_name),
#                 'name' : t,
#                 'count': "",
#                 'compl': str(compl),
#                 'dist' : str(dist)
#             })
#         else:  
#             tree.append({
#                 'truncated_name':t,
#                 'count':count,
#                 'children':leaf
#             })
#         if source_order!=None:
#             source_count = GOLD[GOLD[col]==t]['upa'].value_counts().to_dict()
#             sources = []
#             for s in source_order:
#                 if s in source_count:
#                     sources.append(source_count[s])
#                 else:
#                     sources.append(0)

#             tree[-1]['sources'] = sources
#     return tree

env = Environment(loader=PackageLoader('mags_mash','utils/templates'),
                  autoescape=select_autoescape(['html']))


# def get_upa_names(ws_url, cb_url, upas):
#     """
#     """
#     ws = Workspace(ws_url)
#     objs = ws.get_object_info3({
#         'objects': [{'ref':upa} for upa in upas]
#     })

#     upa_to_name = {'/'.join([str(info[6]), str(info[0]), str(info[4])]):info[1] for info in objs['infos']}
#     missing_upas = list(set(upas) - set(upa_to_name.keys()))
#     if len(missing_upas) < 1:
#         return upa_to_name

#     dfu = DataFileUtil(cb_url)
#     objs = dfu.get_objects({'object_refs':missing_upas})
#     if len(objs) != len(missing_upas):
#         raise ValueError("Could not find all input names. len upas: %s  len objs: %s"%(len(upas), len(objs)), upas, objs['infos'])
#     for obj in objs:
#         info = obj['info']
#         upa = '/'.join([str(info[6]), str(info[0]), str(info[4])])
#         upa_to_name[upa] = info[1]
#     return upa_to_name

def htmlify(cb_url, stats, upa_names, tree, markers):
    """
    """
    minimum_step = 0.001
    num_steps = 100

    min_dist   = math.floor(100*min([s['dist'] for s in stats]))/100.0
    max_dist   = math.ceil(100*max([s['dist'] for s in stats]))/100.0
    step_dist  = max( round((max_dist-min_dist)/num_steps, 3), minimum_step)
    min_compl  = math.floor(100*min([s['completeness'] for s in stats]))/100.0
    max_compl  = math.ceil(100*max([s['completeness'] for s in stats]))/100.0
    step_compl = max( round((max_dist-min_dist)/num_steps, 3), minimum_step)
    min_cont   = math.floor(100*min([s['contamination'] for s in stats]))/100.0
    max_cont   = math.ceil(100*max([s['contamination'] for s in stats]))/100.0
    step_cont  = max( round((max_dist-min_dist)/num_steps, 3), minimum_step)

    # if len(query_results) == 1:
        # key = list(query_results.keys())[0]
        # id_to_dist_and_kbid_and_relatedids = query_results[key]

        # stats, dist_compl, markers, curr_GOLD = ids_to_info(id_to_dist_and_kbid_and_relatedids)
        # tree_cols = ['Ecosystem','Ecosystem Category','Ecosystem Subtype',\
        #             'Ecosystem Type','Specific Ecosystem','Project / Study Name']
        # tree = create_tree(curr_GOLD, tree_cols, dist_compl, len(curr_GOLD))
        # tree = {"truncated_name":"", "count":"({})".format(str(len(id_to_dist_and_kbid_and_relatedids))), "count_num":len(id_to_dist_and_kbid_and_relatedids), "children":tree}

    if len(upa_names) == 1:

        # for now convert IDs we have to report
        template = env.get_template("index.html")
        return template.render(tree=tree, stats=stats, markers=markers, ranges=[min_dist, max_dist, step_dist, min_compl, max_compl, step_compl, min_cont, max_cont, step_cont])

    elif len(upa_names) > 1:
        # upa_to_name = get_upa_names(ws_url, cb_url, list(query_results.keys()))
        # # sources = upa_to_name.values()
        # stats, tree, markers, sources = ids_to_info_multi(query_results, upa_to_name)

        number_of_points = max(list(tree['sources'].values()))

        short_sources = []
        sources_len = 18
        for s in upa_names:
            s = str(s)
            if len(s) <= sources_len:
                short_sources.append(s)
            else:
                short_sources.append(s[:sources_len-3] + '...')

        template = env.get_template("index_multi.html")
        return template.render(tree=tree, stats=stats, markers=markers, number_of_points=number_of_points, sources=upa_names, short_sources=short_sources,
                ranges=[min_dist, max_dist, step_dist, min_compl, max_compl, step_compl, min_cont, max_cont, step_cont])
    else:
        raise ValueError("Error in query result handling")

def generate_report(cb_url, scratch, workspace_name, stats, upa_names, tree, markers):
# def generate_report(ws_url, cb_url, scratch, workspace_name, query_results): # id_to_dist_and_kbid_and_relatedids):
    """
    """
    report_name = 'Mags_Mash_'+str(uuid.uuid4())
    report_file = os.path.join(scratch, report_name)
    os.mkdir(report_file)
    html_path = os.path.join(report_file, 'index.html')
    # js_path = os.path.join(report_file, 'tree_script.js')

    html_output = htmlify(cb_url, stats, upa_names, tree, markers)
    # html_output = htmlify(ws_url, cb_url, query_results)

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
