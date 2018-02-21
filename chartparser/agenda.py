#!/usr/bin/env python

"""
Kathryn Egan

"""
from rule import Rule
from arc import Arc


class Agenda:

    def __init__(self, tokens, lexicon):
        self.agenda = []
        for index, token in enumerate(tokens):
            for pos in lexicon.get_pos(token):
                arc = Arc(
                    Rule(pos, token), start=index,
                    end=index + 1, dot=1, history=None)
                self.queue(arc)
        self.last = None

    def choose_next(self):
        index = self._choice_protocol()
        iterations = len(self)
        iteration = 0
        while True:
            current = self.agenda.pop(index)
            if current.is_complete():
                return current
            self.queue(current)
            iteration += 1
            if iteration > iterations:
                raise ValueError('Agenda exhausted, no parse found.')

    def _choice_protocol(self):
        return 0

    def predict(self, grammar, current):
        if not current.is_complete():
            return
        try:
            predicted = grammar.first_node(current.rule.parent)
        except KeyError:  # no rules for this key
            return
        # create an arc for each rule for current key
        for i, rule in enumerate(predicted):
            arc = Arc(rule, current.start, current.start, 0)
            self.queue(arc)

    def extend(self, current):
        for arc in self.agenda:
            try:
                self.queue(arc.get_extended(current))
            except ValueError:
                continue

    def queue(self, item):
        self.agenda.append(item)

    def __str__(self):
        return '\n'.join([str(arc) for arc in self.agenda])

    def __len__(self):
        return len(self.agenda)
