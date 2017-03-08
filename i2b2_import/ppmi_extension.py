from defusedxml import ElementTree
from math import floor
from datetime import datetime

from . import utils


########################################################################################################################
# SETTINGS
########################################################################################################################

DEFAULT_DATE = datetime(1, 1, 1)


########################################################################################################################
# PUBLIC FUNCTIONS
########################################################################################################################

def xml2i2b2(xml_file, db_conn):
    tree = ElementTree.parse(xml_file)
    project_id = tree.find('./project/projectIdentifier').text
    ide_source = project_id
    site = tree.find('./project/siteKey').text
    subject_id = tree.find('./project/subject/subjectIdentifier').text
    subject_sex = tree.find('./project/subject/subjectSex').text
    study_id = tree.find('./project/subject/study/studyIdentifier').text
    subject_age = tree.find('./project/subject/study/subjectAge').text
    age_qualifier = tree.find('./project/subject/study/ageQualifier').text
    subject_age_years = utils.compute_age_years(subject_age, age_qualifier)
    subject_age_years = int(floor(subject_age_years)) + 1  # I2B2 uses an integer value for age
    try:
        acquisition_date = datetime.strptime(
            tree.find('./project/subject/study/series/dateAcquired').text, '%Y-%m-%d %H:%M:%S.%f')
    except TypeError:
        acquisition_date = DEFAULT_DATE
    protocols = tree.findall('./project/subject/study/series/imagingProtocol/protocolTerm/protocol')

    patient_num = db_conn.get_patient_num(subject_id, ide_source, project_id)
    db_conn.save_patient(patient_num, subject_sex, subject_age_years)

    encounter_num = db_conn.get_encounter_num(study_id, ide_source, project_id, subject_id, ide_source)
    db_conn.save_visit(encounter_num, patient_num, acquisition_date, site)

    for protocol in protocols:
        concept_cd = protocol.attrib['term']
        concept_path = "/sequence/" + concept_cd
        val = protocol.text
        if val:
            valtype_cd = utils.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            db_conn.save_concept(concept_path, concept_cd)
            db_conn.save_observation(encounter_num, concept_cd, ide_source, acquisition_date, patient_num, valtype_cd,
                                     tval_char, nval_num)