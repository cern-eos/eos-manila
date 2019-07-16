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
import os
import json

import grpc
import grpc_eos.eos_pb2 as eos_pb2
import grpc_eos.eos_pb2_grpc as eos_pb2_grpc

from manila.share import driver
from manila.tests import fake_service_instance

LOG = log.getLogger(__name__)

class RequestSwitcher(object):

    def gen_request(self, request_type, share=None, context=None):
        method_name = request_type
        method = getattr(self, method_name, "Request type does not exist.")
        
        self.share = share
        self.context = context

        return method()

    #def create_share(self):
        

class EOSDriver(driver.ShareDriver):

    def __init__(self, *args, **kwargs):
        super(EOSDriver, self).__init__(False, *args, **kwargs)
        
        self.backend_name = self.configuration.safe_get('share_backend_name') or 'EOS'
        
        channel = grpc.insecure_channel('localhost:50051')
        self.grpc_client = eos_pb2_grpc.EOSStub(channel)
        
        self.total_capacity = 50 

        # if the eos_shares path does not exist, create it so that get_capacities does not fail
        if not os.path.isdir(os.path.expanduser('~') + "/eos_shares/"):
           os.mkdir(os.path.expanduser('~') + "/eos_shares")

    '''
    def manage_existing(self, share, driver_options, share_server=None):
        LOG.debug("Fake share driver: manage")
        LOG.debug("Fake share driver: driver options: %s",
                  six.text_type(driver_options))
        return {'size': 1}
    '''

    def request(self, request_type, share=None, context=None):
        pass

    def unmanage(self, share, share_server=None):
        LOG.debug("Fake share driver: unmanage")

    def create_share(self, context, share, share_server=None):
        #LOG.debug(context.to_dict())
        user = context.to_dict()["user_id"] 
        request = eos_pb2.CreateShareRequest(creator=user, name=share["name"], id=share["id"], size=share["size"])
        response = self.grpc_client.CreateShare(request)
        
        #LOG.debug(context)
        #LOG.debug(share)
        
        if response.response_code < 0:
           return None
        #should return the location of where the share is located on the server
        return '~/eos_shares/' + user  + "/" + share["id"]

    def create_share_from_snapshot(self, context, share, snapshot,
                                   share_server=None):
        return ['/fake/path', '/fake/path2']

    def delete_share(self, context, share, share_server=None):
        user = context.to_dict()["user_id"]
        request = eos_pb2.DeleteShareRequest(id=share["id"], creator=user)
        response = self.grpc_client.DeleteShare(request)

        if response.response_code < 0:
           return False

    def extend_share(self, share, new_size, share_server=None):
        request = eos_pb2.ExtendShareRequest(creator=share["user_id"], id=share["id"], new_size=new_size)
        response = self.grpc_client.ExtendShare(request)

    def shrink_share(self, share, new_size, share_server=None):
        request = eos_pb2.ShrinkShareRequest(creator=share["user_id"], id=share["id"], new_size=new_size)
        response = self.grpc_client.ShrinkShare(request)

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
    
    def get_capacities(self):
        '''
        path = os.path.expanduser('~') + "/eos_shares"
        used = 0

        for filename in os.listdir(path):

            if filename.endswith(".txt"):
                f = open(filename)
                used = used + float(f.read())
                #LOG.debug(lines)
                continue
            else:
                continue
        '''

        path = os.path.expanduser('~') + "/eos_shares"
        used = 0
        #print(os.listdir(path))

        for root, directories, files in os.walk(path):

            for file in files:

                if file.endswith(".txt"):
                    f = open(os.path.join(root, file))
                    used = used + int(f.read())

                    continue
                else:
                    continue

        return used
        
    def _update_share_stats(self):
        used = self.get_capacities()
        
        free = self.total_capacity - used

        data = dict(
            storage_protocol='NFS',
            vendor_name='CERN',
            share_backend_name='EOS',
            driver_version='1.0',
            total_capacity_gb=self.total_capacity,
            free_capacity_gb= free,
            reserved_percentage=5)

        super(EOSDriver, self)._update_share_stats(data)
