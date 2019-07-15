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
import test_grpc_eos.eos_pb2 as eos_pb2
import test_grpc_eos.eos_pb2_grpc as eos_pb2_grpc

from manila.share import driver
from manila.tests import fake_service_instance

LOG = log.getLogger(__name__)


class EOSDriver(driver.ShareDriver):
    """Fake EOS share driver.

    This fake EOS driver was meant to provide a means of learning how to interface with Manila
    The true driver is in driver.py which should be located in the same folder.

    This driver will allow a user to "create" and "delete" shares using the test server in the 
    "test_grpc_eos" folder. Use the Manila CLI or interface to play around with these actions.

    """

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
        request = eos_pb2.CreateShareRequest(name=share["name"], id=share["id"])
        self.grpc_client.CreateShare(request)
        LOG.debug(context)
        LOG.debug(share)
        
        #should return the location of where the share is located on the server
        return 'http://127.0.0.1/eos_shares/' + share["id"]

    def create_share_from_snapshot(self, context, share, snapshot,
                                   share_server=None):
        return ['/fake/path', '/fake/path2']

    def delete_share(self, context, share, share_server=None):
        request = eos_pb2.DeleteShareRequest(id=share["id"])
        self.grpc_client.DeleteShare(request)

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
