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
import re
import copy


class Grammar:

    def __init__(self):
        self.grammar = {}  # initial terminal mapped to rule

    def __str__(self):
        output = []
        for terminal in self:
            for rule in self[terminal]:
                children = ' '.join(rule[1:])
                entry = '{} --> {}'.format(rule[0], children)
                output.append(entry)
        return '\n'.join(output)

    def __getitem__(self, item):
        return self.grammar[item]

    def __iter__(self):
        for terminal in self.grammar:
            yield terminal

    def import_grammar(self, f):
        self.grammer = {}
        for line in f.readlines():
            if not line.strip():
                continue
            self.add(line)

    def add(self, rule):
        try:
            parent, children = rule.split('-->')
        except ValueError:
            return False
        parent = parent.strip().upper()
        children = tuple([child.upper() for child in children.split()])
        if not parent or not children:
            return False
        rule = (parent,) + children
        # identify first terminal node
        terminal = children[0]
        self.grammar.setdefault(terminal, set()).add(rule)
        return True


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
        return self.lexicon[word]

    def get_tokens(self, pos):
        return self.rlexicon[pos]


class InteractiveParser:

    def __init__(self):
        self.grammar = Grammar()
        self.lexicon = Lexicon()
        # self.sentence = StringVar(master=widget)
        self._sentence = ''

    @property
    def sentence(self):
        return self._sentence

    @sentence.setter
    def sentence(self, value):
        self._sentence = value

    def show_lexicon(self):
        self._show(self.lexicon)

    def show_grammar(self):
        self._show(self.grammar)

    def _show(self, obj):
        # Shows the lexicon in a window
        if obj:
            message = str(obj)
        else:
            message = "Nothing to show."
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
        if self.check_lexicon():
            parse = self._parse()
            if parse:
                messagebox.showinfo(message=parse)
            else:
                messagebox.showinfo(message="Sentence failed to parse.")

    def _parse(self):
        # sentence = self.sentence.get()
        sentence = self.sentence
        # remove punctuation
        # sentence = re.sub(r'[\.,?\:;"\(\)!&$#]', ' ', sentence)
        tokens = sentence.upper().split()
        edges = self._get_edges(tokens)  # get edges of sentence
        keys = []
        arcs = []
        chart = []
        index = 0
        for token in edges:
            # get parts of speech of words
            pos = self.lexicon.get_pos(token[0])
            # add keys for words to key list
            for pos in self.lexicon.get_tokens(pos):
                # MAKE A KEY OBJECT
                key = [pos, token[1], token[2], index, -1]
                index += 1
                keys.append(key)
            # assess each key on key list
            while len(keys) != 0:
                key = keys.pop(0)
                terminal = key[0]
                try:
                    rules = self.grammar[terminal]
                except KeyError:
                    return
                    # get list of rules starting with key
                # create an arc for each rule and add to arc list
                for rule in rules:
                    tracer = (len(rule) - 1) * [-1]
                    arc = [rule, [key[1], key[1]], 0, tracer]
                    arcs.append(arc)
                # extend each arc and add back to arc list
                temp = []
                for arc in arcs:
                    arc2 = copy.deepcopy(arc)
                    arc2 = self._extend_arc(arc2, key)
                    # arc successfully extended
                    if arc2:
                        temp.append(arc2)
                        # arc is successfully made into a constituent,
                        # update key list to contain constituent, remove arc
                        if arc2[2] == len(arc2[3]):
                            constituent = [
                                arc2[0][0],
                                arc2[1][0],
                                arc2[1][1],
                                index,
                                arc2[3]]
                            index += 1
                            keys.append(constituent)
                            temp.remove(arc2)
                # add extended arcs back to arc list
                arcs.extend(temp)
                # add key to chart
                chart.append(key)
        parsed = False
        initial_symbol = []
        # check for initial symbol
        for key in chart:
            if key[:-2] == ['S', 0, len(tokens)]:
                parsed = True
                initial_symbol = key
        if parsed:
            return self._backtrace(chart, initial_symbol, edges)

    def _extend_arc(self, arc, key):
        # Returns an extended arc if the arc can be
        # extended, otherwise an empty list
        # part of speech of key and next element on arc must match
        # right edge of arc and left edge of key must match
        arc = []
        if arc[0][arc[2] + 1] == key[0] and arc[1][1] == key[1]:
            arc[1][1] = key[2]
            arc[3][arc[2]] = key[3]
            arc[2] += 1
        return arc

    def _get_edges(self, sequence):
        # Returns the keys for this sentence as a list
        edges = []
        i = 0
        for token in sequence:
            key = [token, i, i + 1]
            i += 1
            edges.append(key)
        return edges

    def _backtrace(self, chart, node, edges):
        # Backtrace the chart to get correct parse
        # leaf node found
        if node[4] == -1:
            for edge in edges:
                if edge[1] == node[1]:
                    return '[.{} {} ] '.format(node[0], edge[0])
        # explore children
        else:
            parse = '[.{} '.format(node[0])
            children = self._find_children(chart, node)
            for child in children:
                parse += self._backtrace(chart, child, edges)
            parse += '] '
            return parse

    def _find_children(self, chart, node):
        # Returns a list of the children of the given node
        children = []
        for item in chart:
            if item[3] in node[4]:
                children.append(item)
            if len(children) == len(node[4]):
                break
        return children

    def import_lexicon(self):
        # Prompts user for lexicon file
        self._import(self.lexicon.import_lexicon, 'lexicon')

    def import_grammar(self):
        self._import(self.grammar.import_grammar, 'grammar')

    def _import(self, function, name):
        file = filedialog.askopenfilename()
        with open(file, 'r') as f:
            try:
                module(f)
            except Exception as e:
                messagebox.showinfo(
                    message="An fatalerror occurred while reading " +
                    "the file..\n{}".format(name, e))
            else:
                messagebox.showinfo(
                    message="{} successfully imported.".format(file))

    def check_lexicon(self):
        # Checks whether every word in the sentence is in the lexicon.
        # If there is an unknown word, prompts for user command.
        # Returns true if all words in input are in the lexicon at
        # the termination of the method, False otherwise
        for token in self.sentence.get().split():
            if self.lexicon.has_word(token):
                message = \
                    "The word \"{}\" is not in the lexicon. " +\
                    "Would you like to add it?"
                response = messagebox.askyesno(message=message.format(word))
                if response is None:
                    return
                while True:
                    pos = simpledialog.askstring(
                        title="", prompt="Please enter a part of speech:")
                    if pos is None:
                        return
                    if not pos.strip():
                        continue
                self.lexicon.add(word, pos)
        return True

    def add_lexical_entry(self):
        # Prompts user for a word to add to the lexicon
        word = self._prompt('word')
        if not word:
            return
        pos = self._prompt('part of speech')
        if not pos:
            return
        self.lexicon.add(word, pos)
        message = "{} : {} has been added to the lexicon"
        messagebox.showinfo(message=message.format(pos, word))

    def _prompt(self, name):
        prompt = "Please enter a {}:".format(name)
        while True:
            answer = simpledialog.askstring(
                title="", prompt=prompt)
            # user has cancelled
            if answer is None:
                return
            if not answer.strip():
                continue
        return answer

    # Prompts user for a rule to add to the grammar
    def add_grammar_rule(self):
        rule = self._prompt(
            'rule in the form NONTERMINAL --> TERMINAL1 ' +
            '(TERMINAL2) ... (NONTERMINAL1) ...')
        if rule is None:
            return
        try:
            self.grammar.add(rule)
        except ValueError:
            messagebox.showinfo(
                message="Failed to add {} to the grammar.".format(rule))
        else:
            messagebox.showinfo(
                message="Added {} to the grammar.".format(rule))

    def search(self):
        # Prompts user for a word to search
        if not self.lexicon:
            messagebox.showinfo(message="There is no lexicon.")
            return
        word = self._prompt('word')
        if not word:
            return
        try:
            pos = self.lexicon.get_pos(word)
        except KeyError:
            message = \
                "That word is not in the lexicon. " +\
                "Would you like to add it?"
            if messagebox.askyesno(message=message):
                pos = self._prompt('part of speech')
                if not pos:
                    return
                self.lexicon.add(word, pos)
                message = "{} : {} has been added to the lexicon"
                messagebox.showinfo(message=message.format(pos, word))
        else:
            message = "The part(s) of speech of {} is/are:\n\n{}"
            messagebox.showinfo(message=message.format(word, result))

    def exit(self):
        # Asks user for save file info, exits program.
        for lang_set, name in zip((self.lexicon, self.grammar), ('lexicon', 'grammar')):
            message = "Would you like to save the {}?".format(name)
            if lang_set and messagebox.askyesnocancel(message=message):
                file = filedialog.asksaveasfilename()
                with open(file, 'w') as f:
                    f.write(str(lang_set))
        mainframe.quit()


def main():
    # constructs graphical interface
    root = Tk()
    root.title("Interactive Parser")
    mainframe = ttk.Frame(root, padding='3 3 12 12')
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    parser = InteractiveParser()
    ttk.Button(mainframe, text='Show Lexicon', width=15, command=parser.show_lexicon).grid(column=1, row=1, sticky=W)
    ttk.Button(mainframe, text='Show Grammar', width=15, command=parser.show_grammar).grid(column=1, row=2, sticky=W)
    ttk.Button(mainframe, text='Add a Lexical Entry', width=15, command=parser.add_lexical_entry).grid(column=2, row=1, sticky=W)
    ttk.Button(mainframe, text='Add a Grammar Rule', width=15, command=parser.add_grammar_rule).grid(column=2, row=2, sticky=W)
    ttk.Button(mainframe, text='Import Lexicon', width=15, command=parser.import_lexicon).grid(column=3, row=1, sticky=W)
    ttk.Button(mainframe, text='Import Grammar', width=15, command=parser.import_grammar).grid(column=3, row=2, sticky=W)
    ttk.Button(mainframe, text='Search for Word', width=15, command=parser.search).grid(column=1, row=8, sticky=W)
    sentence_entry = ttk.Entry(mainframe, width=15, textvariable=parser.sentence)
    sentence_entry.grid(column=2, row=5, columnspan=2, sticky=(W, E))
    ttk.Button(mainframe, text='Parse', width=15, command=parser.parse).grid(column=3, row=6, sticky=E)
    ttk.Button(mainframe, text='Exit', width=10, command=exit).grid(column=3, row=8, sticky=E)
    ttk.Label(mainframe, text='Enter a sentence:').grid(column=1, row=5, sticky=E)
    ttk.Label(mainframe, text='').grid(column=1, row=3, sticky=E)
    ttk.Label(mainframe, text='').grid(column=1, row=7, sticky=E)
    # add padding around every widget
    for child in mainframe.winfo_children():
        child.grid_configure(padx=5, pady=5)
    # ensure user doesn't have to click first
    sentence_entry.focus()
    root.bind('<Return>', parser.parse_sentence)

    root.mainloop()


if __name__ == '__main__':
    main()
