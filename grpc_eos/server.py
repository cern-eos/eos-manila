import grpc
from concurrent import futures
import time
import os

# import the generated classes
import eos_pb2
import eos_pb2_grpc

import eos

EOS_PROTOCOL = "EOS"
AUTH_KEY = "BakTIcB08XwQ7vNvagi8"

# create a class to define the server functions
class EOSServicer(eos_pb2_grpc.EOSServicer):
   
    ''' HELPER FUNCTIONS '''

    def validate_auth(self, key=None):
        return AUTH_KEY == "BakTIcB08XwQ7vNvagi8"

    def generate_response(self, message=None, code=None):
        response = eos_pb2.Response()
        response.msg = message
        response.code = code
        return response
   
    ''' ----------------- '''

    def CreateShare(self, request, context):       
        share_location = eos.create_share(request)
        
        if not os.path.isdir(share_location):
           response = self.generate_response(message="Could not create share", code=-1)
        else:
           response = self.generate_response(message=share_location, code=1)
        
        eos.report(action='added', response=response)
        return response

    def DeleteShare(self, request, context):
        old_share_location = eos.delete_share(request)
        
        if os.path.isdir(old_share_location):
           response = self.generate_response(message="Could not delete share", code=-1)
        else:
           response = self.generate_response(message="Share successfully deleted", code=1)

        eos.report(action='deleted', response=response)
        return response

    def ExtendShare(self, request, context):
        eos.change_share_size(request)
        return self.generate_response(message="Share extension successful", code=1)

    def ShrinkShare(self, request, context):
        eos.change_share_size(request)
        return self.generate_response(message="Share shrinkage successful", code=1)

    def ManageExisting(self, request, context):
        size = eos.manage_existing(request)
        
        if int(size) < 0:
           response = self.generate_response(message="Could not manage share", code=-1)
        else:
           response = self.generate_response(message=size, code=1)

        eos.report(action='managed', response=response)
        return response

    def Unmanage(self, request, context):
        try:
            eos.unmanage(request)
            response = self.generate_response(message="Successfully unmanaged share", code=1)
        except ValueError:
            response = self.generate_response(message="Could not unmanage share", code=-1)

        eos.report(action="unmanaged", response=response)
        return response

    def GetUsedCapacity(self, request, context):
        return self.generate_response(message=eos.get_used_capacity(), code=1)

    def GetTotalCapacity(self, request, context):
        return self.generate_response(message="50", code=1) #arbitrary total capacity

    ''' FUNCTION ROUTING '''

    switcher = {
        "create_share": CreateShare,
        "delete_share": DeleteShare,
        "extend_share": ExtendShare,
        "shrink_share": ShrinkShare,
        "manage_existing": ManageExisting,
        "unmanage": Unmanage,
        "get_used_capacity": GetUsedCapacity,
        "get_total_capacity": GetTotalCapacity
    }

    def ServerRequest(self, request, context):
        print(request)

        #check the auth key & check the protocol type
        if request.protocol == EOS_PROTOCOL and self.validate_auth(key=request.auth_key):
            #route the request to the correct method/function
            func = self.switcher.get(request.request_type, lambda: "Function does not exist.")
            return func(self, request=request, context=context)
        else:
           #invalid request -- reject
           return self.generate_response(message="Bad Request: Permission Denied", code=-1)

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_EOSServicer_to_server`
# to add the defined class to the server
eos_pb2_grpc.add_EOSServicer_to_server(
        EOSServicer(), server)

# listen on port 50051
print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
