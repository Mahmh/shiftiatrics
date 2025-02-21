from sqlalchemy import create_engine, text, Column, Integer, String, Boolean, ForeignKey, Date, Time, Enum
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import sessionmaker, declarative_base
from src.server.lib.constants import ENGINE_URL
from src.server.lib.types import WeekendDaysEnum, IntervalEnum

engine = create_engine(ENGINE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=True)
    oauth_provider = Column(String(16), nullable=True)
    oauth_token = Column(String(2048), nullable=True)
    oauth_id = Column(String(64), unique=True, nullable=True)
    __repr__ = lambda self: f'Account({self.account_id})'


class Token(Base):
    __tablename__ = 'tokens'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    token = Column(String(256), unique=True, nullable=False)
    created_at = Column(Date, default=text('CURRENT_TIMESTAMP'))
    expires_at = Column(Date, nullable=True)
    __repr__ = lambda self: f'Token({self.account_id})'


class Employee(Base):
    __tablename__ = 'employees'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = Column(String(100), nullable=False)
    min_work_hours = Column(Integer, nullable=True)
    max_work_hours = Column(Integer, nullable=True)
    __repr__ = lambda self: f'Employee({self.employee_id})'


class Shift(Base):
    __tablename__ = 'shifts'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    shift_id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String(100), nullable=False)
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


class Holiday(Base):
    __tablename__ = 'holidays'
    account_id = Column(Integer, ForeignKey('accounts.account_id', ondelete='CASCADE'), nullable=False)
    holiday_id = Column(Integer, primary_key=True, autoincrement=True)
    holiday_name = Column(String(100), nullable=False)
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
        Enum(WeekendDaysEnum, name='weekend_days_enum', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default='Saturday & Sunday',
        default=WeekendDaysEnum.SAT_SUN.value
    )
    max_emps_in_shift = Column(Integer, nullable=False, server_default='1', default=1)
    email_ntf_enabled = Column(Boolean, nullable=False, server_default='false', default=False)
    email_ntf_interval = Column(
        Enum(IntervalEnum, name='interval_enum', values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default='Monthly',
        default=IntervalEnum.MONTHLY.value
    )
    __repr__ = lambda self: f'Settings({self.account_id})'