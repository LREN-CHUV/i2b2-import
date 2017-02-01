from i2b2_import.meta_import import MetaImport


class MRIDBMetaImport(MetaImport):
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
        pass
