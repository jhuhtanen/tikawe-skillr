DELETE FROM categories;
DELETE FROM category_values;

INSERT INTO categories (id, title) VALUES (1, 'Teaching');

INSERT INTO category_values (category_id, value) VALUES (1, 'Languages');
INSERT INTO category_values (category_id, value) VALUES (1, 'Art');
INSERT INTO category_values (category_id, value) VALUES (1, 'Tech');

INSERT INTO categories (id, title) VALUES (2, 'Chores');

INSERT INTO category_values (category_id, value) VALUES (2, 'Shopping assistance');
INSERT INTO category_values (category_id, value) VALUES (2, 'Household aid');
INSERT INTO category_values (category_id, value) VALUES (2, 'Taking a pet out');