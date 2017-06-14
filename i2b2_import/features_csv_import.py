import logging
import re
from pandas import DataFrame
from pandas import read_csv
from pandas.io.common import EmptyDataError
from os import path
from . import recurse_in_dir_and_apply_fn
from . import utils
from . import i2b2_connection


#######################################################################################################################
# SETTINGS
#######################################################################################################################

STRUCTURE_NAMES_COL = 'Structure Names'
CONCEPT_PATH_PREFIX = 'Imaging Data/Features/Brain'

# Get default data from package folder
pkg_dir, _ = path.split(__file__)
DEFAULT_MAPPING_FILE = path.join(pkg_dir, "default_data", "default_structures_mapping.csv")


#######################################################################################################################
# PUBLIC FUNCTIONS
#######################################################################################################################

def csv2db(file_path, i2b2_db_url, dataset, config=None, regions_name_file=DEFAULT_MAPPING_FILE):
    """
    Import brain features and other observation facts data from a CSV file into the I2B2 DB schema.
    :param file_path: Path to the CSV file.
    :param i2b2_db_url: URL of the I2B2 DB.
    :param dataset: Data set name.
    :param config: List of flags:
        - boost: (optional) When enabled, we consider that all the files from a same folder share the same meta-data.
        When enabled, the processing is (about 2 times) faster. This option is enabled by default.
        - session_id_by_patient: Rarely, a data set might use study IDs which are unique by patient (not for the whole
        study).
        E.g.: LREN data. In such a case, you have to enable this flag. This will use PatientID + StudyID as a session
        ID.
        - visit_id_in_patient_id: Rarely, a data set might mix patient IDs and visit IDs. E.g. : LREN data. In such a
        case, you have to enable this flag. This will try to split PatientID into VisitID and PatientID.
        - visit_id_from_path: Enable this flag to get the visit ID from the folder hierarchy instead of DICOM meta-data
        (e.g. can be useful for PPMI).
        - repetition_from_path: Enable this flag to get the repetition ID from the folder hierarchy instead of DICOM
        meta-data (e.g. can be useful for PPMI).
    :param regions_name_file: CSV file containing the abbreviated regions name in the first column and the full names
        in the second column.
    :return:
    """

    config = config if config else []

    logging.info("Connecting to database...")
    i2b2_conn = i2b2_connection.Connection(i2b2_db_url)

    logging.info("Getting info (subject, visit, etc) from %s" % file_path)
    patient_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
    encounter_ide = None

    if 'visit_id_in_patient_id' in config:
        try:
            encounter_ide, patient_ide = utils.split_patient_id(patient_ide)
        except TypeError:
            encounter_ide = None
    if 'visit_id_in_patient_id' not in config or not encounter_ide:
        try:
            encounter_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
            if 'session_id_by_patient' in config:
                encounter_ide = patient_ide + "_" + encounter_ide
        except AttributeError:
            encounter_ide = None

    provider_id = dataset
    patient_ide_source = dataset
    encounter_ide_source = dataset
    project_id = dataset

    logging.info("Reading data from %s" % file_path)
    try:
        df = DataFrame.from_csv(file_path, index_col=None)
    except EmptyDataError:
        logging.warning("No data found in %s" % file_path)
        df = DataFrame()

    column_headers = list(df)
    concept_columns = set(column_headers) - set(STRUCTURE_NAMES_COL)

    for row in df.iterrows():
        row = row[1]  # (index, row) -> row
        struct_name = row[STRUCTURE_NAMES_COL]
        for concept_postfix in concept_columns:
            concept_fullname = _fullname_from_csv(struct_name, regions_name_file) + " " + concept_postfix
            concept_name = struct_name + " " + concept_postfix
            concept_cd = str(provider_id + ':' + concept_name).rstrip().replace(' ', '_').lower()
            concept_path = path.join("/", provider_id, CONCEPT_PATH_PREFIX, struct_name, concept_postfix)
            val = row[concept_postfix]
            valtype_cd = utils.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None

            i2b2_conn.save_concept(concept_path, concept_cd, concept_fullname)
            patient_num = i2b2_conn.get_patient_num(patient_ide, patient_ide_source, project_id)
            encounter_num = i2b2_conn.get_encounter_num(encounter_ide, encounter_ide_source, project_id, patient_ide,
                                                        patient_ide_source)
            visit = i2b2_conn.get_visit(encounter_num, patient_num)
            try:
                start_date = visit.start_date
                if not start_date:
                    raise AttributeError
            except AttributeError:
                start_date = utils.DEFAULT_DATE
            i2b2_conn.save_observation(encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd,
                                       tval_char, nval_num)
    i2b2_conn.close()
    logging.info("I2B2 database connection closed")


def folder2db(folder, i2b2_db_url, dataset, config=None, regions_name_file=DEFAULT_MAPPING_FILE):
    """
    Import brain features and other observation facts data from a folder containing CSV files into the I2B2 DB schema.
    :param folder: Folder path
    :param i2b2_db_url: URL of the I2B2 DB.
    :param dataset: Data set name.
    :param config: List of flags:
        - boost: (optional) When enabled, we consider that all the files from a same folder share the same meta-data.
        When enabled, the processing is (about 2 times) faster. This option is enabled by default.
        - session_id_by_patient: Rarely, a data set might use study IDs which are unique by patient (not for the whole
        study).
        E.g.: LREN data. In such a case, you have to enable this flag. This will use PatientID + StudyID as a session
        ID.
        - visit_id_in_patient_id: Rarely, a data set might mix patient IDs and visit IDs. E.g. : LREN data. In such a
        case, you have to enable this flag. This will try to split PatientID into VisitID and PatientID.
        - visit_id_from_path: Enable this flag to get the visit ID from the folder hierarchy instead of DICOM meta-data
        (e.g. can be useful for PPMI).
        - repetition_from_path: Enable this flag to get the repetition ID from the folder hierarchy instead of DICOM
        meta-data (e.g. can be useful for PPMI).
    :param regions_name_file: CSV file containing the abbreviated regions name in the first column and the full names
        in the second column.
    :return:
    """
    recurse_in_dir_and_apply_fn(folder, '*.csv',
                                lambda file_path: csv2db(file_path, i2b2_db_url, dataset, config, regions_name_file))


#######################################################################################################################
# PRIVATE FUNCTIONS
#######################################################################################################################

def _fullname_from_csv(struct_name, csv_path):
    try:
        struct_matching = read_csv(csv_path)
        for _, row in struct_matching.iterrows():
            if row[0] == struct_name:
                return row[1]
    except OSError:
        logging.warning("Fullname not found for brain structure %s" % struct_name)
    return ''
