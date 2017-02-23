INSERT INTO "provenance" VALUES (1,'PPMI');

INSERT INTO "processing_step" VALUES (1,'ACQUISITION',1);

INSERT INTO "participant_mapping" VALUES ('12345','PPMI',1);

INSERT INTO "participant" VALUES ('1','M');

INSERT INTO "visit_mapping" VALUES ('scan_1','PPMI',1);

INSERT INTO "visit" VALUES (1,null,null,null,1);

INSERT INTO "session" VALUES (1,'session_1',1);

INSERT INTO "sequence_type" VALUES (1,'TEST SEQ');

INSERT INTO "sequence" VALUES (1,'seq1',1,1);

INSERT INTO "repetition"  VALUES (1,1,1);

INSERT INTO "data_file" VALUES (1,'/fake/fake.dcm','DICOM',1,1);
