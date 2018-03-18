#!/usr/bin/env python

"""
Kathryn Egan

The Parser stores the grammar and lexicon of the language, applies the
rules in those systems to a given sentence, and returns a single possible parse
for the sentence if one is found.
"""
from chartparser.language import Grammar, Lexicon
from chartparser.chart import Chart
from chartparser.agenda import Agenda


class Parser:

    def __init__(self, grammar=Grammar(), lexicon=Lexicon()):
        """ Initializes parser with grammar and lexicon.
        Args:
            grammar (Grammar) : Grammar object for parser
            lexicon (Lexicon) : Lexicon object for parser
        """
        self._grammar = grammar
        self._lexicon = lexicon

    @property
    def grammar(self):
        return self._grammar

    @grammar.setter
    def grammar(self, value):
        self._grammar = value

    @property
    def lexicon(self):
        return self._lexicon

    @lexicon.setter
    def lexicon(self, value):
        self._lexicon = value

    def parse(self, sentence):
        """ Chart parses and backtrackes given sentence and returns exactly one
        parse. Throws ValueError if sentence cannot be parsed.
        Args:
            sentence (str) : sentence to parse
        Returns:
            str : parse for given sentence
        """
        tokens = self.tokenize(sentence)
        chart = self._chartparse(*tokens)
        parse = self._backtrace(chart)
        return parse

    @staticmethod
    def tokenize(sentence):
        sentence = sentence.strip().upper().split()
        # space to perform more complex tokenization, if desired
        return sentence

    def _chartparse(self, *tokens):
        """ Chart parses given tokenized sentence. Returns chart if
        tokenized sentence is parseable, otherwise a ValueError is raised.
        The first parse that is successfully completed is returned as the only
        parse for this sentence. Which parse is returned depends on the
        prediction protocol for the agenda.
        Args:
            tokens (list of str) : tokenized sentence
        Returns:
            Chart : Chart for parsed sentence
        """
        # initialize chart and agenda with tokenized sentence
        chart = Chart(tokens)
        agenda = Agenda(tokens, self.lexicon)
        while True:
            current = agenda.choose_next()
            agenda.predict(self.grammar, current)
            agenda.extend(current)
            if current.is_complete():
                chart.add(current)
            else:
                agenda.queue(current)
            if chart.is_sentence:
                return chart

    def _backtrace(self, chart):
        """ Finds the parse in the given chart. Assumes chart
        contains a parsed sentence.
        Args:
            chart (Chart) : chart for a parsable sentence
        Returns:
            str : parse for given chart as a string
        """
        sentence = chart.sentence
        parse = self._recurse('', sentence)
        return parse

    def _recurse(self, parse, arc):
        """ Recurses on the given arc to find the parses of the child arcs.
        Args:
            parse (str) : running parse of the sentence
            arc (Arc) : current arc
        Returns:
            str : updated parse
        """
        if arc.rule.is_terminal:
            return '[.{} {}]'.format(arc.rule.parent, arc.rule.first)
        parse = '[.{} '.format(arc.rule.parent)
        for child in arc.history:
            parse += self._recurse(parse, child)
        parse += ']'
        return parse
