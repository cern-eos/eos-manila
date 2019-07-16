import grpc
from concurrent import futures
import time
import os

# import the generated classes
import eos_pb2
import eos_pb2_grpc

import eos

shares = {}

# create a class to define the server functions
class EOSServicer(eos_pb2_grpc.EOSServicer):

    def CreateShare(self, request, context):
        response = eos_pb2.Response()
        
        share_location = eos.create_share(request)
        
        if not os.path.isdir(share_location):
           response.msg = "error"
           response.response_code = -1
        else:
           response.msg = "success"
           response.response_code = 1
        
        eos.report(action='added', response=response)

        return response

    def DeleteShare(self, request, context):
        response = eos_pb2.Response()

        success = eos.delete_share(request)

        #if success:
        
        response.msg = "success"
        response.response_code = 1
        
        #else:
        #response.msg = "error"
        #response.response_code = -1

        
        eos.report(action='removed', response=response)

        return response

    def ExtendShare(self, request, context):
        response = eos_pb2.Response()
        eos.change_share_size(request)
        return response        

    def ShrinkShare(self, request, context):
        response = eos_pb2.Response()
        eos.change_share_size(request)
        return response

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
