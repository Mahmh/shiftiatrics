from typing import Literal, TypeAlias
from enum import Enum

SettingValue: TypeAlias = bool | str
ScheduleType: TypeAlias = list[list[list[int]]]
WeekendDays: TypeAlias = Literal['Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday']
Interval: TypeAlias = Literal['Daily', 'Weekly', 'Monthly']
TokenType: TypeAlias = Literal['auth', 'reset', 'verify']
PlanName: TypeAlias = Literal['starter', 'growth', 'advanced', 'enterprise']
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

class WeekendDaysEnum(Enum):
    SAT_SUN = 'Saturday & Sunday'
    FRI_SAT = 'Friday & Saturday'
    SUN_MON = 'Sunday & Monday'

class TokenTypeEnum(Enum):
    AUTH = 'auth'
    RESET = 'reset'
    VERIFY = 'verify'

class PricingPlanEnum(Enum):
    STARTER = 'starter'
    GROWTH = 'growth'
    ADVANCED = 'advanced'
    ENTERPRISE = 'enterprise'