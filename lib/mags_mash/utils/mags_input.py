from installed_clients.DataFileUtilClient import DataFileUtil

def parse_input_upa(cb_url, upa):
    dfu = DataFileUtil(cb_url)

    obj_data = dfu.get_objects({"object_refs":[upa]})['data'][0]
    obj_type  = obj_data['info'][2]
    
    if 'KBaseSets.GenomeSet' in obj_type:
        upas = [gsi['ref'] for gsi in gs_obj['items']]
    elif 'KBaseSearch.GenomeSet' in obj_type:
        upas = [gse['ref'] for gse in gs_obj['elements'].values()]
    elif "KBaseGenomes.ContigSet" in obj_type or "KBaseGenomeAnnotations.Assembly" in obj_type or "KBaseGenomes.Genome" in obj_type
        upas = [upa]
    else:
        raise TypeError("provided input must of type 'KBaseSets.GenomeSet','KBaseSearch.GenomeSet','KBaseGenomes.ContigSet','KBaseGenomeAnnotations.Assembly' or 'KBaseGenomes.Genome' not " +str(obj_type))        
    return upas