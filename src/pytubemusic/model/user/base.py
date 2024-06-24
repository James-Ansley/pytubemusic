from pprint import PrettyPrinter

from pydantic import BaseModel, ConfigDict

__all__ = ("Model",)


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )


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
