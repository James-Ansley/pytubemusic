from inspect import FrameInfo
from types import FunctionType

from approvaltests import StackFrameNamer
from approvaltests.pytest.pytest_config import PytestConfig


# Hack to get around approvaltest test discovery
# See: https://github.com/approvals/ApprovalTests.Python/issues/161
def _is_marked_with_test_dunder(maybe_function: FunctionType | None) -> bool:
    return (
          maybe_function is not None
          and hasattr(maybe_function, "__test__")
          and getattr(maybe_function, "__test__")
    )


def is_pytest_test(frame: FrameInfo) -> bool:
    method_name = frame[3]
    frame_globals = frame.frame.f_globals
    maybe_function = frame_globals.get(method_name)
    patterns = PytestConfig.test_naming_patterns
    return (
          StackFrameNamer._is_match_for_pytest(method_name, patterns)
          or StackFrameNamer._is_marked_with_test_dunder(maybe_function)
    )


StackFrameNamer._is_marked_with_test_dunder = _is_marked_with_test_dunder
StackFrameNamer.is_pytest_test = is_pytest_test


def test[T: FunctionType](f: T) -> T:
    setattr(f, "__test__", True)
    return f
