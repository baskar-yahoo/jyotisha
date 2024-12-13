#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import os.path
import sys
import csv
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[4]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass
from datetime import datetime
from math import ceil

from indic_transliteration import sanscript
from pytz import timezone as tz

import jyotisha
import jyotisha.custom_transliteration
import jyotisha.panchaanga.temporal.names
import jyotisha.panchaanga.spatio_temporal.annual
import jyotisha.panchaanga.temporal
from jyotisha.panchaanga.temporal import names, Graha
from jyotisha.panchaanga.spatio_temporal import City
from jyotisha.panchaanga.temporal import time
from jyotisha.panchaanga.temporal.festival import rules
from jyotisha.panchaanga.temporal.time import Timezone
from jyotisha.panchaanga.writer.tex.svajana_day_details import get_lagna_data_str, get_raahu_yama_gulika_strings, \
  get_karaNa_data_str, get_yoga_data_str, get_raashi_data_str, get_nakshatra_data_str, get_tithi_data_str

logging.basicConfig(
  level=logging.DEBUG,
  format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)

CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def dict_to_tsv(data, filename):
    """Converts a dictionary to a TSV file."""
    print('file name',filename, 'data',data)
    with open(filename, 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')

        # Write header row (if desired)
        if data:
            writer.writerow(data[0].keys())

        # Write data rows
        for row in data:
            writer.writerow(row.values())

def emit(panchaanga, time_format="hh:mm", languages=None, scripts=None, output_stream=None, panchdata=[]):
  """Write out the panchaanga TeX using a specified template
  """
  # day_colours = {0: 'blue', 1: 'blue', 2: 'blue',
  #                3: 'blue', 4: 'blue', 5: 'blue', 6: 'blue'}
  global panchdict
  panchdict={}
  compute_lagnams = panchaanga.computation_system.festival_options.set_lagnas
  if scripts is None:
    scripts = [sanscript.ITRANS]
  if languages is None:
    languages = ['itrans']
 # print("after compute_lagnams")
 # template_file = open(os.path.join(os.path.dirname(__file__), 'templates/daily_cal_template.tex'))

  #template_lines = template_file.readlines()
  #for i in range(len(template_lines)):
    #print(template_lines[i][:-1], file=output_stream)

  year = panchaanga.start_date.year
  print("Year", year)
  #logging.debug(year)
  panchdict['year']=year
  samvatsara_id = (year - 1568) % 60 + 1  # distance from prabhava
  samvatsara_names = (names.NAMES['SAMVATSARA_NAMES']['sa'][scripts[0]][samvatsara_id],
                      names.NAMES['SAMVATSARA_NAMES']['sa'][scripts[0]][(samvatsara_id % 60) + 1])

  yname = samvatsara_names[0]  # Assign year name until Mesha Sankranti
  panchdict['yname']=yname
  print("panchdata",panchdata)
  set_top_content(output_stream, panchaanga, samvatsara_names, scripts, year)
  
  daily_panchaangas = panchaanga.daily_panchaangas_sorted()
  for d, daily_panchaanga in enumerate(daily_panchaangas):
    if d == 0:
      previous_day_panchaanga = None
    else:
      previous_day_panchaanga = daily_panchaangas[d - 1]
    if daily_panchaanga.date < panchaanga.start_date or daily_panchaanga.date > panchaanga.end_date:
      continue
    [y, m, dt] = [daily_panchaanga.date.year, daily_panchaanga.date.month, daily_panchaanga.date.day]
    panchdict['year1']=y
    panchdict['month1']=m
    panchdict['day1']=dt

    # checking @ 6am local - can we do any better?
    local_time = tz(panchaanga.city.timezone).localize(datetime(y, m, dt, 6, 0, 0))
    panchdict['local_time']=local_time
    # compute offset from UTC in hours
    tz_off = (datetime.utcoffset(local_time).days * 86400 +
              datetime.utcoffset(local_time).seconds) / 3600.0
    panchdict['tz_off']=tz_off
    #print("before thithi")
    tithi_data_str = get_tithi_data_str(daily_panchaanga, scripts, time_format, previous_day_panchaanga, include_early_end_angas=True)
    #print("after thithi")
    nakshatra_data_str = get_nakshatra_data_str(daily_panchaanga, scripts, time_format, previous_day_panchaanga, include_early_end_angas=True)
    panchdict['tithi_data_str']=tithi_data_str
    yoga_data_str = get_yoga_data_str(daily_panchaanga, scripts, time_format, previous_day_panchaanga, include_early_end_angas=True)
    panchdict['yoga_data_str']=yoga_data_str
    karana_data_str = get_karaNa_data_str(daily_panchaanga, scripts, time_format, previous_day_panchaanga, include_early_end_angas=True)
    panchdict['karana_data_str']=karana_data_str
    rashi_data_str = get_raashi_data_str(daily_panchaanga, scripts, time_format)
    panchdict['rashi_data_str']=rashi_data_str
    lagna_data_str = get_lagna_data_str(daily_panchaanga, scripts, time_format) if compute_lagnams else ''
    panchdict['lagna_data_str']=lagna_data_str

    gulika, rahu, yama, raatri_gulika, raatri_yama, durmuhurta1, durmuhurta2 = get_raahu_yama_gulika_strings(daily_panchaanga, time_format)
    panchdict['gulika']=gulika
    panchdict['rahu']=rahu
    panchdict['yama']=yama
    panchdict['raatri_gulika']=raatri_gulika
    panchdict['raatri_yama']=raatri_yama
    panchdict['durmuhurta1']=durmuhurta1
    panchdict['durmuhurta2']=durmuhurta2 
    if daily_panchaanga.solar_sidereal_date_sunset.month == 1:
      # Flip the year name for the remaining days
      yname = samvatsara_names[1]
      panchdict['yname']=yname
    # Assign samvatsara, ayana, rtu #
    sar_data = ("test",
                                 names.NAMES['AYANA_NAMES']['sa'][scripts[0]][daily_panchaanga.solar_sidereal_date_sunset.month],
                                 names.NAMES['RTU_NAMES']['sa'][scripts[0]][daily_panchaanga.solar_sidereal_date_sunset.month])
    panchdict['sar_data']=sar_data
    if daily_panchaanga.solar_sidereal_date_sunset.month_transition is None:
      month_end_str = ''
    else:
      _m = daily_panchaangas[d - 1].solar_sidereal_date_sunset.month
      if daily_panchaanga.solar_sidereal_date_sunset.month_transition >= daily_panchaangas[d + 1].jd_sunrise:
        month_end_str = (
          names.NAMES['RASHI_NAMES']['sa'][scripts[0]][_m], time.Hour(
            24 * (daily_panchaanga.solar_sidereal_date_sunset.month_transition - daily_panchaangas[d + 1].julian_day_start)).to_string(format=time_format))
      else:
        month_end_str =  (
          names.NAMES['RASHI_NAMES']['hk'][scripts[0]][_m], time.Hour(
            24 * (daily_panchaanga.solar_sidereal_date_sunset.month_transition - daily_panchaanga.julian_day_start)).to_string(format=time_format))
    panchdict['month_end_str']=month_end_str
    month_data = (
      names.NAMES['RASHI_NAMES']['sa'][scripts[0]][daily_panchaanga.solar_sidereal_date_sunset.month], daily_panchaanga.solar_sidereal_date_sunset.day,
      month_end_str)
    panchdict['month_data']=month_data
    print("after assignment and before caldata")
   # print('\\caldata{%s}{%s}{%s{%s}{%s}{%s}%s}' %
   #       (names.month_map[m].upper(), dt, month_data,
   #        names.get_chandra_masa(daily_panchaanga.lunar_month_sunrise.index, scripts[0]),
   #        names.NAMES['RTU_NAMES']['sa'][scripts[0]][int(ceil(daily_panchaanga.lunar_month_sunrise.index))],
   #        names.NAMES['VARA_NAMES']['sa'][scripts[0]][daily_panchaanga.date.get_weekday()], sar_data), file=output_stream)

    stream_sun_moon_rise_data(daily_panchaanga, output_stream, time_format)
    #panchdict['sun_moon_rise_data']=sun_moon_rise_data
    stream_daylength_based_periods(daily_panchaanga, output_stream, time_format)
    #panchdict['daylength_based_periods']=daylength_based_periods
    print( jyotisha.custom_transliteration.tr(tithi_data_str,'iast',titled=True,source_script=sanscript.brahmic.DEVANAGARI), nakshatra_data_str, rashi_data_str, yoga_data_str,
             karana_data_str, lagna_data_str, file=output_stream)

    #print_festivals_to_stream(daily_panchaanga, output_stream, panchaanga, languages, scripts)

    print(panchaanga.start_date, names.weekday_short_map[daily_panchaanga.date.get_weekday()], file=output_stream)
    print('raghu: ',rahu, 'yama: ',yama, 'gulika: ',gulika, file=output_stream)

    if m == 12 and dt == 31:
      break
  panchdata.append(panchdict)
  print(file=output_stream)


def stream_daylength_based_periods(daily_panchaanga, output_stream, time_format):
  #global panchdict
  jd = daily_panchaanga.julian_day_start
  panchdict['jd']=jd
  braahma_start = time.Hour(24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.braahma.jd_start - jd)).to_string(
    format=time_format)
  panchdict['braahma_start']=braahma_start
  praatahsandhya_start = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.praatas_sandhyaa.jd_start - jd)).to_string(format=time_format)
  panchdict['praatahsandhya_start']=praatahsandhya_start  
  praatahsandhya_end = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.praatas_sandhyaa.jd_end - jd)).to_string(format=time_format)
  panchdict['praatahsandhya_end']=praatahsandhya_end
  saangava = time.Hour(24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.saangava.jd_start - jd)).to_string(
    format=time_format)
  panchdict['saangava']=saangava
  madhyaahna = time.Hour(24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.madhyaahna.jd_start - jd)).to_string(
    format=time_format)
  panchdict['madhyaahna']=madhyaahna
  madhyahnika_sandhya_start = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.maadhyaahnika_sandhyaa.jd_start - jd)).to_string(format=time_format)
  panchdict['madhyahnika_sandhya_start']=madhyahnika_sandhya_start
  madhyahnika_sandhya_end = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.maadhyaahnika_sandhyaa.jd_end - jd)).to_string(
    format=time_format)
  panchdict['madhyahnika_sandhya_end']=madhyahnika_sandhya_end
  aparaahna = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.aparaahna.jd_start - jd)).to_string(
    format=time_format)
  aparaahna_end = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.aparaahna.jd_end - jd)).to_string(
    format=time_format)
  panchdict['aparaahna_end']=aparaahna_end
  sayahna = time.Hour(24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.saayaahna.jd_start - jd)).to_string(
    format=time_format)
  panchdict['sayahna']=sayahna
  sayahna_end = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.saayaahna.jd_end - jd)).to_string(
    format=time_format)
  panchdict['sayahna_end']=sayahna_end
  sayamsandhya_start = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.saayam_sandhyaa.jd_start - jd)).to_string(format=time_format)
  panchdict['sayamsandhya_start']=sayamsandhya_start
  sayamsandhya_end = time.Hour(
    24 * (daily_panchaanga.day_length_based_periods.fifteen_fold_division.saayam_sandhyaa.jd_end - jd)).to_string(format=time_format)
  panchdict['sayamsandhya_end']=sayamsandhya_end
  ratriyama1 = time.Hour(24 * (daily_panchaanga.day_length_based_periods.eight_fold_division.raatri_yaama[0].jd_end - jd)).to_string(
    format=time_format)
  panchdict['ratriyama1']=ratriyama1
  shayana_time_end = time.Hour(24 * (daily_panchaanga.day_length_based_periods.eight_fold_division.shayana.jd_start - jd)).to_string(
    format=time_format)
  panchdict['shayana_time_end']=shayana_time_end
  dinaanta = time.Hour(24 * (daily_panchaanga.day_length_based_periods.eight_fold_division.dinaanta.jd_start - jd)).to_string(
    format=time_format)
  panchdict['dinaanta']=dinaanta
  print(
    ("braahma_start:",braahma_start, "praatahsandhya_start:",praatahsandhya_start, "praatahsandhya_end:",praatahsandhya_end,
                                                               "saangava:",saangava,
                                                               madhyahnika_sandhya_start, madhyahnika_sandhya_end,
                                                               madhyaahna, aparaahna, sayahna,
                                                               sayamsandhya_start, sayamsandhya_end,
                                                               ratriyama1, shayana_time_end, dinaanta),
    file=output_stream)


def stream_sun_moon_rise_data(daily_panchaanga, output_stream, time_format):
  jd = daily_panchaanga.julian_day_start
  sunrise = time.Hour(24 * (daily_panchaanga.jd_sunrise - jd)).to_string(
    format=time_format)
  sunset = time.Hour(24 * (daily_panchaanga.jd_sunset - jd)).to_string(format=time_format)
  moonrise = time.Hour(24 * (daily_panchaanga.graha_rise_jd[Graha.MOON] - jd)).to_string(
    format=time_format)
  moonset = time.Hour(24 * (daily_panchaanga.graha_set_jd[Graha.MOON] - jd)).to_string(
    format=time_format)
  midday = time.Hour(24 * (daily_panchaanga.jd_sunrise*0.5 + daily_panchaanga.jd_sunset*0.5 - jd)).to_string(
  format=time_format)
  if daily_panchaanga.graha_rise_jd[Graha.MOON] > daily_panchaanga.jd_next_sunrise:
    moonrise = '---'
  if daily_panchaanga.graha_set_jd[Graha.MOON] > daily_panchaanga.jd_next_sunrise:
    moonset = '---'
  if daily_panchaanga.graha_rise_jd[Graha.MOON] < daily_panchaanga.graha_set_jd[Graha.MOON]:
    print((sunrise, sunset, moonrise, moonset, midday), file=output_stream)
  else:
    print((sunrise, sunset, moonrise, moonset, midday), file=output_stream)
  panchdict['sunrise']=sunrise
  panchdict['sunset']=sunset
  panchdict['moonrise']=moonrise
  panchdict['moonset']=moonset
  panchdict['midday']=midday  
  

def print_festivals_to_stream(daily_panchaanga, output_stream, panchaanga, languages, scripts):
  rules_collection = rules.RulesCollection.get_cached(
    repos_tuple=tuple(panchaanga.computation_system.festival_options.repos), julian_handling=panchaanga.computation_system.festival_options.julian_handling)
  fest_details_dict = rules_collection.name_to_rule
  print(
    [(languages, scripts, Timezone(timezone_id=panchaanga.city.timezone),
                fest_details_dict, daily_panchaanga.date) for f in
     sorted(daily_panchaanga.festival_id_to_instance.values())], file=output_stream)


def set_top_content(output_stream, panchaanga, samvatsara_names, scripts, year):
  print( year, file=output_stream)
  print( jyotisha.custom_transliteration.tr(samvatsara_names[0],'iast',titled=True,source_script=sanscript.brahmic.DEVANAGARI), 
         jyotisha.custom_transliteration.tr(samvatsara_names[1],'iast',titled=True,source_script=sanscript.brahmic.DEVANAGARI),file=output_stream)
  print( jyotisha.custom_transliteration.tr('kali', 'iast'), file=output_stream)
  print( (year + 3100, year + 3101), file=output_stream)
  print( panchaanga.city.name, file=output_stream)
  print( jyotisha.custom_transliteration.print_lat_lon(panchaanga.city.latitude, panchaanga.city.longitude), file=output_stream)
  

def main():
  [city_name, latitude, longitude, tz] = sys.argv[1:5]
  start_date = sys.argv[5]
  end_date = sys.argv[6]
  panchdata=[]
  panchdict={}
  #print(sys.argv[0]," 0 ", sys.argv[1], " 1 ", sys.argv[5], " 5 ", sys.argv[6], " 6 ")
  #print("about to emit")
  compute_lagnams = False  # Default
  scripts = [sanscript.DEVANAGARI]  # Default language is devanagari
  fmt = 'hh:mm'

  #if len(sys.argv) == 9:
  #  compute_lagnams = True
  #  fmt = sys.argv[7]
  #  scripts = sys.argv[6].split(",")
  #elif len(sys.argv) == 8:
  #  scripts = sys.argv[6].split(",")
  #  fmt = sys.argv[7]
  #  compute_lagnams = False
  #elif len(sys.argv) == 7:
  #  scripts = sys.argv[6].split(",")
  #  compute_lagnams = False

  city = City(city_name, latitude, longitude, tz)

  panchaanga = jyotisha.panchaanga.spatio_temporal.annual.get_panchaanga_for_given_dates(city=city, start_date=start_date, end_date=end_date)
  output_stream=city.name+end_date+'.tsv'
  emit(panchaanga, scripts=scripts,panchdata=panchdata)
  # panchaanga.writeDebugLog()
  #with open(output_stream, 'w', newline='\n') as f_output:
   # tsv_output = csv.writer(f_output, delimiter='\t')
  dict_to_tsv(data=panchdata,filename=output_stream)

if __name__ == '__main__':
  main()
