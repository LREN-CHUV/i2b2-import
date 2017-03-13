from re import split


def txt2i2b2(file_path, db_conn):
    info = _extract_info(file_path)
    # TODO: Import info fields into I2B2 DB


def _extract_info(file_path):
    f = open(file_path, 'r')
    d = {}
    for line in f.readlines():
        line = line.strip()
        line = line.split('//')
        if len(line) == 3:
            if not line[1].isspace():
                key = ''.join(split(r'[ ]+', line[1].strip())[1:])
                value = ' '.join(split(r'[ ]+', line[2].strip())).split("\\")
                d.update({key: value if len(value) > 1 else value[0]})
    f.close()
    return d
