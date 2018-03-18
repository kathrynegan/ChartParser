#!/usr/bin/env python

"""
Kathryn Egan

"""


class Arc:

    def __init__(self, rule, start, end, dot, history=None):
        self.rule = rule
        self.start = start
        self.end = end
        self.dot = dot
        self.history = history if history else [None] * (len(rule) - 1)

    @property
    def identity(self):
        return id(self)

    @property
    def is_terminal(self):
        return self.history == [None] * (len(self.rule) - 1)

    def get_extended(self, key):
        if self._nonextendable(key):
            raise ValueError('Cannot extend {} with {}'.format(self, key))
        extended = Arc(
            self.rule, self.start, key.end,
            self.dot + 1, self.history[::])
        extended.history[self.dot] = key
        return extended

    def _nonextendable(self, other):
        return (
            self.is_complete() or
            self.rule.children[self.dot] != other.rule.parent or
            self.end != other.start)

    def is_complete(self):
        return self.dot == len(self.rule.children)

    def __eq__(self, other):
        try:
            return (
                self.rule == other.rule and
                self.start == other.start and
                self.end == other.end and
                self.dot == other.dot)
        except AttributeError:
            return False

    def __str__(self):
        left = self.rule.parent
        right = list(self.rule.children)
        right.insert(self.dot, '*' + str(self.dot))
        right = ' '.join(right)
        history = [h.identity if h else None for h in self.history]
        return '<{}> {} --> {} {} <{}> {}'.format(
            self.start, left, right, history, self.end, self.identity)

    def __iter__(self):
        yield self
