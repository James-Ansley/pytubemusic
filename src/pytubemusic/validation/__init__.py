import json
import tomllib
from io import BytesIO
from pathlib import Path
from textwrap import indent
from typing import Any

from jsonschema.exceptions import ValidationError
from jsonschema.validators import RefResolver, validate as _validate

from pytubemusic.logutils import PanicOn

_SCHEMATA_ROOT = (Path(__file__) / ".." / "schemata").resolve()


def _get_schema(name: str):
    schema_path = _SCHEMATA_ROOT / f"{name}.schema.json"
    with open(schema_path, "r") as f:
        return json.load(f)


def _dump_validation_err(e: ValidationError):
    return f"Error for field `{e.json_path}`:\n{indent(e.message, '> ')}"


def loadf_or_panic(f: BytesIO, schema_name: str, msg: str):
    """
    Validates a heterogeneous string map of object data against the json
    schema for that object's type

    :raises jsonschema.exceptions.ValidationError: If the data does not
        satisfy the json schema
    """
    data = tomllib.load(f)
    with PanicOn(ValidationError, msg, handler=_dump_validation_err):
        validate(data, schema_name)
    return data


def validate(data: Any, schema_name: str):
    """
    :raises ValidationError: If the schema is not Valid
    """
    path = _SCHEMATA_ROOT / Path(schema_name).parent
    resolver = RefResolver(f"{path.as_uri()}/", {})
    _validate(data, _get_schema(schema_name), resolver=resolver)
