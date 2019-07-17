import grpc
from concurrent import futures
import time
import os

# import the generated classes
import eos_pb2
import eos_pb2_grpc

import eos

EOS_PROTOCOL = "EOS"

# create a class to define the server functions
class EOSServicer(eos_pb2_grpc.EOSServicer):
   
    def validate_auth(self, key=None):
        return True

    def generate_response(self, message=None, code=None):
        response = eos_pb2.Response()
        response.msg = message
        response.code = code
        return response

    def CreateShare(self, request, context):       
        share_location = eos.create_share(request)
        
        if not os.path.isdir(share_location):
           response = self.generate_response(message="Could not create share", code=-1)
        else:
           response = self.generate_response(message="Share successfully created", code=1)
        
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
        return self.generate_response()

    def ShrinkShare(self, request, context):
        eos.change_share_size(request)
        return self.generate_response()

    switcher = {
        "create_share": CreateShare,
        "delete_share": DeleteShare,
        "extend_share": ExtendShare,
        "shrink_share": ShrinkShare
    }

    def ServerRequest(self, request, context):
        #check the auth key & check the protocol type
        if request.protocol == EOS_PROTOCOL and self.validate_auth(key=request.auth_key):
            #route the request to the correct method/function
            func = self.switcher.get(request.request_type, lambda: "Function does not exist.")
            return func(self, request=request, context=context)
        else:
           #invalid request -- reject
           return generate_response(message="Bad Request: Permission Denied", code=-1)

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
