from pandas import DataFrame
from datetime import datetime


########################################################################################################################
# SETTINGS
########################################################################################################################

PATIENT_NUM_COL = 'RID'
ENCOUNTER_NUM_COL = 'MRICode'
PROVIDER_ID_COL = 'ORIGPROT'
START_DATE_COL = 'ScanDate'
DIM_COLUMNS = [PATIENT_NUM_COL, ENCOUNTER_NUM_COL, PROVIDER_ID_COL, START_DATE_COL]


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
    patient_ide_source = src
    encounter_ide_source = src
    project_id = src
    df = DataFrame.from_csv(file_path, index_col=None)
    column_headers = list(df)
    concept_columns = set(column_headers) - set(DIM_COLUMNS)
    for row in df.iterrows():
        row = row[1]  # (index, row) -> row
        patient_ide = str(row[PATIENT_NUM_COL])
        encounter_ide = str(row[ENCOUNTER_NUM_COL])
        provider_id = str(row[PROVIDER_ID_COL])
        start_date = _eu_date_to_datime(row[START_DATE_COL])
        for concept_cd in concept_columns:
            val = row[concept_cd]
            valtype_cd = _find_type(val)
            if valtype_cd == 'N':
                tval_char = 'E'
                nval_num = float(val)
            else:
                tval_char = val
                nval_num = None
            patient_num = db_conn.get_patient_num(patient_ide, patient_ide_source, project_id)
            encounter_num = db_conn.get_encounter_num(encounter_ide, encounter_ide_source, project_id,
                                                      patient_ide, patient_ide_source)
            _save_observation(db_conn, encounter_num, concept_cd, provider_id, start_date, patient_num,
                              valtype_cd, tval_char, nval_num)


########################################################################################################################
# PRIVATE FUNCTIONS
########################################################################################################################


def _eu_date_to_datime(d):
    return datetime.strptime(d, "%d.%m.%Y")


def _save_observation(db_conn, encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd,
                      tval_char, nval_num):
    observation = db_conn.db_session.query(db_conn.ObservationFact) \
        .filter_by(encounter_num=encounter_num, concept_cd=concept_cd, provider_id=provider_id, start_date=start_date,
                   patient_num=patient_num) \
        .first()
    if not observation:
        observation = db_conn.ObservationFact(
            encounter_num=encounter_num, concept_cd=concept_cd, provider_id=provider_id, start_date=start_date,
            patient_num=patient_num, valtype_cd=valtype_cd,
            tval_char=tval_char, nval_num=nval_num, import_date=datetime.now()
        )
        db_conn.db_session.add(observation)
        db_conn.db_session.commit()


def _find_type(val):
    try:
        float(val)
        return 'N'
    except ValueError:
        return 'T'
