#!/usr/bin/env python

"""
Kathryn Egan

"""
from chartparser.arc import Arc


class Agenda:

    def __init__(self, tokens, lexicon):
        self.agenda = []
        for index, token in enumerate(tokens):
            for terminal in lexicon[token]:
                arc = Arc(
                    terminal, start=index,
                    end=index + 1, dot=1, history=None)
                self.agenda.append(arc)

    def choose_next(self):
        index = self._choice_protocol()
        iterations = len(self)
        iteration = 0
        while True:
            current = self.agenda.pop(index)
            if current.is_complete():
                return current
            self.agenda.append(current)
            iteration += 1
            if iteration > iterations:
                raise ValueError('Agenda exhausted, no parse found.')

    def _choice_protocol(self):
        return 0

    def predict(self, grammar, current):
        if not current.is_complete():
            return
        try:
            predicted = grammar[current.rule.parent]
        except KeyError:  # no rules for this key
            return
        else:
            # create an arc for each rule for current key
            for i, rule in enumerate(predicted):
                arc = Arc(rule, current.start, current.start, 0)
                self.agenda.append(arc)

    def extend(self, current):
        for arc in self.agenda:
            try:
                self.agenda.append(arc.get_extended(current))
            except ValueError:
                continue

    def __iter__(self):
        for arc in self.agenda:
            yield arc

    def __str__(self):
        return '\n'.join([str(arc) for arc in self.agenda])

    def __len__(self):
        return len(self.agenda)
