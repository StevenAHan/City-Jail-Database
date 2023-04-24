-- For Creating Authentication

CREATE TABLE users(
    username VARCHAR(30),
    password VARCHAR(100),
    power CHAR(1),
    PRIMARY KEY(username, password)
);

-- 123
INSERT INTO users VALUES("steven", "$2a$12$tqrZifSKi/0SCFtwuxG9e.Xvv/QDKrPfrdT9THZA2SF5IwIHg8/IK", "M");

-- abc
INSERT INTO users VALUES("srikar", "$2a$12$26oZUw1Vo8lokbHR474CDuHdI54K8l9Qq.PlBpF3UzSv9sTlMUR3u", "M");

-- user
INSERT INTO users VALUES("normal", "$2a$12$N/oIjQEw1BBsMrd2empltuDN7IY46IfETipr/Z0j5.cC6jIDymUVe", "V");

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
