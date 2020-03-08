
# yaesql
Yet Another ElasticSearch Query Language 

1. [Introduction](#introduction)
2. [Installing](#installing)
3. [Documentation](#documentation)
    - [API](#api)
    - [Language](#language)
4. [Examples](#examples)


## 1. Introduction<a name="introduction"></a>

Yaesql is a ElasticSearch's Query DSL generator. 

It's based on a "query_string"-like syntax and provides a simple parser that generates a Query DSL object (dictionary).

```
import yaesql

parser = yaesql.Parser()

query_descriptor = parser.parseString("field1:foo OR bar")

query_body = query_descriptor.compose("message")

print(query_body)
```

Output:

```
{
    "query" : {
        "bool" : {
            "should" : [
                {
                    "term" : {
                        "field1" : {
                            "value" : 'foo'
                        }
                    }
                }
                ,
                {
                    "term" : {
                        "message" : {
                            "value" : 'bar'
                        }
                    }
                }
                ,
            ]
        }
    }
}
```




## 2. Installing<a name="installing"></a>

```
git clone https://github.com/dbilli/yaesql.git
cd yaesql
python setup.py test
python setup.py build
python setup.py install
```







## 3. Documentation<a name="documentation"></a>

### 3.1. API<a name="api"></a>

#### Create a parser

```
from yaesql import Parser

parser = Parser()
```

#### Parse a query string

Use the method `parseString()` to parse a query string:

```
query_obj = parser.parseString("field1:foo")
```

The method returns an instance of the class `Query`.

#### Get the DSL object

Call the `Query::compose()` method. The methods accepts a string with the name of the `default field`:

```
dsl_query = query_obj.compose("message")
```

#### User the DSL object

```
from elasticsearch import Elasticsearch

es = Elasticsearch()

res = es.search(index='test', body=dsl_query)
```

### 3.2. Language<a name="language"></a>

A `query` is a sequence of expressions:

        <expression> [ <expression> ... ]

An `expression` can be

* a single `matching expression`
* a group of `matching expression`s combined with logic `operators`: `AND`, `OR`, `NOT`.

You can enclose `expression` in rounded parentheses `()` in order to change `operators`'  precedence.


#### 3.2.1 Matching expression

A `matching expression` is a rule for matching on:

* the `default field`.
* a `field`.


##### Match on the `default field`

The general sintax is:
        
        [ '+' | '-' ] <value>

The `value` part can be:

* Simple value:

       foo
       "foo"
       'foo'

       +foo
       -foo
       -"foo"
       
* Regular expression:

       r"foo.*"
       r'foo.?'
       
       -r'foo.?'
       +r'Hell. world'


##### Match on a `field`:

The syntax is:

       <field name> [ ':' | '=' ] <value>
  
Where `field name` is the name of a field in the matching document. 

The `value` can be:

* A simple value

        field1:foo
        field1:"foo"

* A sequence of values enclosed by `()`:

        field1:("foo" bar "hello world")

##### Compare a `field`

The syntax is:

        <field name> : [ '<' | '<=' | '>' | '>=' ] <value>

Example:

        field1:<=10

        timestamp:>2020-03-20
        timestamp:>"2020-03-20"    equivalent
        timestamp:>'2020-03-20'    equivalent
        


#### 3.2.2 Boolean operators

User boolean `operators` in order to create compound expressions:

* NOT

        NOT <expression>

* AND

        <expression 1> AND <expression2>

* OR

        <expression 1> OR <expression 2>

Operator `NOT` has precedence on `AND`. Operator `AND` has precedence on `OR`. 

For example, this expression:

        alpha OR beta AND NOT gamma OR delta

is equivalent to:

        (alpha OR (beta AND gamma) OR delta)





## 4.Examples<a name="examples"></a>

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

