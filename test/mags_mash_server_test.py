# -*- coding: utf-8 -*-
import os
import time
import unittest
import subprocess
from configparser import ConfigParser

from mags_mash.mags_mashImpl import mags_mash
from mags_mash.mags_mashServer import MethodContext
from mags_mash.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.AssemblyUtilClient import AssemblyUtil

class mags_mashTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('mags_mash'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'mags_mash',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = mags_mash(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_mags_mash_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def upload_data_and_get_refs(self, ws_name):
        files = os.listdir('data/')
        files = [f for f in files if '.fa' in f]
        refs = []
        au = AssemblyUtil(self.__class__.callback_url)
        for f in files:
            new_path = os.path.join(self.__class__.scratch,f)
            path = os.path.join(os.path.join(os.getcwd(),'data'),f)
            args = ['cp',path, new_path]
            subprocess.check_output(args)
            self.assertTrue(os.path.exists(new_path))
            print('curr file',f)
            ref = au.save_assembly_from_fasta(
                {
                    "file":{
                        "path":new_path,
                        "assembly_name":f.split('.fa')[0]
                    },
                    "assembly_name": f.split('.fa')[0] + "_mags_mash_test",
                    "workspace_name": ws_name,
                    "min_contig_length":100,
                    "type": "metagenome"
                }
            )
            refs.append(ref)
        return refs

    def get_genome_set(self):
        return "22385/60/1"

    def validate_report_is_populated(self, ret):
        self.assertTrue('report_ref' in ret)


    def iteration_of(self, ref, ws_name):
        ret = self.getImpl().run_mags_mash(self.getContext(), {'workspace_name': ws_name,
                                                                'ws_ref': ref,
                                                                'n_max_results':10})
        self.validate_report_is_populated(ret)

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        '''
        simple test to see if the 5 files run.
        '''
        ws_name = self.getWsName()

        gs_ref = self.get_genome_set()
        self.iteration_of(gs_ref, ws_name)

        refs = self.upload_data_and_get_refs(ws_name)
        for ref in refs:
            self.iteration_of(ref, ws_name)


