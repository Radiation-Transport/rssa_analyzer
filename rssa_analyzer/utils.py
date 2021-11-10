import time
from typing import Callable


def measure_time(func: Callable):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print(time.time() - start_time)

    return wrapper
