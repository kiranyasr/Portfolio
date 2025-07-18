
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS about;
DROP TABLE IF EXISTS projects;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE about (
    id INTEGER PRIMARY KEY,
    bio TEXT
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tech_stack TEXT,
    github TEXT,
    demo TEXT,
    image TEXT,
    outcome TEXT,
    tools TEXT,
    use_case TEXT
);



INSERT INTO users (username, password) VALUES ('admin', 'admin');
INSERT INTO about (id, bio) VALUES (1, 'This is your editable bio.');
