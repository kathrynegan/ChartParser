#!/usr/env/bin python

from chartparser.chart import Chart
from chartparser.agenda import Agenda
from chartparser.grammar import Grammar
from chartparser.lexicon import Lexicon


class Parser():
    def __init__(self, grammar=Grammar(), lexicon=Lexicon()):
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

    @property
    def sentence(self):
        return self._sentence

    @sentence.setter
    def sentence(self, value):
        self._sentence = value

    def parse(self, sentence):
        chart = self._chartparse(sentence)
        parse = self._backtrace(chart)
        return parse

    def _chartparse(self, sentence):
        tokens = sentence.upper().split()
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
        if not chart:
            return
        sentence = chart.sentence
        parse = self._recurse('', sentence)
        return parse

    def _recurse(self, parse, arc):
        if arc.is_terminal:
            return '[.{} {}]'.format(arc.rule.parent, arc.rule.first)
        parse = '[.{} '.format(arc.rule.parent)
        for child in arc.history:
            parse += self._recurse(parse, child)
        parse += ']'
        return parse
