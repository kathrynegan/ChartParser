#!/usr/bin/env python

"""
Kathryn Egan

"""


class Rule:

    def __init__(self, *nodes):
        nodes = [n for node in nodes for n in node.split('-->')]
        nodes = [n.upper() for node in nodes for n in node.split()]
        if len(nodes) < 2:
            raise ValueError('Rule must have at least two nodes')
        self._rule = tuple(nodes)

    @property
    def first(self):
        return self._rule[1]

    @property
    def parent(self):
        return self._rule[0]

    @property
    def children(self):
        return self._rule[1:]

    @property
    def rule(self):
        return self._rule

    def __str__(self):
        return '{} --> {}'.format(self.parent, ' '.join(self.children))

    def __eq__(self, other):
        return self.rule == other.rule

    def __lt__(self, other):
        return self.rule < other.rule

    def __hash__(self):
        return hash(self.rule)

    def __len__(self):
        return len(self.rule)  # parent

    @classmethod
    def from_string(cls, *rule):
        left, right = rule[0].split('-->')
        left = left.split()
        right = right.split()
        if len(left) != 1:
            raise ValueError('Must provide at least one parent node')
        if len(right) < 1:
            raise ValueError('Must provide at least one child node')
        return cls(*left + right)

    @classmethod
    def from_pair(cls, *rule):
        parent, children = rule[0], rule[1]
        children = children.split()
        if len(children) < 1:
            raise ValueError('Must provide at least one child node')
        return cls(*[parent] + children)

    def is_sentence(self):
        return self.parent == 'S'
