from sqlalchemy import create_engine, func, Column, Integer, String, Boolean, ForeignKey, Date, DateTime, Time, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base
from src.server.lib.constants import ENGINE_URL
from src.server.lib.types import WeekendDaysEnum, TokenTypeEnum, PricingPlanEnum

engine = create_engine(ENGINE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()
_values_callable = lambda x: [e.value for e in x]


class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    email_verified = Column(Boolean, nullable=False, server_default='false', default=False)
    password_changed = Column(Boolean, nullable=False, server_default='false', default=False)
    stripe_customer_id = Column(String(128), unique=True, nullable=True)
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
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    stripe_subscription_id = Column(String(128), unique=True, nullable=False)
    stripe_chkout_session_id = Column(String(128), unique=True, nullable=False)
    __repr__ = lambda self: f'Subscription({self.account_id})'


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
    __repr__ = lambda self: f'Shift({self.shift_id})'


class Schedule(Base):
    __tablename__ = 'schedules'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(JSONB, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    __repr__ = lambda self: f'Schedule({self.schedule_id})'


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
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), primary_key=True)
    dark_theme_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    weekend_days = Column(
        Enum(WeekendDaysEnum, name='weekend_days_enum', values_callable=_values_callable),
        nullable=False,
        server_default='Saturday & Sunday',
        default=WeekendDaysEnum.SAT_SUN.value
    )
    __repr__ = lambda self: f'Settings({self.account_id})'