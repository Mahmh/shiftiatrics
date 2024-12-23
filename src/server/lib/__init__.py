import jpype

from constants import (
    CURRENT_DIR,
    ENABLE_LOGGING
)

from logger import (
    log,
    err_log
)


class JavaUtils:
    def __init__(self):
        utils = jpype.JPackage('server.lib.engine')
        self.Employee = utils.Employee
        self.ShiftScheduler = utils.ShiftScheduler