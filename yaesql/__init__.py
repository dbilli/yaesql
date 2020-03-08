
import pyparsing as pp

#----------------------------------------------------------------------#
# CLASSES                                                              #
#----------------------------------------------------------------------#

class Expr(object):

    def __init__(self, sub=None):
        self.is_sub = False

    def dump(self):
        raise NotImplementedError

    def compose(self, field_name):
        raise NotImplementedError

#----------------------------------------------------------------------#

class Literal(Expr):

    def __init__(self, val):
        super().__init__(val)
        self.val = val

    def compose(self, field_name):
        return self.val

class RegExLiteral(Literal):

    def __init__(self, val):
        super().__init__(val)

    def dump(self):
        return "REGEX(%s)" % (repr(self.val))

    def compose(self, field_name):
        return self.val


class StringLiteral(Literal):

    def __init__(self, val):
        super().__init__(val)

    def dump(self):
        return "STRING(%s)" % (repr(self.val))

class NumberLiteral(Literal):

    def __init__(self, val):
        super().__init__(val)

    def dump(self):
        return "NUMBER(%s)" % (repr(self.val))

#----------------------------------------------------------------------#

class SimpleTerm(Expr):

    def __init__(self, expr):
        super().__init__(expr)
        self.expr = expr

    def dump(self):
        return "SimpleTerm(%s)" % (self.expr.dump()) #.dump())

    def compose(self, field_name):
        
        if isinstance(self.expr, RegExLiteral):
            q = {
                'regexp': {
                    field_name: {
                        "value": self.expr.compose(field_name)
                    }
                }
            
            }
        else:
            q = {
                'term': {
                    field_name: {
                        "value": self.expr.compose(field_name)
                    }
                }
            
            }
        return q

class ComplexTerm(Expr):

    def __init__(self, field_expr, value_expr):
        super().__init__( (field_expr, value_expr) )
        self.field_expr = field_expr
        self.value_expr = value_expr

        value_expr.is_sub = True

    def dump(self):
        return "ComplexTerm(%s:%s)" % (self.field_expr, self.value_expr.dump())

    def compose(self, field_name):
        field_name = self.field_expr
        q = self.value_expr.compose(field_name)
        return q


class MultiValue(Expr):

    def __init__(self, exprs):
        super().__init__( exprs )
        self.exprs = exprs

        for e in self.exprs:
            e.is_sub = True

    def dump(self):
        return "VALUES(%s)" % ( ', '.join([ e.dump() for e in self.exprs ]) )

    def compose(self, field_name):

        q = {
            'bool': {
            }
        }

        must_conds     = []
        must_not_conds = []
        should_conds   = []

        for e in self.exprs:
            subq = e.compose(field_name)

            if   isinstance(e, BoolMust): 
                subq = subq['bool']['must']
                must_conds.append( subq )
            elif isinstance(e, BoolMustNot): 
                subq = subq['bool']['must_not']
                must_not_conds.append( subq )
            else:
                should_conds.append(subq)

        if not must_conds and not must_not_conds and should_conds:
            if len(should_conds) > 1:
                q['bool']['should'  ] = should_conds
            else:
                q = should_conds[0]
        else:
            if must_conds    : 
                q['bool']['must'    ] = must_conds if len(must_conds) > 1 else must_conds[0]
            if must_not_conds: 
                q['bool']['must_not'] = must_not_conds if len(must_not_conds) > 1 else must_not_conds[0] 
            if should_conds  : 
                q['bool']['should'  ] = should_conds if len(should_conds) > 1 else should_conds[0] 

        return q

#----------------------------------------------------------------------#

class BoolExpr(Expr):
    def __init__(self, expr):
        super().__init__(expr)

class BoolMust(BoolExpr):

    def __init__(self, expr):
        super().__init__(expr)
        self.expr = expr

        expr.is_sub = True

    def dump(self):
        return "Must(%s)" % (self.expr.dump())

    def compose(self, field_name):
        q = self.expr.compose(field_name)
        r = {
            'bool': {
                "must": q
            }
        }
        return r

class BoolMustNot(BoolExpr):

    def __init__(self, expr):
        super().__init__(expr)

        self.expr = expr

        expr.is_sub = True

    def dump(self):
        return "MustNot(%s)" % (self.expr.dump())

    def compose(self, field_name):
        q = self.expr.compose(field_name)
        r = {
            'bool': {
                "must_not": q
            }
        }
        return r

#----------------------------------------------------------------------#

class NotExpr(Expr):

    def __init__(self, expr):
        super().__init__(expr)
        self.expr = expr

        expr.is_sub = True

    def dump(self):
        return "NOT(%s)" % (self.expr.dump())

    def compose(self, field_name):
        q = self.expr.compose(field_name)

        q = {
            'bool': {
                'must_not': q
            }
        }

        return q


class AndExpr(Expr):

    def __init__(self, exprs):
        super().__init__(exprs)
        
        self.exprs = exprs

        for e in exprs:
            e.is_sub = True

    def dump(self):
        return "(%s)" % ( ' AND '.join([e.dump() for e in self.exprs]) )

    def compose(self, field_name):
        if len(self.exprs) == 1:

            q = self.expr[0].compose(field_name)
            if 'query' in q:
                return q['query']
            else:
                return {
                    'query': q
                }
        else:
            conds = []
            for e in self.exprs:
                subq = e.compose(field_name)
                conds.append(subq)

            q = {
                'bool': {
                    'must': conds
                }
            }
            return q

class OrExpr(Expr):

    def __init__(self, exprs):
        super().__init__()
        self.exprs = exprs

        for e in exprs:
            e.is_sub = True

    def dump(self):
        return "(%s)" % ( ' OR '.join([e.dump() for e in self.exprs]) )

    def compose(self, field_name):
        if len(self.exprs) == 1:
            return self.expr[0].compose(field_name)
        else:
            conds = []
            for e in self.exprs:
                subq = e.compose(field_name)
                conds.append(subq)

            q = {
                'bool': {
                    'should': conds
                }
            }
            return q

#----------------------------------------------------------------------#

class Query(Expr):

    def __init__(self, exprs):
        super().__init__(exprs)

        self.exprs = exprs

        for e in exprs:
            e.is_sub = True

    def dump(self):
        return "Query(%s)" % (' '.join([e.dump() for e in self.exprs]))

    def compose(self, field_name):

        if len(self.exprs) == 1:
            
            print(1)
            
            e = self.exprs[0]
            
            q = e.compose(field_name)
            
            if self.is_sub:
                return q

            return {
                'query': q
            }

        else:
            must_conds     = []
            must_not_conds = []
            should_conds   = []

            conds = []
            for e in self.exprs:
                subq = e.compose(field_name)

                if   isinstance(e, BoolMust): 
                    subq = subq['bool']['must']
                    must_conds.append( subq )
                elif isinstance(e, BoolMustNot): 
                    subq = subq['bool']['must_not']
                    must_not_conds.append( subq )
                else:
                    should_conds.append(subq)

                conds.append(subq)

            if not must_conds and not must_not_conds and should_conds:
                must_conds = should_conds
                should_conds = []

            q = { 
                'bool': {
                }
            }

            if must_conds    : 
                q['bool']['must'    ] = must_conds if len(must_conds) > 1 else must_conds[0]
            if must_not_conds: 
                q['bool']['must_not'] = must_not_conds if len(must_not_conds) > 1 else must_not_conds[0] 
            if should_conds  : 
                q['bool']['should'  ] = should_conds if len(should_conds) > 1 else should_conds[0] 



            
            if self.is_sub:
                return q

            return {
                'query': q
            }


def _create_parser(self):

    #----------------------------------------------------------------------#
    # TOKENS                                                               #
    #----------------------------------------------------------------------#
    
    START = pp.StringStart().suppress()
    END   = pp.StringEnd().suppress()

    #
    # NUMBER
    #
    #NUMBER = pp.Regex(r"[+-]?\d+(:?\.\d*)?(:?[eE][+-]?\d+)?")           .setParseAction( lambda s, loc, toks: [ self.create_NumberLiteral(int(toks[0])) ] ) 

    #
    # -foo_bar:
    TERM    = pp.Word(pp.alphanums, pp.alphanums+'.-+_/')
    

    #
    # "..."
    # '...'
    #
    QUOTED  = pp.QuotedString('"', escChar='\\') | pp.QuotedString("'", escChar='\\')
    
    #
    # r"..."
    # r'...'
    #
    REGEXP  = pp.Combine(pp.Suppress('r') + QUOTED)       .setParseAction( self.create_RegExLiteral )
    

    STRINGS = (
               REGEXP                                               
               | 
               QUOTED                                               .setParseAction( self.create_StringLiteral ) 
               | 
               TERM                                                 .setParseAction( self.create_StringLiteral )
              )                                                     

    #
    # SYNTAX
    #
    LPAR, RPAR = map(pp.Suppress, "()")

    PLUS  = pp.Suppress('+')
    MINUS = pp.Suppress('-')

    COLON = pp.Suppress(':')

    NOT   = pp.Suppress('NOT')
    AND   = pp.Suppress('AND')
    OR    = pp.Suppress('OR')

    TOKENS = COLON | LPAR | RPAR | NOT | AND | OR | PLUS | MINUS

    #
    # IDENTIFIER (field_names)
    #
    FIELD = pp.Word(pp.alphas, pp.alphanums+".")                         .setParseAction( lambda s, loc, toks: [ toks[0] ] )
    
    #FIELD = (~(TOKENS))            .setParseAction( lambda s, loc, toks: [ toks[0] ] )

    basic_value = (~(TOKENS) + STRINGS)

    #----------------------------------------------------------------------#
    # TERMS                                                                #
    #----------------------------------------------------------------------#

    #
    # Simple TERM
    #
    simple_term = (
            # bool_term 
            #| 
            basic_value                                             .setParseAction( self.create_SimpleTerm )
    )

    #
    # COMPLEX TERM 
    #
    #     <field name> ':' <field_value>
    #

    multi_term_expr  = ( 
            (PLUS  + basic_value)                     .setParseAction( self.create_BoolMust )  
            |                                                        
            (MINUS + basic_value)                     .setParseAction( self.create_BoolMustNot )                        
            |
            basic_value   
    )      

    multi_term_sequence = (
              LPAR 
              + 
              pp.OneOrMore(multi_term_expr)                             .setParseAction( self.create_MultiValue ) 
              + 
              RPAR
             )      

    complex_value = (
             simple_term 
             |
             multi_term_sequence
            )
    
    complex_term = (FIELD + COLON + complex_value)                           .setParseAction( self.create_ComplexTerm ) 

    #-------------------------------------------------------------------
    # EXPRESSION
    #-------------------------------------------------------------------

    query = pp.Forward()

    #
    #   <field>:<query>
    #   <term>
    #   ( <query> )
    #
    base_expr = ( 
             complex_term 
             | 
             simple_term  
             |
             (LPAR + query + RPAR)                                        .setParseAction( lambda s, loc, toks: [ toks[0] ] ) 
            )

    #-------------------------------------------------------------------
    # BOOLEAN EXPRESSION
    #-------------------------------------------------------------------
    
    # NOT expr
    #     expr
    unary_expr  = ( 
            (NOT + base_expr)                       .setParseAction( self.create_NotExpr ) 
            |
            (PLUS  + base_expr)                     .setParseAction( self.create_BoolMust )  
            |                                                        
            (MINUS + base_expr)                     .setParseAction( self.create_BoolMustNot )                        
            |
            base_expr   
    )             

    #simple_expr = unary_expr

    #
    # expr ( AND expr ) *
    #
    and_expr = (unary_expr + pp.ZeroOrMore(AND + unary_expr))                 .setParseAction( self.create_AndExpr ) 

    #
    # expr ( OR expr ) *
    #
    or_expr  = (and_expr    + pp.ZeroOrMore(OR + and_expr))                   .setParseAction( self.create_OrExpr )  

    boolean_expr = or_expr
    
    full_expr = boolean_expr 

    #
    # clause ::= cond_expr +
    #
    clauses = pp.OneOrMore(full_expr)

    query <<= clauses 

    #
    # PARSER
    #
    parser = (
          START
          + 
          query                                                     .setParseAction( self.create_Query ) 
          + 
          END
         )

    return parser



class Parser(object):
    
    def __init__(self):
        self.parser = _create_parser(self)

    def create_RegExLiteral(self, s, loc, toks):
        return RegExLiteral( toks[0] )

    def create_StringLiteral(self, s, loc, toks):
        return StringLiteral( toks[0] )

    def create_NumberLiteral(self, s, loc, toks):
        return NumberLiteral( toks[0] )

    def create_SimpleTerm(self, s, loc, toks):
        return SimpleTerm( toks[0] )

    def create_BoolMust(self, s, loc, toks):
        return BoolMust( toks[0] )

    def create_BoolMustNot(self, s, loc, toks):
        return BoolMustNot( toks[0] )

    def create_ComplexTerm(self, s, loc, toks):
        return ComplexTerm( toks[0], toks[1] )

    def create_MultiValue(self, s, loc, toks):
        return MultiValue(toks)

    def create_NotExpr(self, s, loc, toks):
        return NotExpr( toks[0] )

    def create_AndExpr(self, s, loc, toks):
        if len(toks) == 1:
            return toks[0]
        return AndExpr( toks )

    def create_OrExpr(self, s, loc, toks):
        if len(toks) == 1:
            return toks[0]
        return OrExpr(toks)

    def create_Query(self, s, loc, toks):
        return Query( toks )

    #--------------------------------------------------------------#

    def parseString(self, s):
        return self.parser.parseString(s)[0]



if __name__ == "__main__":

    import sys
    
    parser = Parser()
    
    index_name    = sys.argv[1]
    default_field = sys.argv[2]
    string_query  = sys.argv[3]
    
    print(string_query)
    
    query_generator = parser.parseString(string_query)
    
    print(query_generator.dump())
    
    es_dsl_query = query_generator.compose(default_field)
    
    
    def myprint(o, l=0, ind='    '):
        s = ''
        if isinstance(o, dict):
            s += "{\n"
            for k,v in o.items():
                s += ind * (l+1)
                s += '"%s" : %s' % (k, myprint(v, l+1, ind))
            s += ind * l
            s += "}\n"
        elif isinstance(o, list):
            s += "[\n"
            for o2 in o:
                s += ind * (l+1) + myprint(o2, l+1, ind) 
                s += ind * (l+1) + ',\n'
            s += ind * l
            s +="]\n"
        else:
            s = repr(o) + '\n'
        return s
    
    
    print( myprint(es_dsl_query) )
    
    '''
    from elasticsearch import Elasticsearch
    
    es = Elasticsearch()
    
    res = es.search(index=index_name, body=query_body, size=10000)
    print("Got %d Hits:" % res['hits']['total']['value'])
    for hit in res['hits']['hits']:
        print(hit["_source"])
    '''
