from datetime import timedelta
from pathlib import PurePath
from pprint import PrettyPrinter

from pydantic import BaseModel, Extra

__all__ = (
    "MaybeInt",
    "MaybeFloat",
    "MaybeStr",
    "MaybePath",
    "MaybeTimedelta",
    "Model",
)

type MaybeInt = int | None
type MaybeFloat = float | None
type MaybeStr = str | None
type MaybePath = PurePath | None
type MaybeTimedelta = timedelta | None


class Model(BaseModel):
    class Config:
        extra = Extra.forbid


# noinspection PyUnresolvedReferences,PyProtectedMember
class _ModelPrinter(PrettyPrinter):
    def _pprint_model(self, obj, stream, indent, *args):
        stream.write(f"{type(obj).__name__}(")
        indent += len(type(obj).__name__) + 1
        non_nulls = {k: v for k, v in obj.__dict__.items() if v is not None}
        items = iter(non_nulls.items())
        k, v = next(items)
        stream.write(f"{k}=")
        self._format(v, stream, indent + len(k) + 1, *args)
        for k, v in items:
            stream.write(f"\n{' ' * indent}{k}=")
            self._format(v, stream, indent + len(k) + 1, *args)
        stream.write(f")")

    PrettyPrinter._dispatch[Model.__repr__] = _pprint_model
