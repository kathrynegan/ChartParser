#!/usr/bin/env python

"""
Kathryn Egan

"""


class Rule:

    def __init__(self, *nodes):
        if len(nodes) < 2:
            raise ValueError('Rule must have at least two nodes')
        cleaned = []
        for node in nodes:
            if len(node.split()) > 1:
                raise ValueError(
                    'No node may have two or more items '
                    'divisible by whitespace.')
            cleaned.append(node.upper())
        self._rule = tuple(cleaned)

    @property
    def rule(self):
        return self._rule

    @property
    def first(self):
        return self._rule[1]

    @property
    def parent(self):
        return self._rule[0]

    @property
    def children(self):
        return self._rule[1:]

    def __eq__(self, other):
        return self.rule == other.rule

    def __lt__(self, other):
        return self.rule < other.rule

    def __hash__(self):
        return hash(self.rule)

    def __len__(self):
        return len(self.rule)  # parent


class NonTerminal(Rule):

    def __init__(self, *nodes):
        Rule.__init__(self, *nodes)

    @property
    def is_sentence(self):
        return self.parent == 'S'

    @classmethod
    def from_string(cls, rule):
        left, right = rule.split('-->')
        left = left.split()
        right = right.split()
        if len(left) != 1:
            raise ValueError('Must provide at least one parent node')
        if len(right) < 1:
            raise ValueError('Must provide at least one child node')
        return cls(*left + right)

    def __str__(self):
        return '{} --> {}'.format(self.parent, ' '.join(self.children))


class Terminal(Rule):

    def __init__(self, *terminal):
        Rule.__init__(self, *terminal)
        if len(self.rule) != 2:
            raise ValueError(
                'Terminal must consist of one token and one part of speech.')

    @property
    def token(self):
        return self.first

    @property
    def pos(self):
        return self.parent

    @classmethod
    def from_string(cls, terminal):
        token, pos = terminal.split(':')
        token = token.strip().upper()
        pos = pos.strip().upper()
        if not token or len(token.split()) > 1:
            raise ValueError('Word must be exactly one nuclear entry.')
        if not pos or len(pos.split()) > 1:
            raise ValueError(
                'Part of speech must be exactly one nuclear entry.')
        return cls(pos, token)

    def __str__(self):
        return '{} : {}'.format(self.token, self.pos)


# class Rule:

#     def __init__(self, *nodes):
#         # nodes = [n for node in nodes for n in node.split('-->')]
#         # nodes = [n.upper() for node in nodes for n in node.split()]
#         if len(nodes) < 2:
#             raise ValueError('Rule must have at least two nodes')
#         cleaned = []
#         for node in nodes:
#             if len(node.split()) > 1:
#                 raise ValueError(
#                     'No node may have two or more tokens divisible by whitespace.')
#             cleaned.append(node.upper())
#         self._rule = tuple(cleaned)

#     @property
#     def first(self):
#         return self._rule[1]

#     @property
#     def parent(self):
#         return self._rule[0]

#     @property
#     def children(self):
#         return self._rule[1:]

#     @property
#     def rule(self):
#         return self._rule

#     @property
#     def is_sentence(self):
#         return self.parent == 'S'

#     def __str__(self):
#         return '{} --> {}'.format(self.parent, ' '.join(self.children))

#     def __eq__(self, other):
#         return self.rule == other.rule

#     def __lt__(self, other):
#         return self.rule < other.rule

#     def __hash__(self):
#         return hash(self.rule)

#     def __len__(self):
#         return len(self.rule)  # parent

#     @classmethod
#     def from_string(cls, rule):
#         left, right = rule.split('-->')
#         left = left.split()
#         right = right.split()
#         if len(left) != 1:
#             raise ValueError('Must provide at least one parent node')
#         if len(right) < 1:
#             raise ValueError('Must provide at least one child node')
#         return cls(*left + right)
