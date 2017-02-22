import sys
import os
import logging

from nose.tools import assert_greater_equal
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from i2b2_import import i2b2_connection
from i2b2_import import data_catalog_connection
from i2b2_import import features_csv_import
from i2b2_import import ppmi_xml_import
from i2b2_import import data_catalog_import


DATA_CATALOG_DB_URL = 'postgresql://postgres:postgres@localhost:5433/postgres'
I2B2_DB_URL = 'postgresql://postgres:postgres@localhost:5434/postgres'


class TestPublicFunctions:

    def __init__(self):
        self.i2b2_db_conn = None
        self.dcdb_conn = None

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        self.i2b2_db_conn = i2b2_connection.Connection(I2B2_DB_URL)
        self.dcdb_conn = data_catalog_connection.Connection(DATA_CATALOG_DB_URL)

    def teardown(self):
        self.i2b2_db_conn.close()
        self.dcdb_conn.close()

    def test_01_xml2db(self):
        ppmi_xml_import.meta2i2b2('./data/xml/ppmi.xml', self.i2b2_db_conn)
        ppmi_xml_import.meta2i2b2('./data/xml/ppmi2.xml', self.i2b2_db_conn)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 36)

    def test_02_db2db(self):
        try:
            with open('./data/sql/test.sql', 'r') as sql_file:
                self.dcdb_conn.engine.execute(sql_file.read())
        except IntegrityError:
            logging.warning("Cannot populate DB")
        data_catalog_import.meta2i2b2(self.dcdb_conn, self.i2b2_db_conn)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 36)

    def test_03_csv2db(self):
        features_csv_import.csv2db(
            './data/features/PR00003/01/mt_al_mtflash3d_v2l_1mm/05/'
            'PR00003_Neuromorphics_Vols_MPMs_global_std_values.csv', self.i2b2_db_conn, 'PPMI')
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 1587)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ConceptDimension).count(), 1587)
