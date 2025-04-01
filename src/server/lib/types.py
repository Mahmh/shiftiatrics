from typing import Literal, TypeAlias, Optional
from enum import Enum

SettingValue: TypeAlias = Optional[str | int | bool | list | tuple | Literal['null']]
ScheduleType: TypeAlias = list[list[list[int]]]
WeekendDays: TypeAlias = Literal['Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday']
Interval: TypeAlias = Literal['Daily', 'Weekly', 'Monthly']
TokenType: TypeAlias = Literal['auth', 'reset', 'verify']
PricingPlanName: TypeAlias = Literal['basic', 'standard', 'premium', 'custom']
QueryType: TypeAlias = Literal[
    'General Inquiry',
    'Custom Plan',
    'Technical Issue',
    'Bug Report',
    'Feature Suggestion',
    'Feature Feedback',
    'Business Inquiry',
    'Partnership & Collaboration',
    'Billing & Payment Issue',
    'Refund Request',
    'Account Access Issue',
    'Unable to Log In',
    'Integration Request',
    'Customization Inquiry',
    'Data & Privacy Concerns',
    'Job & Career Opportunities',
    'Other'
]

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
    VERIFY = 'verify'

class PricingPlanEnum(Enum):
    BASIC = 'basic'
    STANDARD = 'standard'
    PREMIUM = 'premium'
    CUSTOM = 'custom'