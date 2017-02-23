from math import floor


def meta2i2b2(data_catalog_conn, i2b2_conn):
    """
    Import meta data from the Data Catalog DB to the I2B2 schema.
    :param data_catalog_conn: Connection to the Data Catalog DB.
    :param i2b2_conn: Connection to the I2B2 DB.
    :return:
    """
    sequences = data_catalog_conn.db_session.query(data_catalog_conn.Sequence).all()
    for seq in sequences:
        scan_id = data_catalog_conn.db_session.query(data_catalog_conn.Session)\
            .filter_by(id=seq.session_id).first().visit_id
        scan = data_catalog_conn.db_session.query(data_catalog_conn.Visit).filter_by(id=scan_id).first()

        participant = data_catalog_conn.db_session.query(data_catalog_conn.Participant)\
            .filter_by(id=scan.participant_id).first()
        patient_ide = participant.id
        sex_cd = participant.gender
        try:
            birth_date = participant.birth_date
        except AttributeError:
            birth_date = None
        try:
            age_in_years_num = int(floor(participant.age)) + 1  # I2B2 uses an integer value for age
        except (AttributeError, TypeError):
            age_in_years_num = None

        repetition_id = data_catalog_conn.db_session.query(data_catalog_conn.Repetition).\
            filter_by(sequence_id=seq.id).first().id
        processing_step_id = data_catalog_conn.db_session.query(data_catalog_conn.DataFile).\
            filter_by(repetition_id=repetition_id)\
            .first().processing_step_id
        provenance_id = data_catalog_conn.db_session.query(data_catalog_conn.ProcessingStep).\
            filter_by(id=processing_step_id).first()\
            .provenance_id
        dataset = data_catalog_conn.db_session.query(data_catalog_conn.Provenance).\
            filter_by(id=provenance_id).first().dataset

        patient_ide_source = dataset
        project_id = dataset
        patient_num = i2b2_conn.get_patient_num(patient_ide, patient_ide_source, project_id)

        i2b2_conn.save_patient(patient_num, sex_cd, age_in_years_num, birth_date)
