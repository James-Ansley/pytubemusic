# PyTubeMusic Tests

Install the test requirements from `tests/requirements.txt`.

These tests
use [ApprovalTests](https://github.com/approvals/ApprovalTests.Python) and
[pytest](https://docs.pytest.org/en/7.4.x/) with the
[ApprovalTests pytest plugin](https://github.com/approvals/ApprovalTests.Python.PytestPlugin).
To enable diff checking on PyCharm, see
[their documentation](https://github.com/approvals/ApprovalTests.Python.PytestPlugin#tip-for-jetbrains-toolbox-and-pycharm-users)
which describes how to set up a run configuration which uses PyCharm's built-in
diff checker.

The working directory of the tests should be set to be the `tests/` directory.
Your pytest arguments should look something like:

```
--approvaltests-add-reporter-args='diff' \
--approvaltests-add-reporter='/Applications/PyCharm.app/Contents/MacOS/pycharm'
```
