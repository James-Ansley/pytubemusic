# PyTubeMusic

## Notes for developers

Installing this project as an editable project will only install the necessary
requirements to run the project. To install _all_ the requirements for
development, run something like the following:

```shell
find . -name "requirements.txt" | xargs -I {} pip install -r {}
```

To run the tests see `tests/README.md`.
