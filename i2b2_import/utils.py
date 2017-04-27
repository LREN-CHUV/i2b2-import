import re
from datetime import datetime
import logging

#######################################################################################################################
# SETTINGS
#######################################################################################################################

DEFAULT_DATE = datetime(1, 1, 1)

YEARS_PER_MONTH = 0.0833334
YEARS_PER_WEEK = 0.0191781
YEARS_PER_DAY = 0.00273973


#######################################################################################################################
# PUBLIC FUNCTIONS
#######################################################################################################################

def find_type(val):
    try:
        float(val)
        return 'N'
    except ValueError:
        return 'T'


def eu_date_to_datetime(d):
    return datetime.strptime(d, "%d.%m.%Y")


def compute_age_years(subject_age, age_qualifier):
    subject_age = float(subject_age)
    if 'Y' == str(age_qualifier).upper():
        return subject_age
    elif 'M' == str(age_qualifier).upper():
        return YEARS_PER_MONTH * subject_age
    elif 'W' == str(age_qualifier).upper():
        return YEARS_PER_WEEK * subject_age
    elif 'D' == str(age_qualifier).upper():
        return YEARS_PER_DAY * subject_age
    else:
        return None


def split_patient_id(participant_id):
    res = re.split("_", participant_id)
    if len(res) == 2:
        return res


def datetime_from_dcm_date(date):
    try:
        return datetime(int(date[:4]), int(date[4:6]), int(date[6:8]))
    except ValueError:
        logging.warning("Cannot parse date from : " + str(date))
