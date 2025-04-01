import jpype

class Engine:
    def __init__(self):
        utils = jpype.JPackage('server.engine')
        self.ShiftScheduler = utils.ShiftScheduler
        self.Employee = utils.Employee
        self.Shift = utils.Shift
        self.Holiday = utils.Holiday
        self.Config = utils.Config