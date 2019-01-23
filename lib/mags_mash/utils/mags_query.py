import requests
import json

search_db = 'JGI_MAGS'

def query_ahs_mags(sw_url, ws_ref, n_max_results):
    payload = {
        "method":"get_homologs",
        "params": {
            'ws_ref': ws_ref,
            'search_db': search_db,
            'n_max_results': n_max_results
        }
    }
    sketch_url = get_sketch_service_url(sw_url)
    resp = requests.post(url=sketch_url, data=json.dumps(payload),
                         headers={'content-type':'application/json'})
    return parse_response(resp.json())
    
def parse_response(resp):
    if resp.get('error'):
        raise RuntimeError("Sketch Service Error: "+resp['error'])
    if not resp.get('result'): 
        raise ValueError("No results in JSON response body")
    if not resp['result'].get('distances'):
        raise ValueError("No Distances in JSON response")

    id_to_dist_and_kbid_and_relatedids = {}
    for d in resp['result']['distances']:
        id_ = d.get('sourceid')
        kb_id = d.get('kbase_id', None)
        relatedids = d.get('relatedids', None)
        dist = float(d.get('dist'))
        id_to_dist_and_kbid_and_relatedids[id_] = (dist, kb_id, relatedids)
    return id_to_dist_and_kbid_and_relatedids


def get_sketch_service_url(sw_url):
    json_obj = {
        "method":"ServiceWizard.get_service_status",
        "id":"",
        "params":[{"module_name":"sketch_service","version":"beta"}],
        "version":"1.1"
    }
    sw_resp = requests.post(url=sw_url, data=json.dumps(json_obj))
    sketch_resp = sw_resp.json()
    sketch_url = sketch_resp['result'][0]['url']
    return sketch_url
