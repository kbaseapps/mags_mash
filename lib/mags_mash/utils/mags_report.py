from installed_clients.KBaseReportClient import KBaseReport
from jinja2 import Environment, PackageLoader, select_autoescape
import pandas as pd
import uuid
import os

def get_location_markers(ids):
    '''
    For now this simply returns 1 marker with
    the location of LBL

    returns list of markers

    marker format:
    {
        'name': name of marker
        'lat': latitude as a float
        'lng': longitude as a float
        'details': pop up details

    }
    '''
    return [{'name':'LBL', 'lat':37.877344, 'lng':-122.250694, 'details':""}]

def get_statistics(ids, GOLD):
    '''
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
            curr['project'] = GOLD[GOLD['GOLD Analysis Project ID'] == relatedids['GOLD_Analysis_ID']]
        else:
            curr['project'] = 'Unknown'

        output.append(curr)

    return output


def ids_to_info(ids):
    '''    
    '''
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
    tree = create_tree(curr_GOLD, [], tree_cols)
    markers = get_location_markers(gold_id_to_id.values())
    stats = get_statistics(ids, curr_GOLD)
    return stats, tree, markers


def create_tree(GOLD, tree, tree_cols):
    '''
    '''    
    if len(tree_cols) == 0:
        return tree
    col = tree_cols[0]
    type_count = GOLD[col].value_counts().to_dict()
    for t in type_count:
        if type_count[t] > 1:
            name = t+" ({})".format(type_count[t])
        else:
            name = t
        tree.append(
            {
                'name':name,
                'children':create_tree(GOLD[GOLD[col]==t], [], tree_cols[1:])
            }
        )
    return tree

env = Environment(loader=PackageLoader('mags_mash','utils/templates'),
                  autoescape=select_autoescape(['html']))


def htmlify(id_to_dist_and_kbid_and_relatedids):
    '''
    '''
    stats, tree, markers = ids_to_info(id_to_dist_and_kbid_and_relatedids)
    # for now convert IDs we have to report
    template = env.get_template('output_template.html')
    return template.render(tree=tree, stats=stats, markers=markers)

    
def generate_report(cb_url, scratch, workspace_name, id_to_dist_and_kbid_and_relatedids):
    '''
    '''
    report_name = 'Mags_Mash_'+str(uuid.uuid4())

    html_output = htmlify(id_to_dist_and_kbid_and_relatedids)
    report_file = os.path.join(scratch, report_name)
    os.mkdir(report_file)
    html_path = os.path.join(report_file, 'output.html')

    with open(html_path, 'w') as f:
        f.write(html_output)
    
    html_link = {
        'path': report_file,
        'name': 'output.html',
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
