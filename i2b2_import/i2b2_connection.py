from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import orm
from sqlalchemy.sql import functions as sql_func

from datetime import datetime

from airflow import configuration


class Connection:

    def __init__(self, db_url=None):
        if db_url is None:
            db_url = configuration.get('data-factory', 'I2B2_SQL_ALCHEMY_CONN')

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
            return 1

    def new_encounter_num(self):
        try:
            return self.db_session.query(sql_func.max(self.EncounterMapping.encounter_num).label('max')).one().max + 1
        except TypeError:
            return 1

    def new_text_search_index(self):
        try:
            return self.db_session.query(
                sql_func.max(self.ObservationFact.text_search_index).label('max')).one().max + 1
        except TypeError:
            return 1

    def get_patient_num(self, patient_ide, patient_ide_source, project_id):
        patient_ide = str(patient_ide)
        patient = self.db_session.query(self.PatientMapping).filter_by(
            patient_ide_source=patient_ide_source, patient_ide=patient_ide, project_id=project_id).first()
        if not patient:
            patient = self.PatientMapping(patient_ide_source=patient_ide_source, patient_ide=patient_ide,
                                          project_id=project_id, patient_num=self.new_patient_num())
            self.db_session.merge(patient)
            self.db_session.commit()
        return patient.patient_num

    def get_encounter_num(self, encounter_ide, encounter_ide_source, project_id, patient_ide, patient_ide_source):
        encounter_ide = str(encounter_ide)
        visit = self.db_session.query(self.EncounterMapping).filter_by(
            encounter_ide_source=encounter_ide_source, encounter_ide=encounter_ide, project_id=project_id,
            patient_ide=patient_ide, patient_ide_source=patient_ide_source).first()
        if not visit:
            visit = self.EncounterMapping(encounter_ide_source=encounter_ide_source, encounter_ide=encounter_ide,
                                          project_id=project_id, patient_ide=patient_ide,
                                          patient_ide_source=patient_ide_source,
                                          encounter_num=self.new_encounter_num())
            self.db_session.merge(visit)
            self.db_session.commit()
        return visit.encounter_num

    def save_observation(self, encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd, tval_char,
                         nval_num):
        observation = self.db_session.query(self.ObservationFact) \
            .filter_by(encounter_num=encounter_num, concept_cd=concept_cd, provider_id=provider_id,
                       start_date=start_date,
                       patient_num=patient_num) \
            .first()
        if not observation:
            observation = self.ObservationFact(
                encounter_num=encounter_num, concept_cd=concept_cd, provider_id=provider_id, start_date=start_date,
                patient_num=patient_num, valtype_cd=valtype_cd,
                tval_char=tval_char, nval_num=nval_num, import_date=datetime.now(),
                text_search_index=self.new_text_search_index()
            )
            self.db_session.merge(observation)
            self.db_session.commit()
        else:
            if valtype_cd not in [None, '', observation.valtype_cd]:
                observation.valtype_cd = valtype_cd
                observation.update_date = datetime.now()
                self.db_session.commit()
            if tval_char not in [None, '', observation.tval_char]:
                observation.tval_char = tval_char
                observation.update_date = datetime.now()
                self.db_session.commit()
            if nval_num not in [None, observation.nval_num]:
                observation.nval_num = nval_num
                observation.update_date = datetime.now()
                self.db_session.commit()

    def save_patient(self, patient_num, sex_cd=None, birth_date=None):
        patient = self.db_session.query(self.PatientDimension) \
            .filter_by(patient_num=patient_num) \
            .first()
        if not patient:
            patient = self.PatientDimension(
                patient_num=patient_num, sex_cd=sex_cd, birth_date=birth_date,
                import_date=datetime.now()
            )
            self.db_session.merge(patient)
            self.db_session.commit()
        else:
            if sex_cd not in [None, '', patient.sex_cd]:
                patient.sex_cd = sex_cd
                patient.update_date = datetime.now()
                self.db_session.commit()
            if birth_date not in [None, '', patient.birth_date]:
                patient.birth_date = birth_date
                patient.update_date = datetime.now()
                self.db_session.commit()

    def save_visit(self, encounter_num, patient_num, patient_age=None, start_date=None, location_cd=None):
        visit = self.db_session.query(self.VisitDimension) \
            .filter_by(encounter_num=encounter_num, patient_num=patient_num) \
            .first()
        if not visit:
            visit = self.VisitDimension(
                encounter_num=encounter_num, patient_num=patient_num, patient_age=patient_age, start_date=start_date,
                location_cd=location_cd, import_date=datetime.now()
            )
            self.db_session.merge(visit)
            self.db_session.commit()
        elif start_date not in [None, visit.start_date]:
            visit.start_date = start_date
            visit.update_date = datetime.now()
            self.db_session.commit()
        elif patient_age not in [None, visit.patient_age]:
            visit.patient_age = patient_age
            visit.update_date = datetime.now()
            self.db_session.commit()

    def save_concept(self, concept_path, concept_cd=None, concept_fullname=None):
        concept = self.db_session.query(self.ConceptDimension) \
            .filter_by(concept_path=concept_path) \
            .first()
        if not concept:
            concept = self.ConceptDimension(
                concept_path=concept_path, concept_cd=concept_cd, name_char=concept_fullname,
                import_date=datetime.now()
            )
            self.db_session.merge(concept)
            self.db_session.commit()
        else:
            if concept_cd not in [None,  '', concept.concept_cd]:
                concept.concept_cd = concept_cd
                concept.update_date = datetime.now()
                self.db_session.commit()
            if concept_fullname not in [None,  '', concept.name_char]:
                concept.name_char = concept_fullname
                concept.update_date = datetime.now()
                self.db_session.commit()

    def get_visit(self, encounter_num, patient_num):
        return self.db_session.query(self.VisitDimension) \
            .filter_by(encounter_num=encounter_num, patient_num=patient_num) \
            .first()
