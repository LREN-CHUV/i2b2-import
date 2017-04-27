import logging
from glob import iglob
from os import path

from . import ppmi_extension
from . import edsd_extension
from . import clm_extension
from . import i2b2_connection


#######################################################################################################################
# PUBLIC FUNCTIONS
#######################################################################################################################


def meta2i2b2(file_path, i2b2_db_url, dataset):
    """
    Import meta-data from a file into the I2B2 schema.
    :param file_path: File (XML, JSON, ...) containing meta-data for a given dataset (PPMI, EDSD, ...).
    :param i2b2_db_url: URL of the I2B2 DB.
    :param dataset: Dataset ID (each dataset uses its own meta-data files format)
    :return:
    """

    logging.info("Connecting to database...")
    i2b2_conn = i2b2_connection.Connection(i2b2_db_url)

    if dataset.upper() == 'PPMI':
        ppmi_extension.xml2i2b2(file_path, i2b2_conn)
    elif dataset.upper() == 'EDSD':
        edsd_extension.txt2i2b2(file_path, i2b2_conn)
    elif dataset.upper() == 'CLM':
        clm_extension.xlsx2i2b2(file_path, i2b2_conn)
    else:
        logging.info("No implementation for this dataset !")

    i2b2_conn.close()


def folder2db(folder, i2b2_db_url, dataset):
    """
    Import meta-data from files from a given folder (recursive) and for a given dataset into the I2B2 schema.
    :param folder: Folder containing meta-data files for a given dataset.
    :param i2b2_db_url: URL of the I2B2 DB.
    :param dataset: Dataset ID (each dataset uses its own meta-data files format)
    :return:
    """

    if dataset.upper() == 'PPMI':
        file_extension = '.xml'
    elif dataset.upper() == 'EDSD':
        file_extension = '.txt'
    elif dataset.upper() == 'CLM':
        file_extension = '.xlsx'
    else:
        logging.info("No implementation for this dataset !")
        return None

    for file_path in iglob(path.join(folder, "**/*" + file_extension), recursive=True):
        meta2i2b2(file_path, i2b2_db_url, dataset)
