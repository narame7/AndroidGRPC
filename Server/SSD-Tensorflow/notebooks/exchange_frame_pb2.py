# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: exchange_frame.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='exchange_frame.proto',
  package='videostreamer',
  syntax='proto3',
  serialized_pb=_b('\n\x14\x65xchange_frame.proto\x12\rvideostreamer\"\x1b\n\nInputVideo\x12\r\n\x05\x66rame\x18\x01 \x01(\x0c\"\x1c\n\x0bOutputVideo\x12\r\n\x05\x66rame\x18\x01 \x01(\x0c\"\x1b\n\x0b\x42oundingBox\x12\x0c\n\x04info\x18\x01 \x01(\t2\xfe\x01\n\rVideoStreamer\x12G\n\x0cVideoProcess\x12\x19.videostreamer.InputVideo\x1a\x1a.videostreamer.OutputVideo\"\x00\x12L\n\x11VideoProcessFromC\x12\x19.videostreamer.InputVideo\x1a\x1a.videostreamer.OutputVideo\"\x00\x12V\n\x17VideoProcessFromAndroid\x12\x19.videostreamer.InputVideo\x1a\x1a.videostreamer.BoundingBox\"\x00(\x01\x30\x01\x42%\n\x15io.grpc.videostreamerB\x05VideoP\x01\xa2\x02\x02VSb\x06proto3')
)




_INPUTVIDEO = _descriptor.Descriptor(
  name='InputVideo',
  full_name='videostreamer.InputVideo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frame', full_name='videostreamer.InputVideo.frame', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=39,
  serialized_end=66,
)


_OUTPUTVIDEO = _descriptor.Descriptor(
  name='OutputVideo',
  full_name='videostreamer.OutputVideo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='frame', full_name='videostreamer.OutputVideo.frame', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=68,
  serialized_end=96,
)


_BOUNDINGBOX = _descriptor.Descriptor(
  name='BoundingBox',
  full_name='videostreamer.BoundingBox',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='info', full_name='videostreamer.BoundingBox.info', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=98,
  serialized_end=125,
)

DESCRIPTOR.message_types_by_name['InputVideo'] = _INPUTVIDEO
DESCRIPTOR.message_types_by_name['OutputVideo'] = _OUTPUTVIDEO
DESCRIPTOR.message_types_by_name['BoundingBox'] = _BOUNDINGBOX
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

InputVideo = _reflection.GeneratedProtocolMessageType('InputVideo', (_message.Message,), dict(
  DESCRIPTOR = _INPUTVIDEO,
  __module__ = 'exchange_frame_pb2'
  # @@protoc_insertion_point(class_scope:videostreamer.InputVideo)
  ))
_sym_db.RegisterMessage(InputVideo)

OutputVideo = _reflection.GeneratedProtocolMessageType('OutputVideo', (_message.Message,), dict(
  DESCRIPTOR = _OUTPUTVIDEO,
  __module__ = 'exchange_frame_pb2'
  # @@protoc_insertion_point(class_scope:videostreamer.OutputVideo)
  ))
_sym_db.RegisterMessage(OutputVideo)

BoundingBox = _reflection.GeneratedProtocolMessageType('BoundingBox', (_message.Message,), dict(
  DESCRIPTOR = _BOUNDINGBOX,
  __module__ = 'exchange_frame_pb2'
  # @@protoc_insertion_point(class_scope:videostreamer.BoundingBox)
  ))
_sym_db.RegisterMessage(BoundingBox)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\025io.grpc.videostreamerB\005VideoP\001\242\002\002VS'))

_VIDEOSTREAMER = _descriptor.ServiceDescriptor(
  name='VideoStreamer',
  full_name='videostreamer.VideoStreamer',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=128,
  serialized_end=382,
  methods=[
  _descriptor.MethodDescriptor(
    name='VideoProcess',
    full_name='videostreamer.VideoStreamer.VideoProcess',
    index=0,
    containing_service=None,
    input_type=_INPUTVIDEO,
    output_type=_OUTPUTVIDEO,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='VideoProcessFromC',
    full_name='videostreamer.VideoStreamer.VideoProcessFromC',
    index=1,
    containing_service=None,
    input_type=_INPUTVIDEO,
    output_type=_OUTPUTVIDEO,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='VideoProcessFromAndroid',
    full_name='videostreamer.VideoStreamer.VideoProcessFromAndroid',
    index=2,
    containing_service=None,
    input_type=_INPUTVIDEO,
    output_type=_BOUNDINGBOX,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_VIDEOSTREAMER)

DESCRIPTOR.services_by_name['VideoStreamer'] = _VIDEOSTREAMER

# @@protoc_insertion_point(module_scope)