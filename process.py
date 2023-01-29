import math
import subprocess
import time
from typing import List

import psutil

MB_SIZE = math.pow(1024, 2)


class Process:

    def __init__(self, cmd: List[str]):
        self.cmd = cmd
        self.t0 = time.time()
        self.t1 = None
        self.max_rss_memory = 0
        self.max_vms_memory = 0
        self.state = None
        self.process = None

    def exec(self):
        self.process = subprocess.Popen(self.cmd, shell=False)
        self.state = True

    def await_completion(self):

        if not self._check_state():
            return False

        self.t1 = time.time()

        try:

            pp = psutil.Process(self.process.pid)

            descendants = list(pp.children(recursive=True))
            descendants = descendants + [pp]
            rss_memory = 0
            vms_memory = 0

            for descendant in descendants:
                try:
                    mem_info = descendant.memory_info()
                    rss_memory += mem_info[0]
                    vms_memory += mem_info[1]
                except psutil.NoSuchProcess:
                    pass

            self.max_rss_memory = max(self.max_rss_memory, rss_memory)
            self.max_vms_memory = max(self.max_vms_memory, vms_memory)

        except psutil.NoSuchProcess:
            return self._check_state()

        return self._check_state()

    def is_running(self) -> bool:
        return psutil.pid_exists(self.process.pid) and self.process.poll() is None

    def get_statistics(self) -> dict:
        res = dict()
        res['command'] = ' '.join(self.cmd)
        res['start_time'] = self.t0
        res['finish_time'] = self.t1
        res['run_time_sec'] = (self.t1 - self.t0) if self.t1 else 0
        res['max_rss_memory_mb'] = self.max_rss_memory / MB_SIZE
        res['max_vms_memory_mb'] = self.max_vms_memory / MB_SIZE

        return res

    def _check_state(self):
        if not self.state:
            return False
        if self.is_running():
            return True

        self.state = False
        self.t1 = time.time()
        return False
