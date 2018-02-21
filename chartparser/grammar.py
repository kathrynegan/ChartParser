#!/usr/bin/env python

"""
Kathryn Egan

"""
from rule import Rule


class Grammar:

    def __init__(self):
        self.grammar = {}  # first terminal mapped to rule
        self.headfirst = {}  # parent mapped to children

    def import_grammar(self, f):
        self.grammar = {}
        for line in f.readlines():
            try:
                self.add(line)
            except ValueError:
                continue

    def first_node(self, first):
        return self.grammar[first]

    def add(self, *nodes):
        rule = Rule(*nodes)
        self.grammar.setdefault(rule.first, set()).add(rule)
        self.headfirst.setdefault(rule.parent, set()).add(rule)
        return True

    def __str__(self):
        output = []
        for parent in sorted(self.headfirst):
            for rule in sorted(self.headfirst[parent]):
                output.append(str(rule))
        return '\n'.join(output)

    def __getitem__(self, item):
        return self.grammar[item]

    def __iter__(self):
        for first in self.grammar:
            yield first

    def __bool__(self):
        return self.grammar != {}
