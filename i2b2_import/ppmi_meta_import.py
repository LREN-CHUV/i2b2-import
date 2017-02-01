from i2b2_import.meta_import import MetaImport
import logging
from xml.etree import ElementTree


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
        root = ElementTree.parse(source).getroot()
        for project_id in root.findall('projectIdentifier'):
            logging.info(project_id)
