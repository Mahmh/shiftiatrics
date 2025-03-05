from typing import Literal
from enum import Enum

WeekendDays = Literal['Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday']
Interval = Literal['Daily', 'Weekly', 'Monthly']

class IntervalEnum(Enum):
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'

class WeekendDaysEnum(Enum):
    SAT_SUN = 'Saturday & Sunday'
    FRI_SAT = 'Friday & Saturday'
    SUN_MON = 'Sunday & Monday'

class TokenTypeEnum(Enum):
    AUTH = 'auth'
    RESET = 'reset'