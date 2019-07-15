import grpc
from concurrent import futures
import time

# import the generated classes
import eos_pb2
import eos_pb2_grpc

#import grpc logic
import eos

#shares = []
shares = {}

# create a class to define the server functions
class EOSServicer(eos_pb2_grpc.EOSServicer):

    def CreateShare(self, request, context):
        response = eos_pb2.Response()
        
        new_share = eos.create_share(request)
        #shares.append(new_share) 
        
        if new_share["id"] in shares: #don't want to overwrite any existing shares
           response.msg = "error"
           response.response_code = -1
        else:
           shares[new_share["id"]] = new_share
           response.msg = "success"
           response.response_code = 1

        #print("Share (" + new_share["id"]  + ") added with " +  response.msg + ". Code: " + str(response.response_code))
        #print("\n~ Available Shares [TOTAL: " + str(len(shares)) + " Shares] ~")
        #print(shares)
        #print("\n") 
        
        eos.report(action='added', id=new_share["id"], response=response, shares=shares)

        return response

    def DeleteShare(self, request, context):
        response = eos_pb2.Response()

        if request.id in shares:
           del shares[request.id]
           response.msg = "success"
           response.response_code = 1
        else:
           response.msg = "error"
           response.response_code = -1

        #print("Share (" + new_share["id"]  + ") removed with " +  response.msg + ". Code: " + str(response.response_code))
        eos.report(action='removed', id=request.id, response=response, shares=shares)

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
