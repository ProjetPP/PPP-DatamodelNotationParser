"""Contains a parser for the “human-writable” notation of the datamodel."""

import ast
from ply import lex, yacc

from ppp_datamodel.nodes import List, Triple, Missing, Resource, Or, And, Intersection, Union

__all__ = ['ParseError', 'parse_triples']

class ParseError(Exception):
    pass

tokens = tuple(('RESOURCE MISSING L_PAREN R_PAREN L_BRACK R_BRACK COMMA '
                'AND OR UNION INTERSECTION').split(' '))
t_L_PAREN = r'\('
t_R_PAREN = r'\)'
t_L_BRACK = r'\['
t_R_BRACK = r'\]'
t_COMMA = r','
t_AND = r'/\\'
t_OR = r'\\/'
t_UNION = r'∪'
t_INTERSECTION = r'∩'
def t_MISSING(t):
    r'\?'
    t.value = Missing()
    return t
def t_RESOURCE(t):
    r'([^()\[\]?,\\/∪∩"“”]+|"([^"\\]|\\.)*"|“([^“”\\]|\\.)*”)'
    # TODO: remove / from the regexp
    if t.value.startswith('“') and t.value.endswith('”'):
        t.value = '"%s"' % t.value[1:-1].replace('"', '\\"')
    if t.value.startswith('"') and t.value.endswith('"'):
        t.value = ast.literal_eval(t.value) # Handle escape characters.
    t.value = Resource(t.value.strip())
    return t
#forbidden = '|'.join((
#    r'\/', r'/\\', '\(', '\)', '\[', '\]', r'(?<!\\)"'))
#t_RESOURCE.__doc__ = '(?!(%s)*)' % (forbidden,)

t_ignore = ' '

def t_error(t):
    raise ParseError('Illegal string `%s`' % t.value)

lex.lex()


def p_triple(t):
    """triple : L_PAREN expression COMMA expression COMMA expression R_PAREN"""
    t[0] = Triple(t[2], t[4], t[6])

def p_list_body_singleton(t):
    """list_body : expression"""
    t[0] = [t[1]]

def p_list_body_comma(t):
    """list_body : list_body COMMA expression"""
    t[0] = t[1]
    t[0].append(t[3])

def p_list(t):
    """list : L_BRACK list_body R_BRACK"""
    t[0] = List(t[2])

def p_list_empty(t):
    """list : L_BRACK R_BRACK"""
    t[0] = List([])

def p_conjonction_base(t):
    """conjonction_base : RESOURCE
                        | MISSING
                        | triple
                        | list"""
    t[0] = t[1]
def p_conjonction_expr(t):
    """conjonction : L_PAREN expression R_PAREN"""
    t[0] = [t[2]]
def p_conjonction_empty(t):
    """conjonction : conjonction_base"""
    t[0] = [t[1]]
def p_conjonction(t):
    """conjonction : conjonction AND conjonction_base"""
    t[0] = t[1]
    t[0].append(t[3])

def p_disjonction_empty(t):
    """disjonction : conjonction"""
    assert isinstance(t[1], list), t[1]
    t[0] = [And(t[1])]
def p_disjonction(t):
    """disjonction : disjonction OR conjonction"""
    t[0] = t[1]
    t[0].append(And(t[3]))


def p_intersection_empty(t):
    """intersection : disjonction"""
    assert isinstance(t[1], list), t[1]
    t[0] = [Or(t[1])]
def p_intersection(t):
    """intersection : intersection INTERSECTION disjonction"""
    t[0] = t[1]
    t[0].append(Or(t[3]))

def p_union_empty(t):
    """union : intersection"""
    assert isinstance(t[1], list), t[1]
    t[0] = [Intersection(t[1])]
def p_union(t):
    """union : union UNION intersection"""
    t[0] = t[1]
    t[0].append(Intersection(t[3]))

def p_expression(t):
    """expression : union"""
    assert isinstance(t[1], list)
    t[0] = Union(t[1])


def p_error(t):
    raise ParseError("Syntax error at '%s'" % t.value)

parser = yacc.yacc(start='expression')

def simplify(tree):
    """Simplify a tree (makes it more human/developper-readable) by
    remplacing singletons by an item."""
    if isinstance(tree, (List, Or, And, Union, Intersection)) and \
            len(tree.list) == 1:
        return simplify(tree.list[0])
    elif isinstance(tree, (List, Or, And, Union, Intersection)):
        return tree.__class__(list(map(simplify, tree.list)))
    elif isinstance(tree, Triple):
        return Triple(simplify(tree.subject),
                      simplify(tree.predicate),
                      simplify(tree.object))
    else:
        return tree

def parse_triples(sentence):
    return simplify(parser.parse(sentence))
