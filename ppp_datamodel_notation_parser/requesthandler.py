"""Request handler of the module."""

from functools import partial

from ppp_datamodel import Sentence, TraceItem, Response
from ppp_datamodel.parsers import parse_triples, ParseError

def tree_to_response(tree, measures, trace):
    trace = trace + [TraceItem('DatamodelNotationParser',
                                            tree, measures)]
    return Response('en', tree, measures, trace)

class RequestHandler:
    def __init__(self, request):
        self.request = request

    def answer(self):
        if not isinstance(self.request.tree, Sentence):
            return []
        try:
            tree = parse_triples(self.request.tree.value)
        except ParseError:
            return []
        measures = {'accuracy': 1, 'relevance': 0.5}
        return [tree_to_response(tree, measures, self.request.trace)]
