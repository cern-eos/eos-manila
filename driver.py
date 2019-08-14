#    Copyright 2011 OpenStack Foundation
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
from manila import exception
from manila.share import api

import openstack

LOG = log.getLogger(__name__)

#eos_group = cfg.OptGroup(name='eos', title='Eos Options')
eos_opts = [
    cfg.StrOpt('eos_authentication_key',
               required=False,
               help="Authentication key to access EOS GRPC server.")
]

CONF = cfg.CONF
#CONF.register_group(eos_group)
CONF.register_opts(eos_opts)   
'''
conn = openstack.connect(auth_url='http://188.185.71.204/identity/v3',
                         username='admin',
                         password='nomoresecret',
                         project_name='admin',
                         project_domain_id='default',
                         user_domain_id='default')
'''
class EosDriver(driver.ExecuteMixin, driver.ShareDriver):

    def __init__(self, *args, **kwargs):
        super(EosDriver, self).__init__(False, *args, config_opts=[eos_opts] ,**kwargs)
        self.api = api.API() 

        self.backend_name = self.configuration.safe_get('share_backend_name') or 'EOS'
        self.configuration.append_config_values(eos_opts)

        channel = grpc.insecure_channel('ajp.cern.ch:50051')
        #channel = grpc.insecure_channel('localhost:50051')
        self.grpc_client = eos_pb2_grpc.EosStub(channel) 

        self.conn = openstack.connect(auth_url='http://188.185.71.204/identity/v3',
                         username='admin',
                         password='nomoresecret',
                         project_name='admin',
                         project_domain_id='default',
                         user_domain_id='default')

    def request(self, request_type, share=None, context=None, metadata={"share_host": None}, new_quota=None):         
        auth_key = self.configuration.eos_authentication_key

        if not share:
            protocol = "EOS"
            request_proto = eos_pb2.ManilaRequest(request_type=request_type, auth_key=auth_key, protocol=protocol)
        else:
            protocol = share["share_proto"]
            share_location = ""
            size = share["size"]

            if share["export_location"]:
               share_location = share["export_location"]    

            if new_quota is not None:
               size = new_quota        

            request_proto = eos_pb2.ManilaRequest(request_type=request_type, 
                                                  auth_key=auth_key, 
                                                  protocol=protocol, 
                                                  share_name=share["display_name"], 
                                                  description=share["display_description"], 
                                                  share_id=share["id"], 
                                                  share_group_id=share["share_group_id"], 
                                                  quota=size, 
                                                  creator=self.conn.identity.get_user(share['user_id']).name, 
                                                  egroup=share["project_id"], 
                                                  admin_egroup="", 
                                                  share_host=metadata["share_host"],
                                                  share_location=share_location)
        
        response = self.grpc_client.ManilaServerRequest(request_proto)
        return response

    def report(self, response):
        if (response.code < 0):
            raise exception.EOSException(msg=response.msg)

    def create_share(self, context, share, share_server=None):
        metadata = self.api.get_share_metadata(context, {'id': share['share_id']})

        #make sure there is a value for the share host before proceeding
        try:
           share_host = metadata["share_host"]
           response = self.request(request_type="CREATE_SHARE", share=share, context=context, metadata=metadata)
        except KeyError:
           response = eos_pb2.ManilaResponse()
           response.code = -1
           response.msg = "Invalid share host"
         
        self.report(response)

        #should return the location of where the share is located on the server
        return response.new_share_path

    def manage_existing(self, share, driver_options):
        # Calculate quota for managed dataset
        quota = driver_options.get("size")
        
        if quota:
            share["size"] = quota

        response = self.request(request_type="MANAGE_EXISTING", share=share)
        self.report(response)
 
        return {"size": response.new_share_quota, "export_locations": [{"path": share["export_location"]}]}

    def unmanage(self, share, share_server=None):
        response = self.request(request_type="UNMANAGE", share=share)
        self.report(response)

    def delete_share(self, context, share, share_server=None):
        user = context.to_dict()["user_id"]
        response = self.request(request_type="DELETE_SHARE", share=share, context=context)
        self.report(response)

    def extend_share(self, share, new_size, share_server=None):
        #share["size"] = new_size
        response = self.request(request_type="EXTEND_SHARE", share=share, new_quota=new_size)
        self.report(response)

    def shrink_share(self, share, new_size, share_server=None):
        #share["size"] = new_size
        response = self.request(request_type="SHRINK_SHARE", share=share, new_quota=new_size)
        self.report(response)
    
    def get_capacities(self):
        response=""

        try:
            response = self.request(request_type="GET_CAPACITIES")
            used = response.total_used 
            total = response.total_capacity

            free = total-used
        except ValueError:
            raise exception.EOSException(msg=response.msg)
      
        return free, total
        
    def _update_share_stats(self):
        free, total = self.get_capacities()

        data = dict(
            storage_protocol='EOS',
            vendor_name='CERN',
            share_backend_name='EOS',
            driver_version='1.0',
            total_capacity_gb=total,
            free_capacity_gb= free,
            reserved_percentage=5)

        super(EosDriver, self)._update_share_stats(data)
