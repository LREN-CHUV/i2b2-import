import logging

from datetime import datetime
from os.path import join

from pandas import read_excel
from pandas import notnull

from . import utils


DATASET = 'clm'
SITE = 'clm'
DEFAULT_DATE = datetime(1, 1, 1)

SEQ_PATH_PREFIX = 'Imaging Data/Acquisition Settings'

PROTOCOLS = [
    "t1_mprage_sag GD",
    "mprage_morpho_wip900_AA",
    "t1_mprage_morpho_wip900B_AA",
    "t1_mprage_morpho_wip900B",
    "T1 MPRAGE morpho sag 32 canaux @ wip",
    "mprage_morpho_wip542f_32ch",
    "t1_mprage_morpho_wip900_32ch",
    "t1_mprage_morpho_900_32ch",
    "T1 MPRAGE morpho sag 16 canaux @ wip",
    "mprage_morpho_wip900B_AA",
    "mprage_morpho_wip900B_AA_64cx",
    "mprage_morpho_wip822_32ch",
    "t1_mprage_morpho_wip900",
    "T1 MPRAGE morpho 32 cx wip806",
    "mprage_900B_morpho",
    "mprage_morpho_wip822B_32ch",
    "T1 MPRAGE morpho 32 cx wip806 @@@@@",
    "mprage_morpho_wip822_16ch",
    "mprage_morpho_wip900_32ch",
    "t1_mprage_morpho_wip900_12ch",
    "t1_mprage_morpho_900_64ch",
    "mprage_morpho_wip542g_32ch",
    "mprage_morpho_wip900_12ch"
]

KEY_COLUMNS = ['CLM_R_CODE', 'ID_EVENT', 'ProtocolName']

CHECK_FINITE_COLUMN = 'MagneticFieldStrength'

ACQUISITION_SETTINGS = [
    'ProtocolName',
    'Manufacturer',
    'ManufacturerModelName',
    'MagneticFieldStrength',
    'FlipAngle',
    'Columns',
    'Rows',
    'EchoTrainLength',
    'EchoTime',
    'PercentPhaseFieldOfView',
    'NumberOfPhaseEncodingSteps',
    'RepetitionTime',
    'PercentSampling',
    'SliceThickness',
    'PixelBandwidth'
]


def xlsx2i2b2(file_path, i2b2_conn):

    logging.info("reading...")
    df = read_excel(file_path)

    logging.info("filtering by protocol name...")
    df = df[df["ProtocolName"].isin(PROTOCOLS)]

    logging.info("removing useless rows...")
    df.drop_duplicates(subset=KEY_COLUMNS, inplace=True)

    logging.info("discarding rows containing not enough information...")
    df = df[notnull(df[CHECK_FINITE_COLUMN])]

    logging.info("storing metadata to I2B2 database...")

    for _, row in df.iterrows():
        patient_num = i2b2_conn.get_patient_num(row['CLM_R_CODE'], DATASET, DATASET)
        i2b2_conn.save_patient(patient_num)

        encounter_num = i2b2_conn.get_encounter_num(row['ID_EVENT'], DATASET, DATASET, row['CLM_R_CODE'], DATASET)
        i2b2_conn.save_visit(encounter_num, patient_num, location_cd=SITE)

        for setting in ACQUISITION_SETTINGS:
            _save_acquisition_setting(i2b2_conn, setting, row[setting], encounter_num, patient_num)


def _save_acquisition_setting(i2b2_conn, setting, value, encounter_num, patient_num):
    concept_cd = DATASET + ':' + setting
    concept_path = join("/", DATASET, SEQ_PATH_PREFIX, setting)
    if value:
        valtype_cd = utils.find_type(value)
        if valtype_cd == 'N':
            tval_char = 'E'
            nval_num = float(value)
        else:
            tval_char = value
            nval_num = None
        i2b2_conn.save_concept(concept_path, concept_cd)
        i2b2_conn.save_observation(encounter_num, concept_cd, DATASET, DEFAULT_DATE, patient_num, valtype_cd,
                                   tval_char, nval_num)
