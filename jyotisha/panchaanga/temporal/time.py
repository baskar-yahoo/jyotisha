import datetime as dt_module
import logging
import sys
import traceback
import datetime
from math import modf
from numbers import Number

import pytz
from astropy.time import Time

from jyotisha.util import zero_if_none
from sanskrit_data.schema import common
from sanskrit_data.schema.common import JsonObject


class Hour(JsonObject):
  """This  class is a time class with methods for printing, conversion etc.
  """

  def __init__(self, hour):
    super().__init__()
    import numpy
    if type(hour) == float or type(hour) == numpy.float64 or type(hour) == int:
      self.hour = hour
    else:
      logging.error(type(hour))
      logging.error(hour)
      raise (TypeError('Input to time class must be int or float!'))

  def toString(self, default_suffix='', format='hh:mm', rounding=False):
    if self.hour < 0:
      logging.error('t<0! %s ' % self.hour)
      logging.error(traceback.print_stack())

    msec, secs = modf(self.hour * 3600)
    msec = round(msec * 1000)
    if msec == 1000:
      msec = 0
      secs += 1

    hour = secs // 3600
    secs = secs % 3600

    suffix = default_suffix
    if format[-1] == '*':
      if hour >= 24:
        suffix = '*'
    else:
      if hour >= 24:
        hour -= 24
        suffix = '(+1)'  # Default notation for times > 23:59

    minute = secs // 60
    secs = secs % 60
    second = secs

    if format in ('hh:mm', 'hh:mm*'):
      # Rounding done if 30 seconds have elapsed
      return '%02d:%02d%s' % (hour, minute + ((secs + (msec >= 500)) >= 30) * rounding, suffix)
    elif format in ('hh:mm:ss', 'hh:mm:ss*'):
      # Rounding done if 500 milliseconds have elapsed
      return '%02d:%02d:%02d%s' % (hour, minute, second + (msec >= 500) * rounding, suffix)
    elif format in ('hh:mm:ss.sss', 'hh:mm:ss.sss*'):
      return '%02d:%02d:%02d.%03d%s' % (hour, minute, second, msec, suffix)
    elif format == 'gg-pp':  # ghatika-pal
      secs = round(self.hour * 3600)
      gg = secs // 1440
      secs = secs % 1440
      pp = secs // 24
      return ('%d-%d' % (gg, pp))
    elif format == 'gg-pp-vv':  # ghatika-pal-vipal
      vv_tot = round(self.hour * 3600 / 0.4)
      logging.debug(vv_tot)
      vv = vv_tot % 60
      logging.debug(vv)
      vv_tot = (vv_tot - vv) // 60
      logging.debug(vv_tot)
      pp = vv_tot % 60
      logging.debug(pp)
      vv_tot = (vv_tot - pp) // 60
      logging.debug(vv_tot)
      gg = vv_tot
      logging.debug(gg)
      return ('%d-%d-%d' % (gg, pp, vv))
    else:
      raise Exception("""Unknown format""")

  def __str__(self):
    return self.toString(format='hh:mm:ss')


def decypher_fractional_hours(time_in_hours):
  minutes, _ = modf(time_in_hours * 60)
  seconds, minutes = modf(minutes * 60)
  return (int(time_in_hours), int(minutes), seconds)


class BasicDate(JsonObject):
  def __init__(self, month, day, year=None):
    self.year = year
    self.month = int(month)
    self.day = int(day)

  def __str__(self):
    if self.year is None:
      return "%02d-%02d" % (self.month, self.day) 
    else:
      return "%04d-%02d-%02d" % (self.year, self.month, self.day)

  def __lt__(self, other):
    return str(self) < str(other)

  def __hash__(self):
    return hash(str(self))


class BasicDateWithTransitions(BasicDate):
  def __init__(self, month, day, year=None, month_transition=None, day_transition=None):
    super(BasicDateWithTransitions, self).__init__(year=year, month=month, day=day)
    self.day_transition = day_transition
    self.month_transition = month_transition
    
  def set_transitions(self, day_transition, month_transition):
    self.day_transition = day_transition
    self.month_transition = month_transition


class Date(BasicDate):
  def __init__(self, year, month, day, hour=None, minute=None, second=None):
    super(Date, self).__init__(year=year, month=month, day=day)
    self.hour = hour
    self.minute = minute
    self.second = second
    self.weekday = None
  
  def set_time_to_day_start(self):
    self.hour = None
    self.minute = None
    self.second = None

  def to_datetime(self):
    return datetime.datetime(year=self.year, month=self.month, day=self.day, hour=zero_if_none(self.hour), minute=zero_if_none(self.minute), second=zero_if_none(self.second), microsecond=self.get_microseconds())

  def __sub__(self, other):
    if isinstance(other, Date):
      dt_diff = self.to_datetime() - other.to_datetime()
      return dt_diff.days + dt_diff.seconds / 3600.0 + dt_diff.microseconds / 60.0 / 1e6
    elif isinstance(other, Number):
      return self.offset_date(days=-other)

  def __add__(self, other):
    if isinstance(other, Number):
      return self.offset_date(days=other)


  @classmethod
  def from_datetime(cls, dt):
    return Date(year=dt.year, month=dt.month, day=dt.day, hour=dt.hour, minute=dt.minute, second=dt.second + dt.microsecond / float(1e6))

  def offset_date(self, **kwargs):
    dt = self.to_datetime()
    offset_dt = dt + datetime.timedelta(**kwargs)
    offset_date = Date.from_datetime(dt=offset_dt)
    return offset_date

  def as_tuple(self):
    return (self.year, self.month, self.day, self.hour, self.minute, self.second)

  def get_fractional_hour(self):
    return zero_if_none(self.hour) + zero_if_none(self.minute)/ 60.0 + zero_if_none(self.second)  / 3600.0

  def get_microseconds(self):  
    return int(zero_if_none(self.second) * 1e6 % 1e6)

  def to_date_fractional_hour_tuple(self):
    fractional_hour = self.get_fractional_hour()
    return [self.year, self.month, self.day, fractional_hour]

  def get_weekday(self):
    if self.weekday is None:
      self.weekday = dt_module.date(year=self.year, month=self.month, day=self.day).isoweekday() % 7
    return self.weekday

  def sanitize(self):
    (year, month, day, hour, minute, second) = (self.year, self.month, self.day, self.hour, self.minute, self.second)
    if second >= 60:
      minute = minute + second / 60
      second = second % 60
    if minute >= 60:
      hour = hour + minute / 60
      minute = minute % 60
    if hour >= 24:
      day = day + hour / 24
      hour = hour % 24
    from calendar import monthrange
    (_, final_day) = monthrange(year, month)
    if day > final_day:
      assert day == final_day + 1, "range not supported by this function"
      day = 1
      month = month + 1
    if month >= 13:
      year = year + (month - 1) / 12
      month = ((month - 1) % 12) + 1
    (self.year, self.month, self.day, self.hour, self.minute, self.second) = (year, month, day, hour, minute, second)
    return self.as_tuple()

  def get_date_str(self):
    return super(Date, self).__str__()


def jd_to_utc_gregorian(jd):
  tm = Time(jd, format='jd')
  tm.format = "ymdhms"
  return Date(year=int(tm.value["year"]), month=int(tm.value["month"]), day=int(tm.value["day"]),
              hour=int(tm.value["hour"]), minute=int(tm.value["minute"]), second=tm.value["second"])


def utc_gregorian_to_jd(date):
  if date.hour is None:
    date.set_time_to_day_start()
  tm = Time(
    {"year": date.year, "month": date.month, "day": date.day, "hour": zero_if_none(date.hour), "minute": zero_if_none(date.minute), "second": zero_if_none(date.second)},
    format='ymdhms')
  tm.format = "jd"
  return tm.value


def get_weekday(jd):
  tm = Time(jd, format='jd')
  tm.format = "datetime"
  # Sunday should be 0.
  return tm.value.isocalendar()[2] % 7


class Timezone:
  def __init__(self, timezone_id):
    self.timezone_id = timezone_id

  def get_timezone_offset_hours_from_jd(self, jd: float):
    """Get timezone offset in hours east of UTC (negative west of UTC)

    Timezone offset is dependent both on place and time (yes- time, not just date) - due to Daylight savings time.
    compute offset from UTC in hours
    """
    local_datetime = self.julian_day_to_local_datetime(jd=jd)
    return (datetime.datetime.utcoffset(local_datetime).days * 86400 +
            datetime.datetime.utcoffset(local_datetime).seconds) / 3600.0

  def julian_day_to_local_time(self, julian_day: float, round_seconds: bool = False) -> Date:
    local_datetime = self.julian_day_to_local_datetime(jd=julian_day)
    local_time = Date(
    local_datetime.year, local_datetime.month, local_datetime.day, local_datetime.hour, local_datetime.minute,
    local_datetime.second + local_datetime.microsecond / 1000000.0)
    if round_seconds:
      (y, m, dt, hours, minutes, seconds) = local_time.as_tuple()
      local_time = Date(y, m, dt, hours, minutes, int(round(seconds)))
    return local_time

  def julian_day_to_local_datetime(self, jd):
    tm = Time(jd, format='jd')
    tm.format = "datetime"
    return pytz.timezone(self.timezone_id).fromutc(tm.value)

  def local_time_to_julian_day(self, date):
    microseconds, _ = modf(zero_if_none(date.second) * 1000000)
    local_datetime = pytz.timezone(self.timezone_id).localize(
      datetime.datetime(date.year, date.month, date.day, zero_if_none(date.hour), zero_if_none(date.minute), int(zero_if_none(date.second)), int(microseconds)))
    tm = Time(local_datetime, format="datetime")
    tm.format = "jd"
    return tm.value

  def julian_day_to_local_time_str(self, jd):
    tm = Time(jd, format='jd')
    tm.format = "datetime"
    local_datetime = pytz.timezone(self.timezone_id).fromutc(tm.value)
    return str(local_datetime)



# A timezone frequently used for debugging (as most developers are located there.)
ist_timezone = Timezone("Asia/Calcutta")


# Essential for depickling to work.
common.update_json_class_index(sys.modules[__name__])
# logging.debug(common.json_class_index)
