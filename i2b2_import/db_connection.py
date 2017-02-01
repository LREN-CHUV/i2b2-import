from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import orm
from sqlalchemy.sql import functions as sql_func

from airflow import configuration


class Connection:

    def __init__(self, db_url=None):
        if db_url is None:
            db_url = configuration.get('mri', 'SQL_ALCHEMY_CONN')

        self.Base = automap_base()
        self.engine = create_engine(db_url)
        self.Base.prepare(self.engine, reflect=True)

        self.ObservationFact = self.Base.classes.observation_fact
        self.PatientDimension = self.Base.classes.patient_dimension
        self.VisitDimension = self.Base.classes.visit_dimension
        self.ConceptDimension = self.Base.classes.concept_dimension
        self.ProviderDimension = self.Base.classes.provider_dimension
        self.ModifierDimension = self.Base.classes.modifier_dimension
        self.CodeLookup = self.Base.classes.code_lookup
        self.PatientMapping = self.Base.classes.patient_mapping
        self.EncounterMapping = self.Base.classes.encounter_mapping

        self.db_session = orm.Session(self.engine)

    def close(self):
        self.db_session.close()

    def new_patient_num(self):
        try:
            return self.db_session.query(sql_func.max(self.PatientMapping.patient_num).label('max')).one().max + 1
        except TypeError:
            return 0

    def new_encounter_num(self):
        try:
            return self.db_session.query(sql_func.max(self.EncounterMapping.encounter_num).label('max')).one().max + 1
        except TypeError:
            return 0
