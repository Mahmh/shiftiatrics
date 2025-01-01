import jpype

class Engine:
    def __init__(self):
        utils = jpype.JPackage('server.engine')
        self.Shift = utils.Shift
        self.Employee = utils.Employee
        self.ShiftScheduler = utils.ShiftScheduler