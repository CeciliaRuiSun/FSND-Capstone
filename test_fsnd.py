import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Category, Item

class FSNDTestCase(unittest.TestCase):
    """This class represents the fsnd test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        db_host = os.getenv('DB_HOST', 'localhost:5432')  
        database_name = os.getenv('DB_NAME', 'fsnd_test')  
        database_path = 'postgresql://{}/{}'.format(db_host, database_name)
        setup_db(self.app, database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])
        self.assertTrue(len(data["categories"]) > 0)
    
    def test_get_categories_not_exist(self):
        Category.query.delete()
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
    
    def test_get_paginated_items(self):
        res = self.client().get("/items")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["items"])
        self.assertTrue(len(data["items"]) > 0)
    
    def test_get_paginated_items_not_exist(self):
        Item.query.delete()
        res = self.client().get("/items")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
    
    def test_create_item(self):
        new_item = {
            'title': 'Crunchy Cheese Flavored Snack Chips',
            'brand': 'Cheetos',
            'comment': 'Very good',
            'category': 1
        }
        total_items_old = len(Item.query.all())
        res = self.client().post("/items", json=new_item)
        data = json.loads(res.data)
        total_items_new = len(Item.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_items_new - total_items_old, 1)

    def test_create_item_fail(self):
        new_item = {
            'title': 'Crunchy Cheese Flavored Snack Chips',
            'comment': 'Very good',
            'category': 1
            }
        res = self.client().post("/items", json=new_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_update_item(self):
        new_item = {
            'id': 1,
            'title': 'Nacho Cheese Flavored Tortilla Chips',
            'brand': 'Doritos',
            'comment': 'I will buy it again',
            'category': 1
        }
        res = self.client().patch("/items/1", json=new_item)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        
    def test_update_item_fail(self):
        new_item = {
            'id': 1,
            'title': 'Crunchy Cheese Flavored Snack Chips',
            'comment': 'Very good',
            'category': 1
            }
        res = self.client().patch("/items/1", json=new_item)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_delete_item(self):
        total_items = len(Item.query.all())
        res = self.client().delete("/items/5")
        data = json.loads(res.data)
        total_items_after_delete = len(Item.query.all())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_items - total_items_after_delete, 1)

    def test_delete_item_does_not_exist(self):
        res = self.client().delete("/items/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


if __name__ == "__main__":
    unittest.main()