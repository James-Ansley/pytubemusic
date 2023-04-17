import json
import tomllib
from io import BytesIO
from pathlib import Path
from textwrap import indent

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

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

    :param target_type: The type of object
    :param data: The heterogeneous string map of public object data

    :raises jsonschema.exceptions.ValidationError: If the data does not
        satisfy the json schema
    """
    data = tomllib.load(f)
    with PanicOn(ValidationError, msg, handler=_dump_validation_err):
        validate(data, _get_schema(schema_name))
    return data
