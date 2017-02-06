# coding: utf-8

"""
This schema is based on the SQL script available here:
https://github.com/i2b2/i2b2-data/blob/master/edu.harvard.i2b2.data/Release_1-7/NewInstall/Crcdata/scripts/crc_create_datamart_postgresql.sql
For more information, you can refer to this document:
https://www.i2b2.org/software/files/PDF/current/CRC_Design.pdf
"""

from sqlalchemy import Column, INTEGER, TEXT, DECIMAL, TIMESTAMP, VARCHAR, CHAR
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


########################################################################################################################
# DATA TABLES
########################################################################################################################

class ObservationFact(Base):
    __tablename__ = 'observation_fact'

    encounter_num = Column(INTEGER, primary_key=True)
    concept_cd = Column(VARCHAR(50), primary_key=True)
    provider_id = Column(VARCHAR(50), primary_key=True)
    start_date = Column(TIMESTAMP, primary_key=True)
    patient_num = Column(INTEGER, primary_key=True)
    modifier_cd = Column(CHAR(50), primary_key=True, server_default='@')
    instance_num = Column(INTEGER, primary_key=True, server_default='1')
    valtype_cd = Column(CHAR(50))
    tval_char = Column(VARCHAR(255))
    nval_num = Column(DECIMAL(18, 5))
    valueflag_cd = Column(CHAR(50))
    quantity_num = Column(DECIMAL(18, 5))
    units_cd = Column(VARCHAR(50))
    end_date = Column(TIMESTAMP)
    location_cd = Column(VARCHAR(50))
    observation_blob = Column(TEXT)
    confidence_num = Column(DECIMAL(18, 5))
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class PatientDimension(Base):
    __tablename__ = 'patient_dimension'

    patient_num = Column(INTEGER, primary_key=True)
    vital_status_cd = Column(VARCHAR(50))
    birth_date = Column(TIMESTAMP)
    death_date = Column(TIMESTAMP)
    sex_cd = Column(CHAR(50))
    age_in_years_num = Column(INTEGER)
    language_cd = Column(VARCHAR(50))
    race_cd = Column(VARCHAR(50))
    marital_status_cd = Column(VARCHAR(50))
    religion_cd = Column(VARCHAR(50))
    zip_cd = Column(VARCHAR(10))
    statecityzip_path = Column(VARCHAR(700))
    income_cd = Column(VARCHAR(50))
    patient_blob = Column(TEXT)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class VisitDimension(Base):
    __tablename__ = 'visit_dimension'

    encounter_num = Column(INTEGER, primary_key=True)
    patient_num = Column(INTEGER, primary_key=True)
    active_status_cd = Column(VARCHAR(50))
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    inout_cd = Column(VARCHAR(50))
    location_cd = Column(VARCHAR(50))
    location_path = Column(VARCHAR(900))
    length_if_stay = Column(INTEGER)
    visit_blob = Column(TEXT)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


########################################################################################################################
# LOOKUP TABLES
########################################################################################################################

class ConceptDimension(Base):
    __tablename__ = 'concept_dimension'

    concept_path = Column(VARCHAR(700), primary_key=True)
    concept_cd = Column(VARCHAR(50))
    name_char = Column(VARCHAR(2000))
    concept_blob = Column(TEXT)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class ProviderDimension(Base):
    __tablename__ = 'provider_dimension'

    provider_id = Column(VARCHAR(50), primary_key=True)
    provider_path = Column(VARCHAR(700), primary_key=True)
    name_char = Column(VARCHAR(850))
    provider_blob = Column(TEXT)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class ModifierDimension(Base):
    __tablename__ = 'modifier_dimension'

    concept_path = Column(VARCHAR(700), primary_key=True)
    concept_cd = Column(VARCHAR(50))
    name_char = Column(VARCHAR(2000))
    modifier_blob = Column(TEXT)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class CodeLookup(Base):
    __tablename__ = 'code_lookup'

    table_cd = Column(VARCHAR(100), primary_key=True)
    column_cd = Column(VARCHAR(100), primary_key=True)
    code_cd = Column(VARCHAR(50), primary_key=True)
    name_char = Column(VARCHAR(650))
    lookup_blob = Column(TEXT)
    upload_date = Column(TIMESTAMP)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


########################################################################################################################
# MAPPING TABLES
########################################################################################################################

class PatientMapping(Base):
    __tablename__ = 'patient_mapping'

    patient_ide = Column(VARCHAR(200), primary_key=True)
    patient_ide_source = Column(VARCHAR(50), primary_key=True)
    patient_num = Column(INTEGER, unique=True)
    patient_ide_status = Column(VARCHAR(50))
    project_id = Column(VARCHAR(50), primary_key=True)
    upload_date = Column(TIMESTAMP)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)


class EncounterMapping(Base):
    __tablename__ = 'encounter_mapping'

    encounter_ide = Column(VARCHAR(200), primary_key=True)
    encounter_ide_source = Column(VARCHAR(50), primary_key=True)
    project_id = Column(VARCHAR(50), primary_key=True)
    encounter_num = Column(INTEGER, nullable=False)
    patient_ide = Column(VARCHAR(200), primary_key=True)
    patient_ide_source = Column(VARCHAR(50), primary_key=True)
    encounter_ide_status = Column(VARCHAR(50))
    upload_date = Column(TIMESTAMP)
    update_date = Column(TIMESTAMP)
    download_date = Column(TIMESTAMP)
    import_date = Column(TIMESTAMP)
    sourcesystem_cd = Column(VARCHAR(50))
    upload_id = Column(INTEGER)
