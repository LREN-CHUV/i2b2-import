import logging

from pandas import read_excel
from pandas import notnull


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


def xlsx2i2b2(file_path, db_conn):

    logging.info("reading...")
    df = read_excel(file_path)

    logging.info("filtering by protocol name...")
    df = df[df["ProtocolName"].isin(PROTOCOLS)]

    logging.info("removing useless rows...")
    df.drop_duplicates(subset=KEY_COLUMNS, inplace=True)

    logging.info("discarding rows containing not enough information...")
    df = df[notnull(df[CHECK_FINITE_COLUMN])]

    logging.info("exporting to CSV file...")
    df.to_csv('/home/mirco/Bureau/results.csv')
