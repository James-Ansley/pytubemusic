from pipe_utils import curry


@curry
def kwarged(func, data):
    return func(**data)