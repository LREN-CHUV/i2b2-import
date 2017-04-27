from defusedxml import ElementTree
from datetime import datetime
from os.path import join

from . import utils


#######################################################################################################################
# SETTINGS
#######################################################################################################################

DEFAULT_DATE = datetime(1, 1, 1)
SEQ_PATH_PREFIX = 'Imaging Data/Acquisition Settings'


#######################################################################################################################
# PUBLIC FUNCTIONS
#######################################################################################################################

def xml2i2b2(xml_file, i2b2_conn):
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
    try:
        acquisition_date = datetime.strptime(
            tree.find('./project/subject/study/series/dateAcquired').text, '%Y-%m-%d %H:%M:%S.%f')
    except TypeError:
        acquisition_date = DEFAULT_DATE
    protocols = tree.findall('./project/subject/study/series/imagingProtocol/protocolTerm/protocol')

    patient_num = i2b2_conn.get_patient_num(subject_id, ide_source, project_id)
    i2b2_conn.save_patient(patient_num, subject_sex)

    encounter_num = i2b2_conn.get_encounter_num(study_id, ide_source, project_id, subject_id, ide_source)
    i2b2_conn.save_visit(encounter_num, patient_num, subject_age_years, acquisition_date, site)

    for protocol in protocols:
        concept_cd = project_id + ':' + protocol.attrib['term']
        concept_path = join("/", project_id, SEQ_PATH_PREFIX, protocol.attrib['term'])
        val = protocol.text
        if val:
            valtype_cd = utils.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            i2b2_conn.save_concept(concept_path, concept_cd)
            i2b2_conn.save_observation(encounter_num, concept_cd, ide_source, acquisition_date, patient_num,
                                       valtype_cd, tval_char, nval_num)
