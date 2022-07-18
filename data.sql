CREATE TABLE purchase(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    stock_name TEXT NOT NULL,
    stock_symbol TEXT NOT NULL,
    stock_price NUMERIC NOT NULL,
    shares INTEGER NOT NULL,
    users_id INTEGER NOT NULL,
    time TEXT NOT NULL,
    action TEXT NOT NULL,
    FOREIGN KEY (users_id)
       REFERENCES users (id)
);
CREATE TABLE subject(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    hours INTEGER NOT NULL,
    percent INTEGER NOT NULL,
    gpa NUMERIC NOT NULL,
    users_id INTEGER NOT NULL,
    FOREIGN KEY (users_id)
       REFERENCES users (id)
);

CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, hash TEXT NOT NULL);