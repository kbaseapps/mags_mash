from installed_clients.AssemblyUtilClient import AssemblyUtil

def get_fasta(cb_url, ws_ref):
    au = AssemblyUtil(cb_url)
    res = au.get_assembly_as_fasta({'ref':ws_ref})
    return res['path']

