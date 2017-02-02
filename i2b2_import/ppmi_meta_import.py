import datetime
import logging
from i2b2_import.meta_import import MetaImport
from defusedxml import ElementTree


DEFAULT_DATE = datetime.datetime(1, 1, 1)


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
        project_id = tree.find('./project/projectIdentifier')
        project_descr = tree.find('./project/projectDescription')
        site = tree.find('./project/siteKey')
        subject_id = tree.find('./project/subject/subjectIdentifier')
        subject_sex = tree.find('./project/subject/subjectSex')
        visit_type = tree.find('./project/subject/visit/visitIdentifier')
        study_id = tree.find('./project/subject/study/studyIdentifier')
        subject_age = tree.find('./project/subject/study/subjectAge')
        age_qualifier = tree.find('./project/subject/study/ageQualifier')
        subject_age_years = _compute_age_years(subject_age, age_qualifier)
        post_mortem = tree.find('./project/subject/study/postMortem')
        series_id = tree.find('./project/subject/study/series/seriesIdentifier')
        try:
            acquisition_date = datetime.datetime.strptime(
                tree.find('./project/subject/study/series/dateAcquired'), '%Y-%m-%d %H:%M:%S.%f')
        except TypeError:
            acquisition_date = DEFAULT_DATE
        image_uid = tree.find('./project/subject/study/series/imagingProtocol/imageUID')
        image_descr = tree.find('./project/subject/study/series/imagingProtocol/description')
        protocol = tree.findall('./project/subject/study/series/imagingProtocol/protocolTerm/protocol')


########################################################################################################################
# PRIVATE FUNCTIONS
########################################################################################################################

def _compute_age_years(subject_age, age_qualifier):
    if 'Y' == str(age_qualifier).upper():
        return subject_age
    elif 'M' == str(age_qualifier).upper():
        return 0.0833334 * subject_age
    elif 'W' == str(age_qualifier).upper():
        return 0.0191781 * subject_age
    elif 'D' == str(age_qualifier).upper():
        return 0.00273973 * subject_age
    else:
        return None
