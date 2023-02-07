from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Dado(_message.Message):
    __slots__ = ["data", "id", "localizacao", "nomeDispositivo", "tipoDispositivo", "valor"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LOCALIZACAO_FIELD_NUMBER: _ClassVar[int]
    NOMEDISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    TIPODISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    VALOR_FIELD_NUMBER: _ClassVar[int]
    data: str
    id: int
    localizacao: str
    nomeDispositivo: str
    tipoDispositivo: int
    valor: float
    def __init__(self, id: _Optional[int] = ..., data: _Optional[str] = ..., localizacao: _Optional[str] = ..., nomeDispositivo: _Optional[str] = ..., tipoDispositivo: _Optional[int] = ..., valor: _Optional[float] = ...) -> None: ...

class Dispositivo(_message.Message):
    __slots__ = ["localizacao", "nomeDispositivo", "tipoDispositivo"]
    LOCALIZACAO_FIELD_NUMBER: _ClassVar[int]
    NOMEDISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    TIPODISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    localizacao: str
    nomeDispositivo: str
    tipoDispositivo: int
    def __init__(self, nomeDispositivo: _Optional[str] = ..., localizacao: _Optional[str] = ..., tipoDispositivo: _Optional[int] = ...) -> None: ...

class EmptyMessage(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class LedStatus(_message.Message):
    __slots__ = ["estado", "localizacao", "nomeDispositivo"]
    ESTADO_FIELD_NUMBER: _ClassVar[int]
    LOCALIZACAO_FIELD_NUMBER: _ClassVar[int]
    NOMEDISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    estado: int
    localizacao: str
    nomeDispositivo: str
    def __init__(self, estado: _Optional[int] = ..., nomeDispositivo: _Optional[str] = ..., localizacao: _Optional[str] = ...) -> None: ...

class ListaDados(_message.Message):
    __slots__ = ["dados"]
    DADOS_FIELD_NUMBER: _ClassVar[int]
    dados: _containers.RepeatedCompositeFieldContainer[Dado]
    def __init__(self, dados: _Optional[_Iterable[_Union[Dado, _Mapping]]] = ...) -> None: ...

class ListaDispositivos(_message.Message):
    __slots__ = ["dispositivos"]
    DISPOSITIVOS_FIELD_NUMBER: _ClassVar[int]
    dispositivos: _containers.RepeatedCompositeFieldContainer[Dispositivo]
    def __init__(self, dispositivos: _Optional[_Iterable[_Union[Dispositivo, _Mapping]]] = ...) -> None: ...

class ListaLedStatus(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _containers.RepeatedCompositeFieldContainer[LedStatus]
    def __init__(self, status: _Optional[_Iterable[_Union[LedStatus, _Mapping]]] = ...) -> None: ...

class Parametros(_message.Message):
    __slots__ = ["data", "localizacao", "nomeDispositivo"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    LOCALIZACAO_FIELD_NUMBER: _ClassVar[int]
    NOMEDISPOSITIVO_FIELD_NUMBER: _ClassVar[int]
    data: str
    localizacao: str
    nomeDispositivo: str
    def __init__(self, localizacao: _Optional[str] = ..., data: _Optional[str] = ..., nomeDispositivo: _Optional[str] = ...) -> None: ...
