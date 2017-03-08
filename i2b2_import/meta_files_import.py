from glob import iglob
from os import path

from . import ppmi_extension


########################################################################################################################
# PUBLIC FUNCTIONS
########################################################################################################################


def meta2i2b2(file_path, db_conn, dataset):
    """
    Import meta-data from a file into the I2B2 schema.
    :param file_path: File (XML, JSON, ...) containing meta-data for a given dataset (PPMI, EDSD, ...).
    :param db_conn: Connection to the I2B2 DB.
    :param dataset: Dataset ID (each dataset uses its own meta-data files format)
    :return:
    """
    if dataset.upper() == 'PPMI':
        ppmi_extension.xml2i2b2(file_path, db_conn)


def folder2db(folder, db_conn, dataset):
    """
    Import meta-data from files from a given folder (recursive) and for a given dataset into the I2B2 schema.
    :param folder: Folder containing meta-data files for a given dataset.
    :param db_conn: Connection to the I2B2 DB.
    :param dataset: Dataset ID (each dataset uses its own meta-data files format)
    :return:
    """
    file_extension = ''
    if dataset.upper() == 'PPMI':
        file_extension = '.xml'

    for file_path in iglob(path.join(folder, "**/*" + file_extension), recursive=True):
        meta2i2b2(file_path, db_conn, dataset)
