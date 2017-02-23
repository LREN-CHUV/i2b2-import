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
        visit_id = data_catalog_conn.db_session.query(data_catalog_conn.Session)\
            .filter_by(id=seq.session_id).one_or_none().visit_id
        visit = data_catalog_conn.db_session.query(data_catalog_conn.Visit).filter_by(id=visit_id).one_or_none()

        participant = data_catalog_conn.db_session.query(data_catalog_conn.Participant)\
            .filter_by(id=visit.participant_id).one_or_none()
        patient_id = participant.id
        sex_cd = participant.gender

        try:
            birth_date = participant.birth_date
        except AttributeError:
            birth_date = None
        try:
            age_in_years_num = int(floor(participant.age)) + 1  # I2B2 uses an integer value for age
        except (AttributeError, TypeError):
            age_in_years_num = None

        patient_ide, dataset = data_catalog_conn.get_patient_map(patient_id)

        patient_ide_source = dataset
        project_id = dataset

        patient_num = i2b2_conn.get_patient_num(patient_ide, patient_ide_source, project_id)

        i2b2_conn.save_patient(patient_num, sex_cd, age_in_years_num, birth_date)
