import grpc

import eos_pb2
import eos_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
grpc_client = eos_pb2_grpc.EOSStub(channel)

new_share = eos_pb2.CreateShareRequest(name="Lissy")
hello = grpc_client.CreateShare(new_share)

print(hello)
