import unittest
import app

def TestApp(unittest.TestCase):


    def test_array_to_json():
        test_array = [ { "key": "val1", "key2": "val2" }, { "key": "val3", "key2": "val4" } ]
        json = app.array_to_json(test_array, "key")
        self.assertEqual(type(json), type({}))
        self.assertTrue("val1" in json)
        self.assertTrue("val2" in json)
        self.assertEqual(json["val1"]["key"], "val1")
        self.assertEqual(json["val2"]["key"], "val3")
