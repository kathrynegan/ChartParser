#!/usr/bin/env python

"""
Kathryn Egan

The Chart keeps track of all possible parses for the given tokenized
sentence.
"""


class Chart:

    def __init__(self, tokens):
        """ Initializes empty chart with given tokens.
        Args:
            tokens (list of str) : tokenized sentence
        """
        self._chart = []
        self._tokens = tokens
        self._sentence = None

    @property
    def sentence(self):
        """ Arc representing a parsed sentence for this chart.
        Returns:
            Arc : arc representing a parsed sentence
        """
        return self._sentence

    @sentence.setter
    def sentence(self, arc):
        """ Sets sentence to an arc representing a parsed sentence for this chart.
        Args:
            arc (Arc) : arc representing a parsed sentence
        """
        self._sentence = arc

    @property
    def is_sentence(self):
        """ Returns whether this chart contains a complete sentence.
        Returns:
            bool : True if chart contains complete sentence, False otherwise
        """
        return self.sentence is not None

    def add(self, arc):
        """ Adds given arc to the chart. If the given arc represents
        a complete parsed sentence, updates sentence variable.
        Args:
            arc (Arc) : arc to add to chart
        """
        if arc in self:
            return
        self._chart.append(arc)
        if arc.rule.parent == 'S' and (arc.start, arc.end) == (0, len(self)):
            self.sentence = arc

    def __contains__(self, arc):
        """ Returns whether given arc is in this chart.
        Args:
            arc (Arc) : arc to look for
        Returns:
            bool : True if given arc is in this chart, False otherwise
        """
        return arc in self._chart

    def __iter__(self):
        """ Provides iterator on this chart. """
        for arc in self._chart:
            yield arc

    def __len__(self):
        """ Returns the number of tokens in the sentence for this chart. """
        return len(self._tokens)

    def __str__(self):
        """ Returns this chart as a string representing all complete
        arcs found in chart and their spans in teh sentence.
        Returns:
            str : this chart as a string
        """
        output = ['    '.join([str(x) for x in range(len(self) + 1)])]
        for arc in self:
            line = []
            for i in range(len(self)):
                line.append('-' if arc.start < i < arc.end else ' ')
                line.append(('-' if arc.start <= i < arc.end else ' ') * 4)
            output.append('{}  {}'.format(''.join(line), arc.rule))
        output = '\n'.join(output)
        return output
