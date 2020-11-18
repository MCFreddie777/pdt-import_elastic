from config.settings import DEBUG, LOG
from datetime import datetime


class Logging():
    def __init__(self, start_time):
        self.start_time = start_time

    def log(self, message):
        if DEBUG or LOG:
            print(f"[{datetime.now() - self.start_time}] {message}")
