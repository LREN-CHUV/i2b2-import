import re
from pandas import DataFrame
from datetime import datetime
from . import utils


########################################################################################################################
# SETTINGS
########################################################################################################################

STRUCTURE_NAMES_COL = 'Structure Names'
DEFAULT_DATE = datetime(1, 1, 1)


########################################################################################################################
# PUBLIC FUNCTIONS
########################################################################################################################

def csv2db(file_path, db_conn, src):
    """
    Import brain features and other observation facts data from a CSV file into the I2B2 DB schema.
    :param file_path: Path to the CSV file.
    :param db_conn: Connection to the I2B2 DB.
    :param src: Data source (e.g. CHUV, ADNI, PPMI, etc).
    :return:
    """
    patient_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
    encounter_ide = str(re.findall('/([^/]+?)/[^/]+?/[^/]+?/[^/]+?\.csv', file_path)[0])
    provider_id = src
    patient_ide_source = src
    encounter_ide_source = src
    project_id = src
    df = DataFrame.from_csv(file_path, index_col=None)
    column_headers = list(df)
    concept_columns = set(column_headers) - set(STRUCTURE_NAMES_COL)
    for row in df.iterrows():
        row = row[1]  # (index, row) -> row
        struct_name = row[STRUCTURE_NAMES_COL]
        for concept_postfix in concept_columns:
            concept_cd = struct_name[:20] + "_" + concept_postfix[:20]
            concept_path = str(struct_name + "/" + concept_postfix).replace(' ', '')
            val = row[concept_postfix]
            valtype_cd = utils.find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            db_conn.save_concept(concept_path, concept_cd)
            patient_num = db_conn.get_patient_num(patient_ide, patient_ide_source, project_id)
            encounter_num = db_conn.get_encounter_num(encounter_ide, encounter_ide_source, project_id,
                                                      patient_ide, patient_ide_source)
            visit = db_conn.get_visit(encounter_num, patient_num)
            try:
                start_date = visit.start_date
            except AttributeError:
                start_date = DEFAULT_DATE
            db_conn.save_observation(encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd,
                                     tval_char, nval_num)
