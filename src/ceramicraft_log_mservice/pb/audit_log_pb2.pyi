from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
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

class AuditLog(_message.Message):
    __slots__ = ("id", "actor_id", "role", "description", "created_at", "previous_hash", "current_hash")
    ID_FIELD_NUMBER: _ClassVar[int]
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_HASH_FIELD_NUMBER: _ClassVar[int]
    CURRENT_HASH_FIELD_NUMBER: _ClassVar[int]
    id: str
    actor_id: int
    role: Role
    description: str
    created_at: str
    previous_hash: str
    current_hash: str
    def __init__(self, id: _Optional[str] = ..., actor_id: _Optional[int] = ..., role: _Optional[_Union[Role, str]] = ..., description: _Optional[str] = ..., created_at: _Optional[str] = ..., previous_hash: _Optional[str] = ..., current_hash: _Optional[str] = ...) -> None: ...

class QueryAuditLogsRequest(_message.Message):
    __slots__ = ("actor_id", "role", "start_time", "end_time", "limit", "offset")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    role: Role
    start_time: str
    end_time: str
    limit: int
    offset: int
    def __init__(self, actor_id: _Optional[int] = ..., role: _Optional[_Union[Role, str]] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class QueryAuditLogsResponse(_message.Message):
    __slots__ = ("logs", "total_count")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[AuditLog]
    total_count: int
    def __init__(self, logs: _Optional[_Iterable[_Union[AuditLog, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...
