#!/usr/bin/env python

"""
Kathryn Egan

Language is a super class that provides some standard functionality to
Grammar and Lexicon, which are two similar but distinct aspects of language:
grammar consists of nonterminal rules, while the lexicon of terminal rules.
"""
from chartparser.rule import Terminal, NonTerminal


class Language:
    """ Super class for grammar and lexicon. """

    def __init__(self):
        """ Initializes two data structures to facilitate
        parsing and code handling, one organized by the first
        child mapped to rule, another organized by parent
        mapped to rule. """
        self._bychild = {}
        self._byparent = {}

    def add(self, item):
        """ Adds item to both dictionaries.
        Args:
            item (Rule) : rule to add
        """
        self._bychild.setdefault(item.first, set()).add(item)
        self._byparent.setdefault(item.parent, set()).add(item)

    def __getitem__(self, child):
        """ Returns rule where given child is the first, e.g.
        'DT' is the first child of the rule NP --> DT N.
        Args:
            child (str) : child to look for
        Returns:
            set of Rules : rules mapped to given child as a set
        """
        return self._bychild[child]

    def __iter__(self):
        """ Provides iterator for this RuleDict. """
        for first in self._bychild:
            yield first


class Grammar(Language):
    """ Stores nonterminal rules in this language. """

    def __init__(self):
        """ Initializes grammar according to super class RuleDict. """
        Language.__init__(self)
        self.name = 'grammar'

    @property
    def grammar(self):
        return self._bychild

    def load(self, f):
        """ Loads grammar from given IO stream.
        Args:
            f (IOBase) : any IO stream
        """
        self._bychild = {}
        self._byparent = {}
        for line in f.readlines():
            if not line.strip():
                continue
            rule = NonTerminal.from_string(line)
            self.add(rule)

    def __len__(self):
        """ Returns the number of total rules in this RuleDict.
        Returns:
            int : number of rules in this RuleDict
        """
        return sum([len(value) for value in self.grammar.values()])

    def __str__(self):
        """ Returns rule dictionary as string, sorted by parent
        and then by children, one rule per line.
        Returns:
            str : RuleDict as string
        """
        output = []
        for parent in sorted(self._byparent):
            for rule in sorted(self._byparent[parent]):
                output.append(str(rule))
        return '\n'.join(output)


class Lexicon(Language):
    """ Stores terminal rules in this language. """

    def __init__(self):
        """ Initializes lexicon according to super class RuleDict. """
        Language.__init__(self)
        self.name = 'lexicon'

    @property
    def lexicon(self):
        return self._bychild

    def load(self, f):
        """ Loads lexicon from given IO stream.
        Args:
            f (IOBase) : any IO stream
        """
        self._bychild = {}
        self._byparent = {}
        for line in f.readlines():
            if not line.strip():
                continue
            rule = Terminal.from_string(line)
            self.add(rule)

    def __len__(self):
        """ Returns the number of unique words in this lexicon.
        Returns:
            int : number of unique words
        """
        return len(self.lexicon)

    def __str__(self):
        """ Returns lexicon as string, sorted by word and then
        by part of speech, one word-pos pair per line.
        Returns:
            str : lexicon as string
        """
        output = []
        for token in sorted(self.lexicon):
            for terminal in sorted(self.lexicon[token]):
                output.append('{} : {}'.format(token, terminal.pos))
        return '\n'.join(output)
