CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    method TEXT NOT NULL,
    salt TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE user_profile (
    user_id TEXT UNIQUE REFERENCES users(id),
    name TEXT NOT NULL
);

CREATE TABLE password_reset_token (
    email TEXT UNIQUE REFERENCES users(username),
    reset_expiry INTEGER NOT NULL,
    reset_token TEXT NOT NULL
);

CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    is_free BOOLEAN NOT NULL CHECK (is_free IN (0, 1)),
    price INTEGER,
    user_id INTEGER REFERENCES users
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills,
    user_id INTEGER REFERENCES users,
    rating INTEGER NOT NULL CHECK (rating IN (0,1,2,3,4,5)),
    description TEXT
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    title TEXT
);

CREATE TABLE category_values (
    id INTEGER PRIMARY KEY,
    category_id INTEGER REFERENCES categories ON DELETE CASCADE,
    value TEXT
);

CREATE TABLE skill_categories (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills ON DELETE CASCADE,
    category_value_id INTEGER REFERENCES category_values ON DELETE CASCADE
);

CREATE TABLE skill_images (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills,
    image_path TEXT
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER REFERENCES skills,
    customer_id INTEGER REFERENCES users,
    is_completed BOOLEAN NOT NULL CHECK (is_completed IN (0, 1)),
    order_placed TEXT NOT NULL,
    order_completed TEXT,
    additional_information TEXT
);
