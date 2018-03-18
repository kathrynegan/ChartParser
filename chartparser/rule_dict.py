#!/usr/bin/env python

"""
Kathryn Egan
"""

from chartparser.rule import Terminal
from chartparser.rule import NonTerminal


class RuleDict:

    def __init__(self):
        self._bychild = {}
        self._byparent = {}

    def add(self, item):
        self._bychild.setdefault(item.first, set()).add(item)
        self._byparent.setdefault(item.parent, set()).add(item)

    def __str__(self):
        output = []
        for parent in sorted(self._byparent):
            for rule in sorted(self._byparent[parent]):
                output.append(str(rule))
        return '\n'.join(output)

    def __getitem__(self, item):
        return self._bychild[item]

    def __iter__(self):
        for first in self._bychild:
            yield first

    def __len__(self):
        return sum([len(value) for value in self._bychild.values()])


class Grammar(RuleDict):

    def __init__(self):
        RuleDict.__init__(self)
        self.name = 'grammar'

    @property
    def grammar(self):
        return self._bychild

    def load(self, f):
        self._bychild = {}
        self._byparent = {}
        for line in f.readlines():
            if not line.strip():
                continue
            rule = NonTerminal.from_string(line)
            self.add(rule)


class Lexicon(RuleDict):

    def __init__(self):
        """ Initializes lexicon."""
        RuleDict.__init__(self)
        self.name = 'lexicon'

    @property
    def lexicon(self):
        return self._bychild

    def load(self, f):
        self._bychild = {}
        self._byparent = {}
        for line in f.readlines():
            if not line.strip():
                continue
            rule = Terminal.from_string(line)
            self.add(rule)

    def __len__(self):
        return len(self.lexicon)

    def __str__(self):
        output = []
        for token in sorted(self.lexicon):
            for terminal in sorted(self.lexicon[token]):
                output.append('{} : {}'.format(token, terminal.pos))
        return '\n'.join(output)
