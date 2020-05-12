import unittest
from unittest.mock import patch, MagicMock
from conduit.utils import job_definitions
import base64
from tarfile import TarFile
import tempfile
import contextlib
import docker
from conduit.tests.testing_utils import config, test_auth_data, resolve_filename

@patch('conduit.utils.job_definitions.boto3.client',**config)
class TestJobDefinitions(unittest.TestCase):
    # TODO need to make job definitions into a class in order to test properly
    def setUp(self):
        
        
        pass
        
        
    
    def test_docker_auth(self,boto3mock):
        
        
        ret = job_definitions.docker_auth()
        print(ret)
        assert(ret == test_auth_data)
    def test_docker_registry_login(self,boto3mock):
        docker_patch = patch('conduit.utils.job_definitions.docker')
        with docker_patch as p:
            p.from_env.return_value.login.return_value = {'Status':'test_resposne'}
            ret = job_definitions.docker_login()
            p.from_env.return_value.login.assert_called_with(username='test_username', password='test_password',registry='test_proxy_endpoint', reauth=True)
            
    @unittest.expectedFailure
    def test_failed_docker_registry_login(self,boto3mock): 
        docker_patch = patch('conduit.utils.job_definitions.docker')
        with docker_patch as p:
            ret = job_definitions.docker_login()
            p.from_env.return_value.login.assert_called_with(username='test_username', password='test_password',registry='test_proxy_endpoint', reauth=True)
            
    def test_create_and_push_docker_image(self,boto3mock):
        docker_client_mock = MagicMock(spec=docker.DockerClient)
        docker_client_mock.images.build.return_value = (None, []) 
        docker_client_mock.images.push.return_value = []


        d_patch = patch('conduit.utils.job_definitions.docker.from_env', return_value=docker_client_mock)
        dl_patch = patch('conduit.utils.job_definitions.docker_login', return_value=docker_client_mock)
        odi_patch = patch('conduit.utils.job_definitions.get_original_docker_name', return_value='test_docker')
        tf = TarFile(mode='w', fileobj=tempfile.NamedTemporaryFile())
        mbc_patch = patch('conduit.utils.job_definitions.make_build_context', return_value=tf)

        mbc_patch.side_effect = tf
        patches = [d_patch, dl_patch, odi_patch, mbc_patch]
        with contextlib.ExitStack() as stack:
            
            managers = [stack.enter_context(patch) for patch in patches]

            tag = 'test_docker:local'
            job_definitions.create_and_push_docker_image({}, tag, local=True)

            docker_client_mock.images.build.assert_called_with(fileobj=tf, rm=True, pull=True, tag=tag, custom_context=True)
            docker_client_mock.images.push.assert_not_called()


            tag = 'test_docker:s3'
            job_definitions.create_and_push_docker_image({}, tag, local=False)
            docker_client_mock.images.build.assert_called_with(fileobj=tf, rm=True, pull=True, tag=tag, custom_context=True)
            docker_client_mock.images.push.assert_called_with(tag, stream=True, decode=True)
            
    def test_create_job_definition(self,boto3mock):
        pass
    def test_create_job_definitions(self,boto3mock):
        pass
    
    def test_docker_login(self,boto3mock):
        pass
    
    def test_extract(self,boto3mock):
        pass
    def test_generate_job_definition(self,boto3mock):
        pass
    def test_get_original_docker_name(self,boto3mock):
        # Test hints
        name = 'test_docker'
        tool_yml = {
            'hints' : {
                'DockerRequirement' : {
                    "dockerPull" : name
                }
            }
        }
        self.assertEqual(name, job_definitions.get_original_docker_name(tool_yml))
        # TODO : Will fail from here down
        name = 'test_docker'
        tool_yml = {
            'hints' : 
                [
                    {
                    "class" : 'DockerRequirement',
                    "dockerPull" : name
                    }
                
                ]
            
        }
        self.assertEqual(name, job_definitions.get_original_docker_name(tool_yml))
        # Test requirements
        tool_yml = {
            'requirements' : [
                {
                    "class" : 'DockerRequirement', 
                    "dockerPull" : name
                }
            ]
            
        }
        self.assertEqual(name, job_definitions.get_original_docker_name(tool_yml))
        # Test exception
        name = 'test_docker'
        tool_yml = {
            'hints' : {
                'DockerRequirement' : {
                    "dockerPull" : name
                }
            }
        }
        self.assertRaises(NotImplementedError, job_definitions.get_original_docker_name, tool_yml)
    def test_make_build_context(self,boto3mock):
        
        f = job_definitions.make_build_context('test_local_build_context', local=True)
        test_t = TarFile(fileobj=f)
        eval_t = TarFile(name=resolve_filename('local_docker_context.tar'))
        self.assertEqual(set(test_t.getnames()), set(eval_t.getnames()))

        f = job_definitions.make_build_context('test_s3_build_context', local=False)
        test_t = TarFile(fileobj=f)
        eval_t = TarFile(name=resolve_filename('s3_docker_context.tar'))
        self.assertEqual(set(test_t.getnames()), set(eval_t.getnames()))


    
    def test_make_tag(self,boto3mock):
        patch1 = patch('conduit.utils.job_definitions.get_original_docker_name', return_value='test_docker')
        dr_patch = patch('conduit.utils.job_definitions.docker_registry_login', return_value='test_registry')
        with patch1, dr_patch:
            self.assertEqual(job_definitions.make_tag('', {}, local=False), "test_registry/test_docker:s3")
            self.assertEqual(job_definitions.make_tag('', {}, local=True), "test_docker:local")
        
        # TODO fails
        patch1 = patch('conduit.utils.job_definitions.get_original_docker_name', return_value='test_registry1/test_docker:test_tag')
        with patch1, dr_patch:
            self.assertEqual(job_definitions.make_tag('', {}, local=False), "test_registry/test_docker:s3")
            self.assertEqual(job_definitions.make_tag('', {}, local=True), "test_docker:local")
        
        patch1 = patch('conduit.utils.job_definitions.get_original_docker_name', return_value='test_registry1/test_docker')
        with patch1, dr_patch:
            self.assertEqual(job_definitions.make_tag('', {}, local=False), "test_registry/test_docker:s3")
            self.assertEqual(job_definitions.make_tag('', {}, local=True), "test_docker:local")