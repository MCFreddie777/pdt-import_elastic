import time


class Retrying:

    def __init__(self, max_retries=20, multiplier=1.1):
        self.max_retries = max_retries
        self.multiplier = multiplier

    def start(self, fn, condition_fn, waiting_time=5.0, retries=1):
        result = fn()

        if condition_fn(result):
            return True, result

        # if condition wasn't fulfilled, retry the function
        if retries <= self.max_retries:
            print(f"Retrying #{retries}: {result}")
            time.sleep(waiting_time)
            return self.start(fn, condition_fn, waiting_time=waiting_time * self.multiplier, retries=retries + 1)

        # return false and result if condition was not fulfilled even after maximum number of tries
        return False, result
