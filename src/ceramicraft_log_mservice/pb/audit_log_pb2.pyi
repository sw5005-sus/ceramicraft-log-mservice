from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RecordAuditLogRequest(_message.Message):
    __slots__ = ("service", "actor_id", "role", "description", "occurred_at")
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    service: str
    actor_id: int
    role: str
    description: str
    occurred_at: str
    def __init__(self, service: _Optional[str] = ..., actor_id: _Optional[int] = ..., role: _Optional[str] = ..., description: _Optional[str] = ..., occurred_at: _Optional[str] = ...) -> None: ...

class RecordAuditLogResponse(_message.Message):
    __slots__ = ("success", "event_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    event_id: str
    def __init__(self, success: _Optional[bool] = ..., event_id: _Optional[str] = ...) -> None: ...

class AuditLog(_message.Message):
    __slots__ = ("id", "service", "actor_id", "role", "description", "occurred_at", "created_at", "previous_hash", "current_hash")
    ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_HASH_FIELD_NUMBER: _ClassVar[int]
    CURRENT_HASH_FIELD_NUMBER: _ClassVar[int]
    id: str
    service: str
    actor_id: int
    role: str
    description: str
    occurred_at: str
    created_at: str
    previous_hash: str
    current_hash: str
    def __init__(self, id: _Optional[str] = ..., service: _Optional[str] = ..., actor_id: _Optional[int] = ..., role: _Optional[str] = ..., description: _Optional[str] = ..., occurred_at: _Optional[str] = ..., created_at: _Optional[str] = ..., previous_hash: _Optional[str] = ..., current_hash: _Optional[str] = ...) -> None: ...

class QueryAuditLogsRequest(_message.Message):
    __slots__ = ("actor_id", "service", "role", "start_time", "end_time", "occurred_at_start", "occurred_at_end", "limit", "offset")
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_START_FIELD_NUMBER: _ClassVar[int]
    OCCURRED_AT_END_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    service: str
    role: str
    start_time: str
    end_time: str
    occurred_at_start: str
    occurred_at_end: str
    limit: int
    offset: int
    def __init__(self, actor_id: _Optional[int] = ..., service: _Optional[str] = ..., role: _Optional[str] = ..., start_time: _Optional[str] = ..., end_time: _Optional[str] = ..., occurred_at_start: _Optional[str] = ..., occurred_at_end: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class QueryAuditLogsResponse(_message.Message):
    __slots__ = ("logs", "total_count")
    LOGS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[AuditLog]
    total_count: int
    def __init__(self, logs: _Optional[_Iterable[_Union[AuditLog, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class VerifyAuditLogChainRequest(_message.Message):
    __slots__ = ("start_time", "end_time")
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    start_time: str
    end_time: str
    def __init__(self, start_time: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class VerifyAuditLogChainResponse(_message.Message):
    __slots__ = ("is_valid", "failed_log_id", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    FAILED_LOG_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    failed_log_id: str
    message: str
    def __init__(self, is_valid: _Optional[bool] = ..., failed_log_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
