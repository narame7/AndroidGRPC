# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import test_pb2 as test__pb2


class ImageCaptionServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.DataStreaming = channel.stream_stream(
        '/imageCaptioning.ImageCaptionService/DataStreaming',
        request_serializer=test__pb2.Request.SerializeToString,
        response_deserializer=test__pb2.Response.FromString,
        )


class ImageCaptionServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def DataStreaming(self, request_iterator, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ImageCaptionServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'DataStreaming': grpc.stream_stream_rpc_method_handler(
          servicer.DataStreaming,
          request_deserializer=test__pb2.Request.FromString,
          response_serializer=test__pb2.Response.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'imageCaptioning.ImageCaptionService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
