import time

class Timer:
    def __init__(self):
        self.start = time.time()

    def reset(self):
        self.start = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start