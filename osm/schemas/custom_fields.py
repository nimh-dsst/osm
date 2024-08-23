from typing import Any, ClassVar, Generic, TypeVar, Union

import odmantic
from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema

T = TypeVar("T", str, bytes)


def _display(value: T) -> str:
    if isinstance(value, bytes):
        return b"..." if value else b""
    return f"{value[:10]}..." if value else ""


class LongField(Generic[T]):
    _inner_schema: ClassVar[CoreSchema]
    _error_kind: ClassVar[str]

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def serialize(
            value: "LongField[T]", info: core_schema.SerializationInfo
        ) -> Union[str, "LongField[T]"]:
            if info.mode == "json":
                return _display(value.get_value())
            else:
                return value

        def get_json_schema(
            _core_schema: CoreSchema, handler: GetCoreSchemaHandler
        ) -> JsonSchemaValue:
            json_schema = handler(cls._inner_schema)
            return json_schema

        json_schema = core_schema.no_info_after_validator_function(
            source,  # construct the type
            cls._inner_schema,
        )

        def get_schema(strict: bool) -> CoreSchema:
            return core_schema.json_or_python_schema(
                python_schema=core_schema.union_schema(
                    [
                        core_schema.is_instance_schema(source),
                        json_schema,
                    ],
                    custom_error_type=cls._error_kind,
                    strict=strict,
                ),
                json_schema=json_schema,
                serialization=core_schema.plain_serializer_function_ser_schema(
                    serialize,
                    info_arg=True,
                    return_schema=core_schema.str_schema(),
                    when_used="json",
                ),
            )

        return core_schema.lax_or_strict_schema(
            lax_schema=get_schema(strict=False),
            strict_schema=get_schema(strict=True),
        )

    def __init__(self, value: T):
        self._value = value

    def get_value(self) -> T:
        return self._value

    def __repr__(self) -> str:
        return '""'  # Always return an empty string representation

    def __str__(self) -> str:
        return _display(self._value)


class LongStr(LongField[str]):
    """A string that displays '...' instead of the full content in logs or tracebacks."""

    _inner_schema: ClassVar[CoreSchema] = core_schema.str_schema()
    _error_kind: ClassVar[str] = "string_type"


class LongBytes(LongField[bytes]):
    """A bytes type that displays '...' instead of the full content in logs or tracebacks."""

    _inner_schema: ClassVar[CoreSchema] = core_schema.bytes_schema()
    _error_kind: ClassVar[str] = "bytes_type"


class FilePlaceholder(odmantic.EmbeddedModel):
    content: LongBytes = odmantic.Field(
        default=b"", json_schema_extra={"exclude": True}
    )
