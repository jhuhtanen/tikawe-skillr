DELETE FROM categories;
DELETE FROM category_values;

INSERT INTO categories (id, title) VALUES (1, 'Teaching');

INSERT INTO category_values (category_id, value) VALUES (1, 'Languages');
INSERT INTO category_values (category_id, value) VALUES (1, 'Art');
INSERT INTO category_values (category_id, value) VALUES (1, 'Tech');