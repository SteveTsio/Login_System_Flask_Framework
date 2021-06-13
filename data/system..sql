CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT
                     NOT NULL,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    email    VARCHAR NOT NULL
);
