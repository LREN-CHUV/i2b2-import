import sys
import os

from nose.tools import assert_greater_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from i2b2_import import db_connection
from i2b2_import import observationfact_csv_import
from i2b2_import import ppmi_xml_import


DB_URL = 'postgresql://postgres:postgres@localhost:5432/postgres'


class TestPublicFunctions:

    def __init__(self):
        self.i2b2_db_conn = None

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        self.i2b2_db_conn = db_connection.Connection(DB_URL)

    def teardown(self):
        self.i2b2_db_conn.close()

    def test_01_csv2db(self):
        observationfact_csv_import.csv2db('./data/features/adni.csv', self.i2b2_db_conn, 'PPMI')
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 12)

    def test_02_xml2db(self):
        ppmi_xml_import.PPMIXMLImport.meta2i2b2('./data/xml/ppmi.xml', self.i2b2_db_conn)
        assert_greater_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 30)
