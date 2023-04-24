-- For Creating Authentication

CREATE TABLE users(
    username VARCHAR(30),
    password VARCHAR(255),
    power CHAR(1),
    PRIMARY KEY(username, password)
);

-- 123
INSERT INTO users VALUES("steven", "$2b$12$SxHP6/PBf2ft5GlDb/rT6uEj5mYQ6kQ9bVYCeBGqXohrzYFQ.pTVu", "M");

-- abc
INSERT INTO users VALUES("srikar", "$2b$12$0bRlQUji0tFHwzvPxQ463.JeUmb3AXN7PSd6IJ737Mz.N4HmBut16", "M");

-- user
INSERT INTO users VALUES("normal", "$2b$12$dGSuTGp9oNWR50K240VY9.P6MDOHO6GTLq9/NYA2bw/Wcy5IMVq3i", "V");

-- DB security - moderators can change anything, editors can edit data other than users, 
--               viewers can view all non-users data, and outsiders cannot do anything

CREATE ROLE viewer;

GRANT SELECT ON * TO viewer;

CREATE ROLE moderator;

GRANT ALL PRIVILEGES ON * TO moderator;

CREATE ROLE editor;

GRANT SELECT INSERT ALTER ON * TO editor;

CREATE ROLE outsider;

REVOKE ALL PRIVILEGES ON * TO outsider;

REVOKE SELECT ON users TO viewer;

REVOKE ALL PRIVILEGES ON users TO editor;
