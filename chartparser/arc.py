#!/usr/bin/env python

"""
Kathryn Egan

The Arc tracks which rules are possible in the sentence, their
position in the sentence, and which subrules/nodes they originated from.
"""


class Arc:

    def __init__(self, rule, start, end, dot, history=None):
        """ Initializes Arc with given rule, its start index, end index,
        the "dot", and history of extensions.
        Args:
            rule (Rule) :
                rule that this arc represents, can be Terminal or NonTerminal
            start (int) :
                current start index of this arc within tokenized sentence
            end (int) :
                current end index of this arc within tokenized sentence
            dot (int) :
                index indicating progress of extending this rule with subrules
            history (list of Rules) : list of the rules that extended this rule
        """
        self.rule = rule
        self.start = start
        self.end = end
        self.dot = dot
        self.history = history if history else [None] * (len(rule) - 1)

    @property
    def identity(self):
        return id(self)

    def get_extended(self, key):
        """ Returns an extended version of this arc according to the given
        "key" arc.
        Args:
            key (Arc) : arc by which to extend this arc
        Returns:
            Arc : extended arc
        """
        if self._nonextendable(key):
            raise ValueError('Cannot extend {} with {}'.format(self, key))
        extended = Arc(
            self.rule, self.start, key.end,
            self.dot + 1, self.history[::])
        extended.history[self.dot] = key
        return extended

    def _nonextendable(self, other):
        """ Returns whether this arc is NOT extendable by other given arc.
        Extendable means that this arc is not complete, that its current end
        index is the same as the other arc's current start index, and the
        current child node (indicated by "dot") is the same as the given
        arc's parent node.
        Args:
            other (Arc) : arc to extend this arc with
        Returns:
            bool :
                True if this arc can CANNOT be extended with given arc
                False if this arc CAN be extended with given arc
        """
        return (
            self.is_complete() or
            self.rule.children[self.dot] != other.rule.parent or
            self.end != other.start)

    def is_complete(self):
        """ Returns whether this arc is complete, meaning all of its
        children have been evaluated and extended by other arcs, or is
        otherwise a terminal. This is indicated with a progress "dot" that
        is at the end of the arc.
        Returns:
            bool :  True if this arc is complete, False otherwise
        """
        return self.dot == len(self.rule.children)

    def __eq__(self, other):
        """ Returns whether this arc is equal to given arc in everything
        EXCEPT history, which is ignored.
        Args:
            other (Arc) : arc to compare
        Returns:
            bool :
                True if both arcs are equal in all but history
                False otherwise
        """
        try:
            return (
                self.rule == other.rule and
                self.start == other.start and
                self.end == other.end and
                self.dot == other.dot)
        except AttributeError:
            return False

    def __str__(self):
        """ Returns this arc as a string.
        Returns:
            str : arc as string
        """
        left = self.rule.parent
        right = list(self.rule.children)
        right.insert(self.dot, '*' + str(self.dot))
        right = ' '.join(right)
        history = [h.identity if h else None for h in self.history]
        return '<{}> {} --> {} {} <{}> {}'.format(
            self.start, left, right, history, self.end, self.identity)

    def __iter__(self):
        """ Provides iterator on this arc. """
        yield self
