from sqlalchemy import (
    create_engine,
    func,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    Date,
    DateTime,
    Time,
    Enum,
    ForeignKey,
    Numeric,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base
from src.server.lib.constants import ENGINE_URL
from src.server.lib.types import WeekendDaysEnum, IntervalEnum, TokenTypeEnum, PricingPlanEnum


engine = create_engine(ENGINE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()
_values_callable = lambda x: [e.value for e in x]


class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=True)
    email_verified = Column(Boolean, nullable=False, server_default='false', default=False)
    stripe_customer_id = Column(String(128), nullable=True)
    has_used_trial = Column(Boolean, nullable=False, server_default='false', default=False)
    oauth_provider = Column(String(16), nullable=True)
    oauth_token = Column(String(2048), nullable=True)
    oauth_id = Column(String(64), unique=True, nullable=True)
    oauth_email = Column(String(256), unique=True, nullable=True)
    __repr__ = lambda self: f'Account({self.account_id})'


class Token(Base):
    __tablename__ = 'tokens'
    token_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    token = Column(String(64), unique=True, nullable=False)
    token_type = Column(
        Enum(TokenTypeEnum, name='token_type_enum', values_callable=_values_callable),
        nullable=False,
        server_default='auth',
        default=TokenTypeEnum.AUTH.value
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    __repr__ = lambda self: f'Token({self.account_id})'


class Subscription(Base):
    __tablename__ = 'subscriptions'
    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    plan = Column(
        Enum(PricingPlanEnum, name='pricing_plan_enum', values_callable=_values_callable),
        nullable=False
    )
    price = Column(Numeric(7, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    plan_details = Column(JSONB, nullable=False)
    stripe_session_id = Column(String(128), nullable=False)
    stripe_subscription_id = Column(String(128), unique=True, nullable=False)
    __table_args__ = (CheckConstraint('price >= 0', name='positive_price'),)
    __repr__ = lambda self: f'Subscription({self.account_id})'


class CustomPlanInfo(Base):
    __tablename__ = 'custom_plan_infos'
    info_id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), unique=True, nullable=False)
    price = Column(Numeric(7, 2), nullable=False)
    plan_details = Column(JSONB, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    stripe_price_id = Column(String(128), unique=True, nullable=False)
    stripe_product_id = Column(String(128), nullable=False)
    stripe_pending_checkout_url = Column(Text, nullable=True)
    __table_args__ = (
        CheckConstraint('price >= 0', name='positive_price'),
        UniqueConstraint('stripe_price_id', 'stripe_product_id', name='uq_price_product')
    )
    __repr__ = lambda self: f'CustomPlanInfo({self.account_id})'


class Employee(Base):
    __tablename__ = 'employees'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(40), nullable=False)
    min_work_hours = Column(Integer, nullable=True)
    max_work_hours = Column(Integer, nullable=True)
    __repr__ = lambda self: f'Employee({self.employee_id})'


class Shift(Base):
    __tablename__ = 'shifts'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(40), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    __repr__ = lambda self: f'Employee({self.shift_id})'


class Schedule(Base):
    __tablename__ = 'schedules'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(JSONB, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    __repr__ = lambda self: f'Schedule({self.schedule_id})'


class ScheduleRequests(Base):
    __tablename__ = 'schedule_requests'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), primary_key=True)
    num_requests = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    __repr__ = lambda self: f'ScheduleRequests({self.account_id})'


class Holiday(Base):
    __tablename__ = 'holidays'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    holiday_id = Column(Integer, primary_key=True, autoincrement=True)
    holiday_name = Column(String(40), nullable=False)
    assigned_to = Column(ARRAY(Integer, dimensions=1), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    __repr__ = lambda self: f'Holiday({self.holiday_id})'


class Settings(Base):
    __tablename__ = 'settings'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False, primary_key=True)
    dark_theme_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    min_max_work_hours_enabled = Column(Boolean, nullable=False, server_default='true', default=True)
    multi_emps_in_shift_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    multi_shifts_one_emp_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    weekend_days = Column(
        Enum(WeekendDaysEnum, name='weekend_days_enum', values_callable=_values_callable),
        nullable=False,
        server_default='Saturday & Sunday',
        default=WeekendDaysEnum.SAT_SUN.value
    )
    max_emps_in_shift = Column(Integer, nullable=False, server_default='1', default=1)
    email_ntf_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    email_ntf_interval = Column(
        Enum(IntervalEnum, name='interval_enum', values_callable=_values_callable),
        nullable=False,
        server_default='Monthly',
        default=IntervalEnum.MONTHLY.value
    )
    __repr__ = lambda self: f'Settings({self.account_id})'