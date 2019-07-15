import grpc

import eos_pb2
import eos_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
grpc_client = eos_pb2_grpc.EOSStub(channel)

new_share_request = eos_pb2.CreateShareRequest(name="Lissy")
response = grpc_client.CreateShare(new_share_request)


