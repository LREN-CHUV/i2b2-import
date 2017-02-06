[![CircleCI](https://circleci.com/gh/LREN-CHUV/i2b2-import.svg?style=svg)](https://circleci.com/gh/LREN-CHUV/i2b2-import)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/850854199e9c4fbca8386a10bf1c4867)](https://www.codacy.com/app/mirco-nasuti/i2b2-import?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=LREN-CHUV/i2b2-import&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/LREN-CHUV/i2b2-import/blob/master/LICENSE)


# I2B2 Import

## Introduction

This library provides functions to import data into an I2B2 DB schema.

## Installation

Run: `pip install i2b2_import`

## Usage

To import brain features and other observations from a CSV file, use:
```
observationfact_csv_import.csv2db(file_path, db_conn, src)
    Import brain features and other observation facts data from a CSV file into the I2B2 DB schema.
    * param file_path: Path to the CSV file.
    * param db_conn: Connection to the I2B2 DB.
    * param src: Data source (e.g. CHUV, ADNI, PPMI, etc).
```

To import metadata from an XML file following the PPMI practice, use:
```
ppmi_xml_import.PPMIXMLImport.meta2i2b2(source, db_conn):
    The function that imports meta data from PPMI XML file into the I2B2 schema.
    * param source: XML file containing PPMI meta data.
    * param db_conn: Connection to the I2B2 DB.
```

To import metadata from the data-catalog-db, use:
```
datacatalogdb_import.DataCatalogDBImport.meta2i2b2(source, db_conn)
    The function that imports meta data from the MRI DB into the I2B2 schema.
    * param source: Connection to the MRI DB.
    * param db_conn: Connection to the I2B2 DB.
```


## Test

Open the tests directory and run `./test.sh`.

NOTE: Docker is needed.

## build

Run `./build.sh`.

## Push on PyPi

Run `./publish.sh`.

(This builds the project prior to pushing it).
