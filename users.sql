CREATE TABLE users{
    username VARCHAR(30),
    password VARCHAR(30),
    power CHAR(1),
    PRIMARY KEY(username, password)
};

INSERT INTO users VALUES("steven", "123", "A");

INSERT INTO users VALUES("srikar", "abc", "A");

INSERT INTO users VALUES("normal", "user", "V");