#    Copyright 2012 OpenStack Foundation
#    Copyright 2014 Mirantis Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_log import log
import six
import json

import grpc
import test_eos_grpc.eos_pb2 as eos_pb2
import test_eos_grpc.eos_pb2_grpc as eos_pb2_grpc

from manila.share import driver
from manila.tests import fake_service_instance

LOG = log.getLogger(__name__)


class EOSDriver(driver.ShareDriver):
    """Fake share driver.
    This fake driver can be also used as a test driver within a real
    running manila-share instance. To activate it use this in manila.conf::
        enabled_share_backends = fake
        [fake]
        driver_handles_share_servers = True
        share_backend_name = fake
        share_driver = manila.tests.fake_driver.FakeShareDriver
    With it you basically mocked all backend driver calls but e.g. networking
    will still be activated.
    """

    '''
        The best place to initialize connection to the real EOS server
    '''
    def __init__(self, *args, **kwargs):
        #self._setup_service_instance_manager()
        super(EOSDriver, self).__init__(False, *args, **kwargs)
        self.backend_name = self.configuration.safe_get('share_backend_name') or 'EOS'
        channel = grpc.insecure_channel('localhost:50051')
        self.grpc_client = eos_pb2_grpc.EOSStub(channel)
    
    '''
    def manage_existing(self, share, driver_options, share_server=None):
        LOG.debug("Fake share driver: manage")
        LOG.debug("Fake share driver: driver options: %s",
                  six.text_type(driver_options))
        return {'size': 1}
    '''

    def unmanage(self, share, share_server=None):
        LOG.debug("Fake share driver: unmanage")

    def create_snapshot(self, context, snapshot, share_server=None):
        pass

    def delete_snapshot(self, context, snapshot, share_server=None):
        pass

    def create_share(self, context, share, share_server=None):
        
        request = eos_pb2.CreateShareRequest(name='hellowrld')
        self.grpc_client.CreateShare(request)
        
        return 1

    def create_share_from_snapshot(self, context, share, snapshot,
                                   share_server=None):
        return ['/fake/path', '/fake/path2']

    def delete_share(self, context, share, share_server=None):
        pass

    def ensure_share(self, context, share, share_server=None):
        pass

    def allow_access(self, context, share, access, share_server=None):
        pass

    def deny_access(self, context, share, access, share_server=None):
        pass

    def do_setup(self, context):
        pass

    def setup_server(self, *args, **kwargs):
        pass

    def teardown_server(self, *args, **kwargs):
        pass

    def create_share_group(self, context, group_id, share_server=None):
        pass

    def delete_share_group(self, context, group_id, share_server=None):
        pass

    def _update_share_stats(self):
        data = dict(
            storage_protocol='NFS',
            vendor_name='EOS/CERN',
            share_backend_name='EOS',
            driver_version='1.0',
            total_capacity_gb=500,
            free_capacity_gb=100,
            reserved_percentage=5)
        super(EOSDriver, self)._update_share_stats(data)
