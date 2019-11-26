#!/usr/bin/env python

"""
Kathryn Egan

Rule is a super class that provides standard functionality for Terminal and
NonTerminal. Terminal is limited to one parent and one child and is
essentially a part of the lexicon, or spoken form of language. NonTerminal
is limited to one parent but may have any number of children as defined
by the language. NonTerminal is the grammar, or unspoken rules of language.
"""


class Rule:
    """ Super class for terminal and nonterminal rules. """

    def __init__(self, *nodes):
        """ Initializes rule of any length greater than two. Raises
        ValueError if less than two nodes are provided. Assumes the
        first node in nodes is the single parent node, while nodes
        at index 1+ are the children, in order. Raises ValueError if
        any node is divisible by whitespace.
        Args:
            nodes (list of str) :
                list of nodes in this rule in the form
                [parent, child1, child2, ... childn]
        """
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
        """ Returns the first child in this rule.
        Returns:
            str : first child in rule
        """
        return self._rule[1]

    @property
    def parent(self):
        """ Returns the parent in this rule.
        Returns:
            str : parent in this rule
        """
        return self._rule[0]

    @property
    def children(self):
        """ Returns all the children in this rule.
        Returns:
            list of str : list of children in rule
        """
        return self._rule[1:]

    def __eq__(self, other):
        """ Returns whether this rule and the given
        rule are the same, meaning the parent and all
        children are represented by same children in order.
        Args:
            other (Rule) : rule to compare
        Returns:
            bool : True if parent and all children are same, False otherwise
        """
        return self.rule == other.rule

    def __lt__(self, other):
        """ Returns whether this rule is less than the given
        rule alphabetically.
        Args:
            other (Rule) : rule to compare
        Returns:
            bool :
                True if this rule is less than other rule alphabetically
                False otherwise
        """
        return self.rule < other.rule

    def __hash__(self):
        """ Returns a hash of this rule so that it can be used
        in a dicionary or set.
        Return:
            hash : hash of this rule
        """
        return hash(self.rule)

    def __len__(self):
        """ Returns the length of this rule, including the parent.
        Returns:
            int : length of this rule
        """
        return len(self.rule)


class NonTerminal(Rule):

    def __init__(self, *nodes):
        """ Initializes NonTerminal rule with super class. """
        Rule.__init__(self, *nodes)

    @property
    def is_sentence(self):
        """ Returns whether this rule represents a sentence.
        Returns:
            bool : True if this rule make a sentence, False otherwise
        """
        return self.parent == 'S'

    @property
    def is_terminal(self):
        """ Returns False - this is not a terminal rule. """
        return False

    @classmethod
    def from_string(cls, rule):
        """ Creates a NonTerminal rule from a string. Raises
        ValueError if the left side of the rule does not have
        exactly one node or the right side does not have at least
        one node.
        Args:
            rule (str) : rule as a string
        Returns:
            NonTerminal : give rule as a NonTerminal object
        """
        left, right = rule.split('-->')
        left = left.split()
        right = right.split()
        if len(left) != 1:
            raise ValueError('Must provide at least one parent node')
        if len(right) < 1:
            raise ValueError('Must provide at least one child node')
        return cls(*left + right)

    def __str__(self):
        """ Returns this nonterminal rule as a string.
        Returns:
            str : this rule as a string
        """
        return '{} --> {}'.format(self.parent, ' '.join(self.children))


class Terminal(Rule):

    def __init__(self, *nodes):
        """ Initializes Terminal rule with super class.
        Raises ValueError if there is not exactly one token
        and one part of speech. """
        Rule.__init__(self, *nodes)
        if len(self.rule) != 2:
            raise ValueError(
                'Terminal must consist of one token and one part of speech.')

    @property
    def token(self):
        """ Returns the token or word in this rule.
        Returns:
            str : token in rule
        """
        return self.first

    @property
    def pos(self):
        """ Returns the part of speech in this rule.
        Returns:
            str : part of speech in rule
        """
        return self.parent

    @property
    def is_terminal(self):
        """ Returns True - this rule is terminal. """
        return True

    @classmethod
    def from_string(cls, terminal):
        """ Creates a Terminal rule from a string. Raises
        ValueError if there is not exactly one token and one
        part of speech in this rule.
        Args:
            rule (str) : rule as a string
        Returns:
            NonTerminal : give rule as a NonTerminal object
        """
        token, pos = terminal.split(':')
        token = token.strip().upper()
        pos = pos.strip().upper()
        if len(token.split()) != 1:
            raise ValueError('Word must be exactly one nuclear entry.')
        if len(pos.split()) != 1:
            raise ValueError(
                'Part of speech must be exactly one nuclear entry.')
        return cls(pos, token)

    def __str__(self):
        """ Returns this terminal rule as a string.
        Returns:
            str : this rule as a string
        """
        return '{} : {}'.format(self.token, self.pos)
