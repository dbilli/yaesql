
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

    def test_strings(self):

        import yaesql
        import json
        
        parser = yaesql.Parser()
        
        tests = [
            #
            # Simple term
            #
            (
             'foo', 
             '{"query": {"term": {"message": {"value": "foo"}}}}'
            ),
            (
             '"foo"', 
             '{"query": {"term": {"message": {"value": "foo"}}}}'
            ),
            (
             "'foo'", 
             '{"query": {"term": {"message": {"value": "foo"}}}}'
            ),
            (
             'r"foo"', 
             '{"query": {"regexp": {"message": {"value": "foo"}}}}'
            ), 
            (
             "r'foo'", 
             '{"query": {"regexp": {"message": {"value": "foo"}}}}'
            ),
            #
            # Complex field
            #
            (
             'field1:foo', 
             '{"query": {"term": {"field1": {"value": "foo"}}}}'
            ),
            (
             'field1:"foo"', 
             '{"query": {"term": {"field1": {"value": "foo"}}}}'
            ),
            (
             "field1:'foo'", 
             '{"query": {"term": {"field1": {"value": "foo"}}}}'
            ),
            (
             'field1:r"foo"', 
             '{"query": {"regexp": {"field1": {"value": "foo"}}}}'
            ), 
            (
             "field1:r'foo'", 
             '{"query": {"regexp": {"field1": {"value": "foo"}}}}'
            ),

        ]
        
        for s, s2 in tests:
            q = parser.parseString(s)
            qs = q.compose("message")
            
            self.assertEqual( json.dumps(qs), s2 )
        
        

if __name__ == '__main__':
    unittest.main()
