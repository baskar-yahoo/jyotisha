import jyotisha
from jyotisha import custom_transliteration
from jyotisha.panchaanga.temporal import time, names


def get_lagna_data_str(daily_panchaanga, scripts, time_format):
  jd = daily_panchaanga.julian_day_start
  lagna_data_str = 'लग्नम्–'
  for lagna_ID, lagna_end_jd in daily_panchaanga.lagna_data:
    lagna = names.NAMES['RASHI_NAMES']['sa'][scripts[0]][lagna_ID]
    lagna_data_str = '%s\\mbox{%s\\RIGHTarrow\\textsf{%s}} ' % \
                     (lagna_data_str, lagna,
                      time.Hour(24 * (lagna_end_jd - jd)).to_string(
                        format=time_format))
  return lagna_data_str


def get_raahu_yama_gulika_strings(daily_panchaanga, time_format):
  jd = daily_panchaanga.julian_day_start
  rahu = '%s--%s' % (
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.raahu.jd_start - jd)).to_string(
      format=time_format),
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.raahu.jd_end - jd)).to_string(
      format=time_format))
  yama = '%s--%s' % (
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.yama.jd_start - jd)).to_string(
      format=time_format),
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.yama.jd_end - jd)).to_string(
      format=time_format))
  gulika = '%s--%s' % (
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.gulika.jd_start - jd)).to_string(
      format=time_format),
    time.Hour(24 * (daily_panchaanga.day_length_based_periods.gulika.jd_end - jd)).to_string(
      format=time_format))
  return gulika, rahu, yama


def get_karaNa_data_str(daily_panchaanga, scripts, time_format):
  jd = daily_panchaanga.julian_day_start
  karana_data_str = ''
  for numKaranam, karaNa_span in enumerate(daily_panchaanga.sunrise_day_angas.karanas_with_ends):
    (karana_ID, karana_end_jd) = (karaNa_span.anga.index, karaNa_span.jd_end)
    # if numKaranam == 1:
    #     karana_data_str += '\\hspace{1ex}'
    karana = names.NAMES['KARANA_NAMES']['sa'][scripts[0]][karana_ID]
    if karana_end_jd is None:
      karana_data_str = '%s\\mbox{%s\\Too{}}' % \
                        (karana_data_str, karana)
    else:
      karana_data_str = '%s\\mbox{%s\\To{}\\textsf{%s (%s)}}\\hspace{1ex}' % \
                        (karana_data_str, karana,
                         time.Hour(
                           24 * (karana_end_jd - daily_panchaanga.jd_sunrise)).to_string(format='gg-pp'),
                         time.Hour(24 * (karana_end_jd - jd)).to_string(
                           format=time_format))
  return karana_data_str


def get_yoga_data_str(daily_panchaanga, scripts, time_format):
  jd = daily_panchaanga.julian_day_start
  yoga_data_str = ''
  for iYoga, yoga_span in enumerate(daily_panchaanga.sunrise_day_angas.yogas_with_ends):
    (yoga_ID, yoga_end_jd) = (yoga_span.anga.index, yoga_span.jd_end)
    # if yoga_data_str != '':
    #     yoga_data_str += '\\hspace{1ex}'
    yoga = names.NAMES['YOGA_NAMES']['sa'][scripts[0]][yoga_ID]
    if yoga_end_jd is None:
      if iYoga == 0:
        yoga_data_str = '%s\\mbox{%s\\To{}%s}' % \
                        (yoga_data_str, yoga, custom_transliteration.tr('ahOrAtram', scripts[0]))
      else:
        yoga_data_str = '%s\\mbox{%s\\Too{}}' % \
                        (yoga_data_str, yoga)
    else:
      yoga_data_str = '%s\\mbox{%s\\To{}\\textsf{%s (%s)}}\\hspace{1ex}' % \
                      (yoga_data_str, yoga,
                       time.Hour(24 * (yoga_end_jd - daily_panchaanga.jd_sunrise)).to_string(
                         format='gg-pp'),
                       time.Hour(24 * (yoga_end_jd - jd)).to_string(
                         format=time_format))
  if yoga_end_jd is not None:
    yoga_data_str += '\\mbox{%s\\Too{}}' % (
      names.NAMES['YOGA_NAMES']['sa'][scripts[0]][(yoga_ID % 27) + 1])
  return yoga_data_str


def get_raashi_data_str(daily_panchaanga, scripts, time_format):
  jd = daily_panchaanga.julian_day_start
  rashi_data_str = ''
  for iRaashi, raashi_span in enumerate(daily_panchaanga.sunrise_day_angas.raashis_with_ends):
    if iRaashi == 0:
      (rashi_ID, rashi_end_jd) = (raashi_span.anga.index, raashi_span.jd_end)
      # if rashi_data_str != '':
      #     rashi_data_str += '\\hspace{1ex}'
      rashi = names.NAMES['RASHI_SUFFIXED_NAMES']['sa'][scripts[0]][rashi_ID]
      if rashi_end_jd is None:
        rashi_data_str = '%s\\mbox{%s}' % (rashi_data_str, rashi)
      else:
        rashi_data_str = '%s\\mbox{%s \\RIGHTarrow \\textsf{%s}}' % \
                         (rashi_data_str, rashi,
                          time.Hour(24 * (rashi_end_jd - jd)).to_string(
                            format=time_format))
  return rashi_data_str


def get_nakshatra_data_str(daily_panchaanga, scripts, time_format):
  jd = daily_panchaanga.julian_day_start
  nakshatra_data_str = ''
  for iNakshatra, nakshatra_span in enumerate(daily_panchaanga.sunrise_day_angas.nakshatras_with_ends):
    (nakshatra_ID, nakshatra_end_jd) = (nakshatra_span.anga.index, nakshatra_span.jd_end)
    if nakshatra_data_str != '':
      nakshatra_data_str += '\\hspace{1ex}'
    nakshatra = names.NAMES['NAKSHATRA_NAMES']['sa'][scripts[0]][nakshatra_ID]
    if nakshatra_end_jd is None:
      if iNakshatra == 0:
        nakshatra_data_str = '%s\\mbox{%s\\To{}%s}' % \
                             (nakshatra_data_str, nakshatra,
                              custom_transliteration.tr('ahOrAtram', scripts[0]))
    else:
      nakshatra_data_str = '%s\\mbox{%s\\To{}\\textsf{%s (%s)}}' % \
                           (nakshatra_data_str, nakshatra,
                            time.Hour(
                              24 * (nakshatra_end_jd - daily_panchaanga.jd_sunrise)).to_string(format='gg-pp'),
                            time.Hour(24 * (nakshatra_end_jd - jd)).to_string(
                              format=time_format))
  return nakshatra_data_str


def get_tithi_data_str(daily_panchaanga, scripts, time_format):
  # What is the jd at 00:00 local time today?
  jd = daily_panchaanga.julian_day_start
  tithi_data_str = ''
  for iTithi, tithi_span in enumerate(daily_panchaanga.sunrise_day_angas.tithis_with_ends):
    (tithi_ID, tithi_end_jd) = (tithi_span.anga.index, tithi_span.jd_end)
    # if tithi_data_str != '':
    #     tithi_data_str += '\\hspace{1ex}'
    tithi = '\\raisebox{-1pt}{\\moon[scale=0.8]{%d}}\\hspace{2pt}' % (tithi_ID) + \
            names.NAMES['TITHI_NAMES']['sa'][scripts[0]][tithi_ID]
    if tithi_end_jd is None:
      if iTithi == 0:
        tithi_data_str = '%s\\mbox{%s\\To{}%s}' % \
                         (tithi_data_str, tithi,
                          custom_transliteration.tr('ahOrAtram (tridinaspRk)', scripts[0]))
    else:
      tithi_data_str = '%s\\mbox{%s\\To{}\\textsf{%s (%s)}}\\hspace{1ex}' % \
                       (tithi_data_str, tithi,
                        time.Hour(
                          24 * (tithi_end_jd - daily_panchaanga.jd_sunrise)).to_string(format='gg-pp'),
                        time.Hour(24 * (tithi_end_jd - jd)).to_string(
                          format=time_format))
  return tithi_data_str