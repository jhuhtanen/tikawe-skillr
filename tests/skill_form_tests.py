import unittest
from copy import copy
from operator import contains

from flaskr.skills import SkillForm


valid_form_data = { "title" : "title", "price": "1", "description": "description", "is_free": "0", "category" : "1", "subcategory" : "1"}

class TestFormValidation(unittest.TestCase):
    def test_empty_form(self):
        form_data = {}
        form = SkillForm(form_data)
        has_errors = form.validate()
        self.assertTrue(has_errors)
        self.assertEqual(4, len(form.errors))

    def test_all_fields_exists(self):
        form_data = copy(valid_form_data)
        form = SkillForm(form_data)
        has_errors = form.validate()
        self.assertFalse(has_errors)
        self.assertEqual(0, len(form.errors))

    def test_title_missing(self):
        form_data = copy(valid_form_data)
        form_data["title"] = ""
        form = SkillForm(form_data)
        has_errors = form.validate()
        self.assertTrue(has_errors)
        self.assertEqual(1, len(form.errors))

    def test_price_incorrect(self):
        form_data = copy(valid_form_data)
        form_data["price"] = "-5"
        form = SkillForm(form_data)
        has_errors = form.validate()
        self.assertTrue(has_errors)
        self.assertEqual(1, len(form.errors))
        self.assertTrue(contains(form.errors, "Price must be 1 or greater!"))
