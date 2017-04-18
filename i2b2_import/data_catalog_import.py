import logging
from os import path
from datetime import datetime
from . import i2b2_connection
from . import data_catalog_connection


SEQ_PATH_PREFIX = 'Imaging Data/Acquisition Settings'
DEFAULT_DATE = datetime.now()


def catalog2i2b2(data_catalog_url, i2b2_db_url):
    """
    Import meta data from the Data Catalog DB to the I2B2 schema.
    :param data_catalog_url: URL of the Data Catalog DB.
    :param i2b2_db_url: URL of the I2B2 DB.
    :return:
    """

    logging.info("Connecting to (i2b2) database...")
    i2b2_conn = i2b2_connection.Connection(i2b2_db_url)

    logging.info("Connecting to (data-catalog) database...")
    data_catalog_conn = data_catalog_connection.Connection(data_catalog_url)

    sequences = data_catalog_conn.db_session.query(data_catalog_conn.Sequence).all()
    for seq in sequences:
        visit_id = data_catalog_conn.db_session.query(data_catalog_conn.Session)\
            .filter_by(id=seq.session_id).one_or_none().visit_id
        visit = data_catalog_conn.db_session.query(data_catalog_conn.Visit).filter_by(id=visit_id).one_or_none()
        visit_date = visit.date
        try:
            visit_age = visit.patient_age
        except AttributeError:
            visit_age = None

        participant = data_catalog_conn.db_session.query(data_catalog_conn.Participant)\
            .filter_by(id=visit.participant_id).one_or_none()
        patient_id = participant.id
        sex_cd = participant.gender
        try:
            birth_date = participant.birth_date
        except AttributeError:
            birth_date = None

        visit_ide, dataset = data_catalog_conn.get_visit_map(visit_id)
        patient_ide, dataset = data_catalog_conn.get_patient_map(patient_id)

        encounter_num = i2b2_conn.get_encounter_num(visit_ide, dataset, dataset, patient_ide, dataset)
        patient_num = i2b2_conn.get_patient_num(patient_ide, dataset, dataset)

        i2b2_conn.save_visit(encounter_num, patient_num, visit_age, visit_date)
        i2b2_conn.save_patient(patient_num, sex_cd, birth_date)

        seq_type = data_catalog_conn.db_session.query(data_catalog_conn.SequenceType)\
            .filter_by(id=seq.sequence_type_id).one_or_none()
        start_date = visit_date if visit_date else DEFAULT_DATE
        provider_id = dataset
        _save_sequence(i2b2_conn, seq, seq_type, encounter_num, patient_num, start_date, provider_id)

    data_catalog_conn.close()
    i2b2_conn.close()


def _save_sequence(i2b2_conn, seq, seq_type, encounter_num, patient_num, start_date, provider_id):
    # save sequence name
    concept_path = path.join("/", provider_id, SEQ_PATH_PREFIX, 'name')
    concept_cd = provider_id + ':protocol_name'
    valtype_cd = 'T'
    tval_char = seq.name
    nval_num = None
    i2b2_conn.save_concept(concept_path, concept_cd)
    i2b2_conn.save_observation(encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd, tval_char,
                               nval_num)

    if seq_type:
        seq_param_list = [
            {'name': 'manufacturer', 'type': 'T', 'value': seq_type.manufacturer},
            {'name': 'magnetic_field_strength', 'type': 'N', 'value': seq_type.magnetic_field_strength},
            {'name': 'institution_name', 'type': 'T', 'value': seq_type.institution_name},
            {'name': 'slice_thickness', 'type': 'N', 'value': seq_type.slice_thickness},
            {'name': 'repetition_time', 'type': 'N', 'value': seq_type.repetition_time},
            {'name': 'echo_time', 'type': 'N', 'value': seq_type.echo_time},
            {'name': 'echo_number', 'type': 'N', 'value': seq_type.echo_number},
            {'name': 'number_of_phase_encoding_steps', 'type': 'N', 'value': seq_type.number_of_phase_encoding_steps},
            {'name': 'percent_phase_field_of_view', 'type': 'N', 'value': seq_type.percent_phase_field_of_view},
            {'name': 'pixel_bandwidth', 'type': 'N', 'value': seq_type.pixel_bandwidth},
            {'name': 'flip_angle', 'type': 'N', 'value': seq_type.flip_angle},
            {'name': 'rows', 'type': 'N', 'value': seq_type.rows},
            {'name': 'columns', 'type': 'N', 'value': seq_type.columns},
            {'name': 'magnetic_field_strength', 'type': 'N', 'value': seq_type.magnetic_field_strength},
            {'name': 'space_between_slices', 'type': 'N', 'value': seq_type.space_between_slices},
            {'name': 'echo_train_length', 'type': 'N', 'value': seq_type.echo_train_length},
            {'name': 'percent_sampling', 'type': 'N', 'value': seq_type.percent_sampling},
            {'name': 'pixel_spacing_0', 'type': 'N', 'value': seq_type.pixel_spacing_0},
            {'name': 'pixel_spacing_1', 'type': 'N', 'value': seq_type.pixel_spacing_1}
        ]

        for seq_param in seq_param_list:
            _save_sequence_parameter(i2b2_conn, seq_type.name, seq_param['name'], seq_param['type'],
                                     seq_param['value'], encounter_num, provider_id, start_date, patient_num)


def _save_sequence_parameter(i2b2_conn, sequence_name, param_name, param_type, param_val, encounter_num, provider_id,
                             start_date, patient_num):
    concept_cd = provider_id + ':' + param_name
    concept_path = path.join("/", provider_id, SEQ_PATH_PREFIX, sequence_name, param_name)
    if param_type == 'N':
        valtype_cd = 'N'
        tval_char = 'E'
        nval_num = param_val
    else:
        valtype_cd = 'T'
        tval_char = param_val
        nval_num = None
    i2b2_conn.save_concept(concept_path, concept_cd)
    i2b2_conn.save_observation(encounter_num, concept_cd, provider_id, start_date, patient_num, valtype_cd, tval_char,
                               nval_num)
