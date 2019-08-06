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
class EosServicer(eos_pb2_grpc.EosServicer):
   
    ''' HELPER FUNCTIONS '''

    def validate_auth(self, key=None):
        return AUTH_KEY == "BakTIcB08XwQ7vNvagi8"

    def generate_response(self, message=None, code=None, total_used=None, total_capacity=None, new_share_quota=None, new_share_path=None):
        response = eos_pb2.ManilaResponse()
        response.msg = message
        response.code = code
        
        if total_capacity is not None:
            response.total_used = total_used
            response.total_capacity = total_capacity
        
        if new_share_quota is not None:
            response.new_share_quota = new_share_quota
        
        if new_share_path is not None:
            response.new_share_path = new_share_path
        
        return response
   
    ''' ----------------- '''

    def CreateShare(self, request, context):       
        share_location = eos.create_share(request)
        
        if not os.path.isdir(share_location):
           response = self.generate_response(message="Could not create share", code=-1)
        else:
           response = self.generate_response(message="Share successfully created", code=1, new_share_path=share_location)
        
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
        try:
            eos.change_share_size(request)
            response = self.generate_response(message="Share extension successful", code=1)
        except ValueError:
            self.generate_response(message="Share extension unsuccessful", code=-1)

        eos.report(action='extended', response=response)
        return response

    def ShrinkShare(self, request, context):
        try:
            eos.change_share_size(request)
            response = self.generate_response(message="Share shrinkage successful", code=1)
        except:
             response =  self.generate_response(message="Share shrinkage unsuccessful", code=-1)

        eos.report(action="shrunk", response=response)
        return response

    def ManageExisting(self, request, context):
        quota = eos.manage_existing(request)
        
        if int(size) < 0:
           response = self.generate_response(message="Could not manage share", code=-1)
        else:
           response = self.generate_response(message="Successfully managed share", code=1, new_share_size=quota)

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

    def GetCapacities(self, request, context):
        try:
            response = self.generate_response(message="Capacities retrieved", code=1, total_used=eos.get_used_capacity(), total_capacity=eos.get_total_capacity())
        except:
            response =  self.generate_response(message="Unable to retrieve capacities", code=-1)

        eos.report(action="retrived capacities", response=response)
        return response

    ''' FUNCTION ROUTING '''

    switcher = {
        0: CreateShare,
        1: DeleteShare,
        2: ExtendShare,
        3: ShrinkShare,
        4: ManageExisting,
        5: Unmanage,
        6: GetCapacities
    }

    def ManilaServerRequest(self, request, context):
        print(request)

        #check the auth key & check the protocol type
        if request.protocol == EOS_PROTOCOL and self.validate_auth(key=request.auth_key):

            '''
            "self.switcher.get" uses the request_type/enum to check the
            corresponding method with the switcher object above (Python does not have switch statements)
            '''
            func = self.switcher.get(request.request_type, lambda: "Function does not exist.")
            return func(self, request=request, context=context) #runs the function
        else:
           #invalid request -- reject
           return self.generate_response(message="Bad Request: Permission Denied", code=-1)

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_EOSServicer_to_server`
# to add the defined class to the server
eos_pb2_grpc.add_EosServicer_to_server(
        EosServicer(), server)

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
