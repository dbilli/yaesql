
import unittest

import yaesql

class TestStringMethods(unittest.TestCase):

    def test_import(self):

        parser = yaesql.Parser()
        
    def test_parse(self):
        
        parser = yaesql.Parser()

        parser.parseString("foo")

    def test_parse_error(self):

        parser = yaesql.Parser()
        
        with self.assertRaises(Exception):
            parser.parseString(":foo")
    
    def test_simple_query(self):

        import yaesql
        import json
        
        parser = yaesql.Parser()
        
        query_descriptor = parser.parseString("field1:foo OR bar")
        
        query_body = query_descriptor.compose("message")
       
        self.assertEqual( json.dumps(query_body), '{"query": {"bool": {"should": [{"term": {"field1": {"value": "foo"}}}, {"term": {"message": {"value": "bar"}}}]}}}')
        
        

if __name__ == '__main__':
    unittest.main()
