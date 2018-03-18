#!/usr/bin/env python

"""
Kathryn Egan

The Agenda keeps a running list of all the arcs eligible for
adding to the chart or extending during parsing.
"""
from chartparser.arc import Arc


class Agenda:

    def __init__(self, tokens, lexicon):
        """ Initializes Agenda object with all the terminal
        arcs associated with the given tokens and according
        to the rules defined in the given lexicon.
        Args:
            tokens (list of str) : list of words in sentence
            lexicon (Lexicon) : lexicon for this language
        """
        self.agenda = []
        for index, token in enumerate(tokens):
            for terminal in lexicon[token]:
                arc = Arc(
                    terminal, start=index,
                    end=index + 1, dot=1, history=None)
                self.agenda.append(arc)

    def choose_next(self):
        """ Chooses the next complete arc to use as the key
        to try to extend other arcs. Raises ValueError if all arcs
        have been examined and none are complete (i.e. no parse).
        Returns:
            Arc : next complete Arc in current agenda
        """
        index = self._choice_protocol()
        iterations = len(self)
        iteration = 0
        while True:
            current = self.agenda.pop(index)
            if current.is_complete():
                return current
            self.agenda.append(current)
            iteration += 1
            if iteration > iterations:
                raise ValueError('Agenda exhausted, no parse found.')

    def _choice_protocol(self):
        """ Choice protocol can be any rule-based or stochastic
        system for choosing the next arc to use to extend other
        arcs in the agenda. The current protocol is simply
        to choose the first one off the list.
        Returns:
            int : index of chosen arc
        """
        # space to add more complex choice algorithms, if desired
        return 0

    def predict(self, grammar, current):
        """ Adds all nonterminal rules that could be
        extended by the current arc to the agenda according
        to the given grammar.
        Args:
            grammar (Grammar) : grammar for this language
            current (Arc) : current arc to look up in grammar
        """
        if not current.is_complete():
            return
        try:
            predicted = grammar[current.rule.parent]
        except KeyError:  # no rules for this key
            return
        else:
            # create an arc for each rule for current key
            for i, rule in enumerate(predicted):
                arc = Arc(rule, current.start, current.start, 0)
                self.agenda.append(arc)

    def extend(self, current):
        """ Uses current arc to extend any extendable arcs
        in the agenda. Extendable arcs are copied and their copies
        are extended so the original arc can remain for extension
        by other arcs further in the process.
        Args:
            current (Arc) : current arc to extend other arcs with
        """
        for arc in self.agenda:
            try:
                self.agenda.append(arc.get_extended(current))
            except ValueError:
                continue

    def __iter__(self):
        """ Provides iterator on this agenda. """
        for arc in self.agenda:
            yield arc

    def __str__(self):
        """ Returns this agenda as a string.
        Returns:
            str : agenda as string
        """
        return '\n'.join([str(arc) for arc in self.agenda])

    def __len__(self):
        """ Returns the number of arcs in this agenda.
        Returns:
            int : number of arcs in agenda
        """
        return len(self.agenda)
