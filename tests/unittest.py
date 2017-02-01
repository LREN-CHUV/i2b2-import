import sys
import os
import subprocess

from nose.tools import assert_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from i2b2_import import db_connection
from i2b2_import import observation_fact_import


DB_URL = 'postgresql://postgres:postgres@localhost:5432/postgres'


class TestPublicFunctions:

    def __init__(self):
        self.i2b2_db_conn = None

    @classmethod
    def setup_class(cls):
        subprocess.call("./init_db.sh", shell=True)  # Create the DB tables

    @classmethod
    def teardown_class(cls):
        pass

    def setup(self):
        self.i2b2_db_conn = db_connection.Connection(DB_URL)

    def teardown(self):
        self.i2b2_db_conn.close()

    def test_01_csv2db(self):
        observation_fact_import.csv2db('./data/features/adni.csv', self.i2b2_db_conn, 'TEST')
        assert_equal(self.i2b2_db_conn.db_session.query(self.i2b2_db_conn.ObservationFact).count(), 6)
