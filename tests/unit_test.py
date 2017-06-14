import logging
import os

from nose.tools import assert_greater_equal
from sqlalchemy.exc import IntegrityError

from i2b2_import import i2b2_connection
from i2b2_import import data_catalog_connection
from i2b2_import import features_csv_import
from i2b2_import import meta_files_import
from i2b2_import import data_catalog_import


if 'DATA_CATALOG_DB_URL' in os.environ:
    DATA_CATALOG_DB_URL = os.environ['DATA_CATALOG_DB_URL']
else:
    DATA_CATALOG_DB_URL = 'postgresql://postgres:postgres@localhost:5433/postgres'

if 'I2B2_DB_URL' in os.environ:
    I2B2_DB_URL = os.environ['I2B2_DB_URL']
else:
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

    def test_01_ppmi_xml_import(self):
        meta_files_import.meta2i2b2('./data/ppmi_meta/ppmi.xml', I2B2_DB_URL, 'PPMI')
        meta_files_import.meta2i2b2('./data/ppmi_meta/ppmi2.xml', I2B2_DB_URL, 'PPMI')
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 36)

    def test_02_clm_xlsx_import(self):
        meta_files_import.meta2i2b2('./data/clm_meta/clm.xlsx', I2B2_DB_URL, 'CLM')
        # TODO: add assertion here

    def test_03_data_catalog_import(self):
        try:
            with open('./data/sql/test.sql', 'r') as sql_file:
                self.dcdb_conn.engine.execute(sql_file.read())
        except IntegrityError:
            logging.warning("Cannot populate DB")
        data_catalog_import.catalog2i2b2(DATA_CATALOG_DB_URL, I2B2_DB_URL)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 36)

    def test_04_brain_features_import(self):
        features_csv_import.csv2db(
            './data/features/PR00003/01/mt_al_mtflash3d_v2l_1mm/05/'
            'PR00003_Neuromorphics_Vols_MPMs_global_std_values.csv', I2B2_DB_URL, 'PPMI')
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 324)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ConceptDimension).count(), 324)
