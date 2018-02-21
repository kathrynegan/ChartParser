#!/usr/bin/env python

"""
Kathryn Egan

"""


class Chart:

    def __init__(self, tokens):
        self._chart = []
        self._tokens = tokens
        self._sentence = None

    @property
    def length(self):
        return len(self._tokens)

    @property
    def sentence(self):
        return self._sentence

    @sentence.setter
    def sentence(self, boolean):
        self._sentence = boolean

    @property
    def is_sentence(self):
        return self.sentence is not None

    def add(self, arc):
        if arc in self:
            return
        self._chart.append(arc)
        if arc.rule.parent == 'S' and (arc.start, arc.end) == (0, self.length):
            self.sentence = arc

    def __contains__(self, arc):
        return arc in self._chart

    def __iter__(self):
        for arc in self._chart:
            yield arc

    def __str__(self):
        output = ['    '.join([str(x) for x in range(self.length + 1)])]
        for arc in self:
            line = []
            for i in range(self.length):
                line.append('-' if arc.start < i < arc.end else ' ')
                line.append(('-' if arc.start <= i < arc.end else ' ') * 4)
            output.append('{}  {}'.format(''.join(line), arc.rule))
        output = '\n'.join(output)
        return output
