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

from oslo_config import cfg
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

eos_opts = [
    cfg.HostAddressOpt('hitachi_hsp_host',
                       required=True,
                       help="HSP management host for communication between "
                            "Manila controller and HSP."),
    cfg.StrOpt('hitachi_hsp_username',
               required=True,
               help="HSP username to perform tasks such as create filesystems"
                    " and shares."),
    cfg.StrOpt('hitachi_hsp_password',
               required=True,
               secret=True,
               help="HSP password for the username provided."),
]

CONF = cfg.CONF
CONF.register_opts(eos_opts)   

class EOSDriver(driver.ShareDriver):

    def __init__(self, *args, **kwargs):
        super(EOSDriver, self).__init__(False, *args, **kwargs)
 
        self.backend_name = self.configuration.safe_get('share_backend_name') or 'EOS'
        self.configuration.append_config_values(eos_opts)

        channel = grpc.insecure_channel('localhost:50051')
        self.grpc_client = eos_pb2_grpc.EOSStub(channel) 

    def request(self, request_type, share=None, context=None):         
        auth_key = "dsfdf"
        protocol = "EOS"

        if not share:
            request_proto = eos_pb2.Request(request_type=request_type, auth_key=auth_key, protocol=protocol)
        else:
            request_proto = eos_pb2.Request(request_type=request_type, auth_key=auth_key, protocol=protocol, share_name=share["display_name"], description=share["display_description"], share_id=share["id"], share_group_id=share["share_group_id"], quota=share["size"], creator=share["user_id"], egroup=share["project_id"], admin_egroup="")
        
        response = self.grpc_client.ServerRequest(request_proto)

        return response

    def unmanage(self, share, share_server=None):
        LOG.debug("Fake share driver: unmanage")

    def create_share(self, context, share, share_server=None):
        response = self.request(request_type="create_share", share=share, context=context)
        if response.code < 0:
           return None

        #should return the location of where the share is located on the server
        return response.msg #'~/eos_shares/' + share["user_id"] + "/" + share["display_name"]

    def create_share_from_snapshot(self, context, share, snapshot,
                                   share_server=None):
        return ['/fake/path', '/fake/path2']

    def delete_share(self, context, share, share_server=None):
        user = context.to_dict()["user_id"]
        #request = eos_pb2.DeleteShareRequest(id=share["id"], creator=user)
        #response = self.grpc_client.DeleteShare(request)

        response = self.request(request_type="delete_share", share=share, context=context)


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
        try:
            response = self.request(request_type="get_used_capacity")
            used = int(response.msg)

            response = self.request(request_type="get_total_capacity")
            total = int(response.msg)

            free = total-used
        except ValueError:
            return None
      
        return free, total
        
    def _update_share_stats(self):
        free, total = self.get_capacities()

        data = dict(
            storage_protocol='NFS',
            vendor_name='CERN',
            share_backend_name='EOS',
            driver_version='1.0',
            total_capacity_gb=total,
            free_capacity_gb= free,
            reserved_percentage=5)

        super(EOSDriver, self)._update_share_stats(data)
