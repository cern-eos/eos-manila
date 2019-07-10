import grpc
from concurrent import futures
import time

# import the generated classes
import eos_pb2
import eos_pb2_grpc

# import the original calculator.py
import eos

shares = []

# create a class to define the server functions, derived from
# calculator_pb2_grpc.CalculatorServicer
class EOSServicer(eos_pb2_grpc.EOSServicer):

    # calculator.square_root is exposed here
    # the request and response are of the data type
    # calculator_pb2.Number
    def CreateShare(self, request, context):
        response = eos_pb2.Response()
        
        new_share = eos.create_share(request.name)
        shares.append(new_share)

        response.msg = "success"
        response.response_code = 1
        print(shares)

        return '~/'


# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

# use the generated function `add_CalculatorServicer_to_server`
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
