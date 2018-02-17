"""
Kathryn Nichols
December 12, 2012
CSE 415
Project

This program used Tkinter to provide a GUI of a chart parser. The user
can pass a lexicon and grammar file as arguments (in that order) to the
program at startup or import from the main window.

There are many restrictions on the form of the input, please see the
project report for details before using. Also see report for details
on features and functions and a discussion of chart parsing.

UPDATED: 2/13/2018

Python 3
"""
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog


class Grammar:

    def __init__(self):
        self.grammar = {}  # first terminal mapped to rule
        self.headfirst = {}  # parent mapped to children

    def import_grammar(self, f):
        self.grammar = {}
        for line in f.readlines():
            try:
                self.add(line)
            except ValueError:
                continue

    def first_node(self, first):
        return self.grammar[first]

    def add(self, *nodes):
        rule = Rule(*nodes)
        self.grammar.setdefault(rule.first, set()).add(rule)
        self.headfirst.setdefault(rule.parent, set()).add(rule)
        return True

    def __str__(self):
        output = []
        for parent in sorted(self.headfirst):
            for rule in sorted(self.headfirst[parent]):
                output.append(str(rule))
        return '\n'.join(output)

    def __getitem__(self, item):
        return self.grammar[item]

    def __iter__(self):
        for first in self.grammar:
            yield first

    def __bool__(self):
        return self.grammar != {}


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


class Arc:

    def __init__(self, rule, start, end, dot, history=None):
        self.rule = rule
        self.start = start
        self.end = end
        self.dot = dot
        if history:
            self.history = history
        else:
            self.history = [None] * (len(rule) - 1)

    @property
    def identity(self):
        return id(self)

    @property
    def no_history(self):
        return self.history.count(None) > 0

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
        return (
            self.rule == other.rule and
            self.start == other.start and
            self.end == other.end and
            self.dot == other.dot)

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


class Agenda:

    def __init__(self, tokens, lexicon):
        self.agenda = []
        for index, token in enumerate(tokens):
            for pos in lexicon.get_pos(token):
                arc = Arc(
                    Rule(pos, token), start=index,
                    end=index + 1, dot=1, history=None)
                self.queue(arc)
        self.last = None

    def choose_next(self):
        index = self._choice_protocol()
        iterations = len(self)
        iteration = 0
        while True:
            current = self.agenda.pop(index)
            if current.is_complete():
                return current
            self.queue(current)
            iteration += 1
            if iteration > iterations:
                raise ValueError('Agenda exhausted, no parse found.')

    def _choice_protocol(self):
        return 0

    def predict(self, grammar, current):
        if not current.is_complete():
            return
        try:
            predicted = grammar.first_node(current.rule.parent)
        except KeyError:  # no rules for this key
            return
        # create an arc for each rule for current key
        for i, rule in enumerate(predicted):
            arc = Arc(rule, current.start, current.start, 0)
            self.queue(arc)

    def extend(self, current):
        for arc in self.agenda:
            try:
                self.queue(arc.get_extended(current))
            except ValueError:
                continue

    def queue(self, item):
        self.agenda.append(item)

    def __str__(self):
        return '\n'.join([str(arc) for arc in self.agenda])

    def __len__(self):
        return len(self.agenda)


class InteractiveParser:

    def __init__(self, root):
        self.root = root
        self.grammar = Grammar()
        self.lexicon = Lexicon()
        # self.sentence = StringVar(master=widget)
        # self._sentence = StringVar()
        self.root.title("Interactive Parser")
        self.mainframe = ttk.Frame(self.root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        ttk.Button(
            self.mainframe, text='Show Lexicon', width=15,
            command=self.show_lexicon).grid(column=1, row=1, sticky=W)
        ttk.Button(
            self.mainframe, text='Show Grammar', width=15,
            command=self.show_grammar).grid(column=1, row=2, sticky=W)
        ttk.Button(
            self.mainframe, text='Add a Word', width=15,
            command=self.add_lexical_entry).grid(column=2, row=1, sticky=W)
        ttk.Button(
            self.mainframe, text='Add a Rule', width=15,
            command=self.add_grammar_rule).grid(column=2, row=2, sticky=W)
        ttk.Button(
            self.mainframe, text='Import Lexicon', width=15,
            command=self.import_lexicon).grid(column=3, row=1, sticky=W)
        ttk.Button(
            self.mainframe, text='Import Grammar', width=15,
            command=self.import_grammar).grid(column=3, row=2, sticky=W)
        ttk.Button(
            self.mainframe, text='Search for Word', width=15,
            command=self.search).grid(column=1, row=8, sticky=W)
        self._sentence = ttk.Entry(
            self.mainframe, width=15)  #, textvariable=lambda: self._sentence)
        self._sentence.grid(column=2, row=5, columnspan=2, sticky=(W, E))
        ttk.Button(
            self.mainframe, text='Parse', width=15,
            command=self.parse).grid(column=3, row=6, sticky=E)
        ttk.Button(
            self.mainframe, text='Exit', width=10,
            command=exit).grid(column=3, row=8, sticky=E)
        ttk.Label(
            self.mainframe, text='Enter a sentence:').grid(column=1, row=5, sticky=E)
        ttk.Label(
            self.mainframe, text='').grid(column=1, row=3, sticky=E)
        ttk.Label(
            self.mainframe, text='').grid(column=1, row=7, sticky=E)
        # add padding around every widget
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        # ensure user doesn't have to click first
        self._sentence.focus()
        # self.root.bind('<Return>', self.parse)

    @classmethod
    def no_GUI(cls):
        cls.grammar = Grammar()
        cls.lexicon = Lexicon()
        return cls

    @property
    def sentence(self):
        try:
            return self._sentence.get()
        except AttributeError:
            return self._sentence

    @sentence.setter
    def sentence(self, value):
        self._sentence = value

    def show_lexicon(self):
        self._show(self.lexicon)

    def show_grammar(self):
        self._show(self.grammar)

    def _show(self, obj):
        message = str(obj) if obj else "Nothing to show."
        messagebox.showinfo(message=message)

    def parse(self):
        if not self.sentence:
            messagebox.showinfo(message="There is no sentence to parse.")
            return
        if not self.lexicon:
            messagebox.showinfo(message="There is no lexicon.")
            return
        if not self.grammar:
            messagebox.showinfo(message="There is no grammar.")
            return
        try:
            chart = self._chartparse(self.sentence)
        except KeyError:
            messagebox.showinfo(message="Unknown words found.")
        except ValueError:
            messagebox.showinfo(message="Sentence failed to parse.")
        else:
            parse = self._backtrace(chart)
            parse = self._to_string(parse)
            messagebox.showinfo(message=parse)

    def _to_string(self, parse):
        return str(parse)

    def _chartparse(self, sentence):
        tokens = sentence.upper().split()
        chart = Chart(tokens)
        agenda = Agenda(tokens, self.lexicon)
        while True:
            current = agenda.choose_next()
            agenda.predict(self.grammar, current)
            agenda.extend(current)
            if current.is_complete():
                chart.add(current)
            else:
                agenda.queue(current)
            if chart.is_sentence:
                return chart

    def _backtrace(self, chart):
        sentence = chart.sentence
        parse = self._recurse([sentence], sentence)
        return parse

    def _recurse(self, parse, node):
        for child in node.history:
            if child is None:
                continue
            parse.append(child)
            parse = self._recurse(parse, child)
        return parse

    def import_lexicon(self):
        self._import(self.lexicon.import_lexicon, 'lexicon')

    def import_grammar(self):
        self._import(self.grammar.import_grammar, 'grammar')

    def _import(self, function, name):
        file = filedialog.askopenfilename()
        if not file:
            return
        with open(file, 'r') as f:
            try:
                module(f)
            except Exception as e:
                messagebox.showinfo(
                    message="An fatal error occurred while reading " +
                    "the file..\n{}".format(name, e))
            else:
                messagebox.showinfo(
                    message="{} successfully imported.".format(file))

    def add_lexical_entry(self):
        try:
            word = self._prompt('a word')
            pos = self._prompt('a part of speech')
        except ValueError:
            return
        word = word.strip().upper()
        pos = pos.strip().upper()
        self.lexicon.add(word, pos)

    def _prompt(self, name):
        prompt = "Please enter {}:".format(name)
        while True:
            answer = simpledialog.askstring(title="", prompt=prompt)
            # user has cancelled
            if answer is None:
                raise ValueError
            if answer.strip():
                return answer

    def add_grammar_rule(self):
        try:
            parent = self._prompt('the parent')
            children = self._prompt('the children separated by spaces')
        except ValueError:
            return
        try:
            self.grammar.add(parent, children)
        except ValueError:
            messagebox.showinfo(
                message="Failed to add to the grammar.")

    def search(self):
        word = self._prompt('word')
        if not word:
            return
        try:
            pos = self.lexicon.get_pos(word)
        except KeyError:
            messagebox.showinfo(message="That word is not in the lexicon.")
        else:
            message = "The part(s) of speech of {} is/are:\n\n{}"
            message = message.format(word, ', '.join(sorted(pos)))
            messagebox.showinfo(message=message)

    def exit(self):
        for item, name in zip((self.lexicon, self.grammar), ('lexicon', 'grammar')):
            message = "Would you like to save the {}?".format(name)
            if item and messagebox.askyesnocancel(message=message):
                file = filedialog.asksaveasfilename()
                with open(file, 'w') as f:
                    f.write(str(item))
        mainframe.quit()


def main():
    # constructs graphical interface
    root = Tk()
    parser = InteractiveParser(root)
    root.mainloop()


if __name__ == '__main__':
    main()
