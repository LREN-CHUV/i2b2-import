import re
from pandas import DataFrame
from datetime import datetime
from glob import iglob
from os import path
from . import utils


########################################################################################################################
# SETTINGS
########################################################################################################################

STRUCTURE_NAMES_COL = 'Structure Names'
CONCEPT_PATH_PREFIX = '/Imaging Data/Features/Brain'
DEFAULT_DATE = datetime(1, 1, 1)


########################################################################################################################
# PUBLIC FUNCTIONS
########################################################################################################################

def csv2db(file_path, i2b2_conn, dataset, config=None):
    """
    Import brain features and other observation facts data from a CSV file into the I2B2 DB schema.
    :param file_path: Path to the CSV file.
    :param i2b2_conn: Connection to the I2B2 DB.
    :param dataset: Data set name.
    :param config: A few settings. It is a dictionary that accepts the following fields:
        - pid_in_vid: Rarely, a data set might mix patient IDs and visit IDs. E.g. : LREN data. In such a case, you
        to enable this flag. This will try to split PatientID into VisitID and PatientID.
        - sid_by_patient: Rarely, a data set might use study IDs which are unique by patient (not for the whole study).
        E.g.: LREN data. In such a case, you have to enable this flag. This will use PatientID + StudyID as a sessionID.
    :return:
    """
    try:
        pid_in_vid = config['pid_in_vid']
    except (KeyError, TypeError):
        pid_in_vid = False
    try:
        sid_by_patient = config['sid_by_patient']
    except (KeyError, TypeError):
        sid_by_patient = False

    patient_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
    encounter_ide = None

    if pid_in_vid:
        try:
            encounter_ide, patient_ide = utils.split_patient_id(patient_ide)
        except TypeError:
            encounter_ide = None
    if not pid_in_vid or not encounter_ide:
        try:
            encounter_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
            if sid_by_patient:  # If the Study ID is given at the patient level (e.g. LREN data), here is a little trick
                encounter_ide = patient_ide + "_" + encounter_ide
        except AttributeError:
            encounter_ide = None

    provider_id = dataset
    patient_ide_source = dataset
    encounter_ide_source = dataset
    project_id = dataset

    df = DataFrame.from_csv(file_path, index_col=None)
    column_headers = list(df)
    concept_columns = set(column_headers) - set(STRUCTURE_NAMES_COL)

    for row in df.iterrows():
        row = row[1]  # (index, row) -> row
        struct_name = row[STRUCTURE_NAMES_COL]
        for concept_postfix in concept_columns:
            concept_cd = struct_name[:20] + "_" + concept_postfix[:20]
            concept_path = path.join(CONCEPT_PATH_PREFIX, struct_name, concept_postfix)
            val = row[concept_postfix]
            valtype_cd = utils.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None

            i2b2_conn.save_concept(concept_path, concept_cd)
            patient_num = i2b2_conn.get_patient_num(patient_ide, patient_ide_source, project_id)
            encounter_num = i2b2_conn.get_encounter_num(encounter_ide, encounter_ide_source, project_id,
                                                        patient_ide, patient_ide_source)
            visit = i2b2_conn.get_visit(encounter_num, patient_num)
            try:
                start_date = visit.start_date
                if not start_date:
                    raise AttributeError
            except AttributeError:
                start_date = DEFAULT_DATE
            i2b2_conn.save_observation(encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd,
                                       tval_char, nval_num)


def folder2db(folder, i2b2_conn, dataset, config=None):
    """
    Import brain features and other observation facts data from a folder containing CSV files into the I2B2 DB schema.
    :param folder: Folder path
    :param i2b2_conn: Connection to the I2B2 DB.
    :param dataset: Data set name.
    :param config: A few settings. It is a dictionary that accepts the following fields:
        - pid_in_vid: Rarely, a data set might mix patient IDs and visit IDs. E.g. : LREN data. In such a case, you
        to enable this flag. This will try to split PatientID into VisitID and PatientID.
        - sid_by_patient: Rarely, a data set might use study IDs which are unique by patient (not for the whole study).
        E.g.: LREN data. In such a case, you have to enable this flag. This will use PatientID + StudyID as a sessionID.
    :return:
    """
    for file_path in iglob(path.join(folder, "**/*.csv"), recursive=True):
        csv2db(file_path, i2b2_conn, dataset, config)
