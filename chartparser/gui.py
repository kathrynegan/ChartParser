#!/usr/bin/env python

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
from chartparser.parser import Parser
from chartparser.grammar import Grammar
from chartparser.lexicon import Lexicon


class GUI:

    def __init__(self, root):
        self.root = root
        self.grammar = Grammar()
        self.lexicon = Lexicon()
        # self.sentence = StringVar(master=widget)
        # self._sentence = StringVar()
        self.root.title("Interactive Chart Parser")
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
        self._sentence = ttk.Entry(self.mainframe, width=15)
        self._sentence.grid(column=2, row=5, columnspan=2, sticky=(W, E))
        ttk.Button(
            self.mainframe, text='Parse', width=15,
            command=self.parse_sentence).grid(column=3, row=6, sticky=E)
        ttk.Button(
            self.mainframe, text='Exit', width=10,
            command=exit).grid(column=3, row=8, sticky=E)
        ttk.Label(
            self.mainframe, text='Enter a sentence:').grid(
            column=1, row=5, sticky=E)
        ttk.Label(
            self.mainframe, text='').grid(column=1, row=3, sticky=E)
        ttk.Label(
            self.mainframe, text='').grid(column=1, row=7, sticky=E)
        # add padding around every widget
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        # ensure user doesn't have to click first
        self._sentence.focus()

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
        if obj:
            messagebox.showinfo(obj.name.upper(), str(obj))
        else:
            messagebox.showerror('ERROR', 'No {}.'.format(obj.name))

    def parse_sentence(self):
        if not self.sentence:
            return
        parser = Parser(self.grammar, self.lexicon)
        try:
            parse = parser.parse(self.sentence)
        except KeyError:
            messagebox.showerror('ERROR', 'Unknown words.')
        except IndexError:
            messagebox.showerror('ERROR', 'No grammar.')
        except ValueError:
            messagebox.showerror('ERROR', 'No parse.')
        else:
            messagebox.showinfo(self.sentence.upper(), parse)

    def import_lexicon(self):
        self._import(self.lexicon)

    def import_grammar(self):
        self._import(self.grammar)

    def _import(self, obj):
        file = filedialog.askopenfilename()
        # user has cancelled
        if not file:
            return
        with open(file, 'r') as f:
            try:
                obj.load(f)
            except Exception as e:
                messagebox.showerror(
                    'ERROR', 'Failed to load\n{}.'.format(obj.name, e))

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
            messagebox.showerror(
                'ERROR', 'Failed to add given rule to grammar.')

    def search(self):
        word = self._prompt('word')
        if not word:
            return
        try:
            pos = self.lexicon[word]
        except KeyError:
            messagebox.showerror('ERROR', '{} not found.'.format(word))
        else:
            messagebox.showinfo(
                'POS for {}'.format(word.upper()), ', '.join(sorted(pos)))

    def exit(self):
        for obj in self.lexicon, self.grammar:
            message = "Would you like to save the {}?".format(obj.name)
            if item and messagebox.askyesnocancel(message=message):
                file = filedialog.asksaveasfilename()
                with open(file, 'w') as f:
                    f.write(str(obj))
        mainframe.quit()


def main():
    # constructs graphical interface
    root = Tk()
    GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
