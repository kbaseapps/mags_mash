import requests
import json

search_db = 'JGI_MAGS'

def query_sketch_mags(sw_url, input_upas, auth_token):
    '''
    Query the sketch service for items related to the workspace reference.

    sw_url: service wizard url
    input_upas: list of workspace references
    n_max_results: number of results to return
    auth_token: authorization token
    '''
    sketch_url = get_sketch_service_url(sw_url)

    results = {}
    for upa in input_upas:
        payload = {
            "method":"get_homologs",
            "params": {
                'ws_ref': upa,
                'search_db': search_db,
                'n_max_results': 500
            }
        }

        print('='*80)
        print('sketch_url:',sketch_url)
        print('='*80)

        resp = requests.post(url=sketch_url, data=json.dumps(payload),
                             headers={'content-type':'application/json', 'authorization':auth_token})
        results[upa] = parse_response(resp.json())
    return results

def parse_response(resp):
    '''
    parse the resonse from the sketch service.

    resp: json response body from sketch service
    '''
    if resp.get('error'):
        raise RuntimeError("Sketch Service Error: ",resp['error'])
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
    '''
    get the most recent sketch_service url from the service wizard. 

    sw_url: service wizard url
    '''
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
