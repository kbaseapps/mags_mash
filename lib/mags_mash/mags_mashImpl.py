# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
from .utils.mags_query import query_sketch_mags
from .utils.mags_report import generate_report
from .utils.mags_input import parse_input_upa
#END_HEADER


class mags_mash:
    '''
    Module Name:
    mags_mash

    Module Description:
    A KBase module: mags_mash
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/kbaseapps/mags_mash.git"
    GIT_COMMIT_HASH = "62d7d5d2ab8a0bef2d5bf70009399cb630e05f5e"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.sw_url = config['srv-wiz-url']
        self.auth_token = os.environ['KB_AUTH_TOKEN']
        self.ws_url = config["workspace-url"]
        #END_CONSTRUCTOR
        pass


    def run_mags_mash(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_mags_mash
        if params.get('ws_ref'):
            ws_ref = params.get('ws_ref')
        else:
            raise ValueError("Assembly Reference must be provided")
        if params.get('n_max_results'):
            n_max_results = params.get('n_max_results')
        else:
            raise ValueError("n_max_results was not set properly")

        input_upas = parse_input_upa(self.callback_url, ws_ref)

        # id_to_dist_and_kbid_and_relatedids = query_sketch_mags(self.sw_url, input_upas, n_max_results, self.auth_token)
        query_results = query_sketch_mags(self.sw_url, input_upas, n_max_results, self.auth_token)

        output = generate_report(self.ws_url, self.callback_url, self.shared_folder,\
                                  params.get('workspace_name'), query_results)

        #END run_mags_mash

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_mags_mash return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
