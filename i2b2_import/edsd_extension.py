from re import split

from . import utils


DATASET = 'EDSD'


def txt2i2b2(file_path, i2b2_conn):
    info = _extract_info(file_path)
    patient_ide = info['PatientName']  # Sometimes the patient ID is stored in PatientName field for EDSD
    patient_sex = info['PatientSex']
    patient_age = utils.compute_age_years(int(info['PatientAge'][:-1]), info['PatientAge'][-1])
    study_id = info['StudyId']
    visit_ide = patient_ide + '_' + study_id
    acq_date = utils.datetime_from_dcm_date(info['AcquisitionDate'])

    encounter_num = i2b2_conn.get_encounter_num(visit_ide, DATASET, DATASET, patient_ide, DATASET)
    patient_num = i2b2_conn.get_patient_num(patient_ide, DATASET, DATASET)

    i2b2_conn.save_visit(encounter_num, patient_num, patient_age, acq_date)
    i2b2_conn.save_patient(patient_num, patient_sex)

    # TODO: Complete it ! E.g. save sequence info, etc.


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
