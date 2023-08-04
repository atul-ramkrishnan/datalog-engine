import time

class Timer:
    def __init__(self, label="Time taken"):
        self.label = label

    def __enter__(self):
        self.start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        end_time = time.perf_counter()
        elapsed_time = end_time - self.start_time
        print(f"{self.label}: {elapsed_time:.6f} seconds")
