#!/usr/bin/env python

"""
Kathryn Egan

"""


class Lexicon:

    def __init__(self):
        self._lexicon = {}  # token mapped to parts of speach
        self._rlexicon = {}  # part of speech mapped to tokens

    @property
    def lexicon(self):
        return self._lexicon

    @property
    def rlexicon(self):
        return self._rlexicon

    def import_lexicon(self, f):
        for line in f.readlines():
            if not line.strip():
                continue
            pos, tokens = line.split(':')
            pos = pos.strip().upper()
            tokens = [token.upper() for token in tokens.split(',') if token]
            for token in tokens:
                self.add(token, pos)

    def add(self, token, pos):
        token = token.strip().upper()
        pos = pos.strip().upper()
        self.lexicon.setdefault(token, set()).add(pos)
        self.rlexicon.setdefault(pos, set()).add(token)

    def has_word(self, word):
        return word.strip().upper() in self.lexicon

    def has_pos(self, pos):
        return pos.strip().upper() in self.rlexicon

    def get_pos(self, word):
        word = word.strip().upper()
        return self.lexicon[word]

    def get_tokens(self, pos):
        pos = pos.strip().upper()
        return self.rlexicon[pos]

    def __str__(self):
        output = []
        for pos in sorted(self.rlexicon):
            tokens = ', '.join(sorted(self.rlexicon[pos]))
            output.append('{} : {}'.format(pos, tokens))
        return '\n'.join(output)

    def __iter__(self):
        for token in self.lexicon:
            yield token

    def __getitem__(self, item):
        return self.lexicon[item]

    def __bool__(self):
        return self.lexicon != {}
