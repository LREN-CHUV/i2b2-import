from i2b2_import.meta_import import MetaImport
from math import floor


class DataCatalogDBImport(MetaImport):
    """
    This is an implementation of the MetaImport class.
    It can be used to import meta data from the MRI DB into the I2B2 schema.
    """
    @staticmethod
    def meta2i2b2(source, db_conn):
        """
        The function that imports meta data from the MRI DB into the I2B2 schema.
        :param source: Connection to the MRI DB.
        :param db_conn: Connection to the I2B2 DB.
        :return:
        """
        sequences = source.db_session.query(source.Sequence).all()
        for seq in sequences:
            scan_id = source.db_session.query(source.Session).filter_by(id=seq.session_id).first().scan_id
            scan = source.db_session.query(source.Scan).filter_by(id=scan_id).first()

            participant = source.db_session.query(source.Participant).filter_by(id=scan.participant_id).first()
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

            repetition_id = source.db_session.query(source.Repetition).filter_by(sequence_id=seq.id).first().id
            processing_step_id = source.db_session.query(source.DataFile).filter_by(repetition_id=repetition_id)\
                .first().processing_step_id
            provenance_id = source.db_session.query(source.ProcessingStep).filter_by(id=processing_step_id).first()\
                .provenance_id
            dataset = source.db_session.query(source.Provenance).filter_by(id=provenance_id).first().dataset

            patient_ide_source = dataset
            project_id = dataset
            patient_num = db_conn.get_patient_num(patient_ide, patient_ide_source, project_id)

            db_conn.save_patient(patient_num, sex_cd, age_in_years_num, birth_date)
