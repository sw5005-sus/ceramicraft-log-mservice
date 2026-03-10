from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    MERCHANT: _ClassVar[Role]
    CUSTOMER: _ClassVar[Role]
    SYSTEM: _ClassVar[Role]
ROLE_UNSPECIFIED: Role
MERCHANT: Role
CUSTOMER: Role
SYSTEM: Role

class RecordAuditLogRequest(_message.Message):
    __slots__ = ("actor_id", "role", "description")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    role: Role
    description: str
    def __init__(self, actor_id: _Optional[int] = ..., role: _Optional[_Union[Role, str]] = ..., description: _Optional[str] = ...) -> None: ...

class RecordAuditLogResponse(_message.Message):
    __slots__ = ("success", "event_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    event_id: str
    def __init__(self, success: bool = ..., event_id: _Optional[str] = ...) -> None: ...
