# yaesql
Yet Another ElasticSearch Query Language 

## Introduction

Yaesql is a ElasticSearch's Query DSL generator. 

It's based on a "query_string"-like syntax and provides a simple parser that generates a Query DSL object (dictionary).

```
import yaesql

parser = yaesql.Parser()

query_descriptor = parser.parseString("field1:foo OR bar")

query_body = query_descriptor.compose("message")

print(query_body)
```

## Installing

```
git clone https://github.com/dbilli/yaesql.git
cd yaesql
python setup.py test
python setup.py build
python setup.py install
```

## Examples

### Example 1 

Query string:

```
foo
```

Result:

```
{
    "query" : {
        "term" : {
            "message" : {
                "value" : 'foo'            
            }
        }
    }
}
```

### Example 2

Query string:

```
text:r"foo.*"
```

Result:

```
{
    "query" : {
        "regexp" : {
            "text" : {
                "value" : 'foo.*'
            }
        }
    }
}
```

### Example 3

Query string:

```
message:alpha AND omega OR field1:(-bar -foo)
```

Result:

```
{
    "query" : {
        "bool" : {
            "should" : [
                {
                    "bool" : {
                        "must" : [
                            {
                                "term" : {
                                    "message" : {
                                        "value" : 'alpha'
                                    }
                                }
                            }
                            ,
                            {
                                "term" : {
                                    "message" : {
                                        "value" : 'omega'
                                    }
                                }
                            }
                            ,
                        ]
                    }
                }
                ,
                {
                    "bool" : {
                        "must_not" : [
                            {
                                "term" : {
                                    "field1" : {
                                        "value" : 'bar'
                                    }
                                }
                            }
                            ,
                            {
                                "term" : {
                                    "field1" : {
                                        "value" : 'foo'
                                    }
                                }
                            }
                            ,
                        ]
                    }
                }
                ,
            ]
        }
    }
}
```


## Authors

* **Diego Billi**

## License

This project is licensed under the GNUv2 License - see the [LICENSE](LICENSE.md) file for details

## Acknowledgments

* Thomas Steinacher (https://blog.close.com/author/thomas-steinacher)

