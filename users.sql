-- For Creating Authentication

CREATE TABLE users(
    username VARCHAR(30),
    password VARCHAR(30),
    power CHAR(1),
    PRIMARY KEY(username, password)
);

INSERT INTO users VALUES("steven", "123", "M");

INSERT INTO users VALUES("srikar", "abc", "M");

INSERT INTO users VALUES("normal", "user", "V");

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
