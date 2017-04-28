from re import split
from os.path import join

from . import utils


DATASET = 'edsd'
ACQUISITION_SETTINGS = ['Manufacturer', 'ManufacturerModelName', 'MagneticFieldStrength']
ACQUISITION_CONCEPT_PREFIX = join("/", DATASET, "Imaging Data/Acquisition Settings")


def txt2i2b2(file_path, i2b2_conn):
    info = _extract_info(file_path)
    patient_ide = info['PatientName']  # Sometimes the patient ID is stored in PatientName field for EDSD
    patient_sex = info['PatientSex']
    patient_age = utils.compute_age_years(int(info['PatientAge'][:-1]), info['PatientAge'][-1])
    study_id = 'V' + info['StudyID'] if len(info['StudyID']) > 1 else 'V0' + info['StudyID']
    visit_ide = patient_ide + '_' + study_id
    acq_date = utils.datetime_from_dcm_date(info['AcquisitionDate'])
    birthdate = utils.datetime_from_dcm_date(info['PatientBirthdate'])

    encounter_num = i2b2_conn.get_encounter_num(visit_ide, DATASET, DATASET, patient_ide, DATASET)
    patient_num = i2b2_conn.get_patient_num(patient_ide, DATASET, DATASET)

    i2b2_conn.save_visit(encounter_num, patient_num, patient_age, acq_date)
    i2b2_conn.save_patient(patient_num, patient_sex, birth_date=birthdate)

    visit = i2b2_conn.get_visit(encounter_num, patient_num)

    concept_path = join(ACQUISITION_CONCEPT_PREFIX, "name")
    concept_cd = DATASET + ':protocol_name'
    i2b2_conn.save_concept(concept_path, concept_cd)
    try:
        start_date = visit.start_date
        if not start_date:
            raise AttributeError
    except AttributeError:
        start_date = utils.DEFAULT_DATE
    i2b2_conn.save_observation(encounter_num, concept_cd, DATASET, start_date, patient_num, 'T',
                               info['SeriesDescription'], None)

    for concept in ACQUISITION_SETTINGS:
        concept_cd = DATASET + ':' + concept
        concept_path = join(ACQUISITION_CONCEPT_PREFIX, concept)
        i2b2_conn.save_concept(concept_path, concept_cd)
        val = info[concept]
        valtype_cd = utils.find_type(val)
        if valtype_cd == 'N':
            tval_char = 'E'
            nval_num = float(val)
        else:
            tval_char = val
            nval_num = None
        try:
            start_date = visit.start_date
            if not start_date:
                raise AttributeError
        except AttributeError:
            start_date = utils.DEFAULT_DATE
        i2b2_conn.save_observation(encounter_num, concept_cd, DATASET, start_date, patient_num, valtype_cd,
                                   tval_char, nval_num)


def _extract_info(file_path):
    f = open(file_path, 'r')
    d = {}
    for line in f.readlines():
        line = line.strip()
        line = line.split('//')
        if len(line) == 3:
            if not line[1].isspace():
                key = ''.join(split(r'[ ]+', line[1].strip())[1:])
                value = ' '.join(split(r'[ ]+', line[2].strip())).split("\\")
                d.update({key: value if len(value) > 1 else value[0]})
    f.close()
    return d
