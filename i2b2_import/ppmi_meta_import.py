import datetime
from defusedxml import ElementTree
from math import floor

from i2b2_import.meta_import import MetaImport


DEFAULT_DATE = datetime.datetime(1, 1, 1)
YEARS_PER_MONTH = 0.0833334
YEARS_PER_WEEK = 0.0191781
YEARS_PER_DAY = 0.00273973
SOURCE_POSTFIX = "_XML"


########################################################################################################################
# PUBLIC FUNCTIONS
########################################################################################################################

class PPMIMetaImport(MetaImport):
    """
    This is an implementation of the MetaImport class.
    It can be used to import meta data from PPMI XML file into the I2B2 schema.
    """
    @staticmethod
    def meta2i2b2(source, db_conn):
        """
        The function that imports meta data from PPMI XML file into the I2B2 schema.
        :param source: XML file containing PPMI meta data.
        :param db_conn: Connection to the I2B2 DB.
        :return:
        """
        tree = ElementTree.parse(source)
        project_id = tree.find('./project/projectIdentifier').text
        ide_source = project_id + SOURCE_POSTFIX
        project_descr = tree.find('./project/projectDescription').text
        site = tree.find('./project/siteKey').text
        subject_id = tree.find('./project/subject/subjectIdentifier').text
        subject_sex = tree.find('./project/subject/subjectSex').text
        visit_type = tree.find('./project/subject/visit/visitIdentifier').text
        study_id = tree.find('./project/subject/study/studyIdentifier').text
        subject_age = tree.find('./project/subject/study/subjectAge').text
        age_qualifier = tree.find('./project/subject/study/ageQualifier').text
        subject_age_years = _compute_age_years(subject_age, age_qualifier)
        subject_age_years = int(floor(subject_age_years)) + 1  # I2B2 uses an integer value for age
        post_mortem = tree.find('./project/subject/study/postMortem').text
        series_id = tree.find('./project/subject/study/series/seriesIdentifier').text
        try:
            acquisition_date = datetime.datetime.strptime(
                tree.find('./project/subject/study/series/dateAcquired').text, '%Y-%m-%d %H:%M:%S.%f')
        except TypeError:
            acquisition_date = DEFAULT_DATE
        image_uid = tree.find('./project/subject/study/series/imagingProtocol/imageUID').text
        image_descr = tree.find('./project/subject/study/series/imagingProtocol/description').text
        protocol = tree.findall('./project/subject/study/series/imagingProtocol/protocolTerm/protocol')[0].text

        patient_num = db_conn.get_patient_num(subject_id, ide_source, project_id)
        _save_patient(db_conn, patient_num, subject_sex, subject_age_years)


########################################################################################################################
# PRIVATE FUNCTIONS
########################################################################################################################

def _compute_age_years(subject_age, age_qualifier):
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


def _save_patient(db_conn, patient_num, sex_cd, age_in_years_num):
    patient = db_conn.db_session.query(db_conn.PatientDimension) \
        .filter_by(patient_num=patient_num) \
        .first()
    if not patient:
        patient = db_conn.PatientDimension(
            patient_num=patient_num, sex_cd=sex_cd, age_in_years_num=age_in_years_num
        )
        db_conn.db_session.add(patient)
        db_conn.db_session.commit()
    else:
        patient.sex_cd = sex_cd
        patient.age_in_years_num = age_in_years_num
        db_conn.db_session.commit()
