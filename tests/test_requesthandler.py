from unittest import TestCase
from ppp_datamodel.communication import Request
from ppp_datamodel import Triple, Resource, Missing
from ppp_libmodule.tests import PPPTestCase

from ppp_datamodel_notation_parser import app

class RequestHandlerTest(PPPTestCase(app)):
    def testRH(self):
        j = {'id': '1', 'language': 'en', 'measures': {}, 'trace': [],
             'tree': {'type': 'sentence', 'value': '(foo, bar, ?)'}}

        answers = self.request(j)
        self.assertEqual(len(answers), 1, answers)

        self.assertEquals(answers[0].tree,
                Triple(
                    Resource('foo'),
                    Resource('bar'),
                    Missing()))
