class MetaImport(object):
    """
    This is an abstract class. You should inherit from this class to implement a new way of importing meta data into the
    I2B2 schema. For example, we will need an implementation to import PPMI XML files meta data, meta data from the mri
    DB (that contains informations from DICOM and NIFTI files), BIDS formatted JSON files, etc.
    """
    @staticmethod
    def meta2i2b2(source, db_conn):
        """
        Abstract function. Implementation of it should extract some meta data from the 'source' and store them in the DB
        at 'db_conn'.
        :param source: Input data. Can be a file, a DB URL, etc.
        :param db_conn: Connection to the I2B2 DB.
        :return:
        """
        raise NotImplementedError("You should implement meta2i2b2")
