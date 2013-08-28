# -*- coding: utf-8 -*-
import os
import unittest
from parsimonious import Grammar
from parsimonious.nodes import Node, RegexNode


here = os.path.abspath(os.path.dirname(__file__))
QUERY_PEG = os.path.join(here, 'query.peg')


class QueryPEGTestCase(unittest.TestCase):
    # Simple test to ensure the 'query.peg' file loads properly.

    @property
    def grammar(self):
        if not hasattr(self, '_grammar'):
            with open(QUERY_PEG, 'r') as fb:
                grammar = Grammar(fb.read())
            self._grammar = grammar
        return self._grammar

    def test_term_matching(self):
        gram = self.grammar

        # Simple term matching
        text = "grumble"
        node_tree = gram['term'].parse(text)
        self.assertEqual(node_tree,
                         RegexNode('term', text, 0, len(text)),
                         node_tree)
        self.assertEqual(
            gram['term'].parse(text).match.group(),
            text)

        # Quoted single term matching, should respond the same way as
        #   the simple term matching.
        text = "'grumble'"
        match_text = text[1:len(text)-1]
        node_tree = gram['quoted_term'].parse(text)
        self.assertEqual(node_tree,
                         Node('quoted_term', text, 0, len(text), children=[
                             Node('quote', text, 0, 1, children=[Node('', text, 0, 1)]),
                             # Grouping '()' node.
                             Node('', text, 1, 8, children=[
                                 # ZeroOrMore '*' node.
                                 Node('', text, 1, 8, children=[
                                     RegexNode('term', text, 1, 8),
                                     ]),
                                 ]),
                             Node('quote', text, 8, 9, children=[Node('', text, 8, 9)])
                             ]),
                         node_tree)
        self.assertEqual(node_tree.children[1].text,
            match_text)


        # Two quoted term matching, should respond as one term value.
        text = "'grumble wildly'"
        match_text = text[1:len(text)-1]
        node_tree = gram['quoted_term'].parse(text)
        self.assertEqual(node_tree,
                         Node('quoted_term', text, 0, len(text), children=[
                             Node('quote', text, 0, 1, children=[Node('', text, 0, 1)]),
                             # Grouping '()' node.
                             Node('', text, 1, 15, children=[
                                 # ZeroOrMore '*' nodes.
                                 Node('', text, 1, 8, children=[
                                     RegexNode('term', text, 1, 8),
                                     ]),
                                 Node('', text, 8, 9, children=[
                                     RegexNode('space', text, 8, 9),
                                     ]),
                                 Node('', text, 9, 15, children=[
                                     RegexNode('term', text, 9, 15),
                                     ]),
                                 ]),
                             Node('quote', text, 15, 16, children=[Node('', text, 15, 16)]),
                             ]),
                         node_tree)
        self.assertEqual(node_tree.children[1].text,
                         match_text)
