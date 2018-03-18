#!/usr/bin/env python

"""
Kathryn Egan

The GUI uses tkinter to provide a user interface for the parser, grammar,
and lexicon. User can import lexica and grammars or add rules one at a time.
Sentences can be parsed on the fly.
"""
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
from chartparser.parser import Parser
from chartparser.language import Grammar, Lexicon


class GUI:

    def __init__(self, root):
        """ Initialize user interface for the parser. """
        self.root = root
        self.grammar = Grammar()
        self.lexicon = Lexicon()
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
        self.sentence = ttk.Entry(self.mainframe, width=15)
        self.sentence.grid(column=2, row=5, columnspan=2, sticky=(W, E))
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
        self.sentence.focus()

    def show_lexicon(self):
        """ Show lexicon in window. """
        self._show(self.lexicon)

    def show_grammar(self):
        """ Show grammar in window. """
        self._show(self.grammar)

    def _show(self, obj):
        """ Show given object in window or display error
        if the object is empty. """
        if obj:
            messagebox.showinfo(obj.name.upper(), self._truncate(str(obj)))
        else:
            messagebox.showerror('ERROR', 'No {}.'.format(obj.name))

    def _truncate(self, string):
        items = string.split('\n')
        if len(items) <= 20:
            return string
        return '\n'.join(items[:20] + ['...'] + [items[-1]])

    def parse_sentence(self):
        """ Parse sentence that is currently in sentence textbox.
        Displays a single possible parse in message window.
        Displays error message if there are words in the sentence
        that are not in the lexicon, or if there is no grammar imported,
        or if no parse is found.
        """
        if not self.sentence:
            return
        sentence = self.sentence.get()
        parser = Parser(self.grammar, self.lexicon)
        try:
            parse = parser.parse(sentence)
        except KeyError:
            messagebox.showerror('ERROR', 'Unknown words or punctuation.')
        except IndexError:
            messagebox.showerror('ERROR', 'No grammar.')
        except ValueError:
            messagebox.showerror('ERROR', 'No parse.')
        else:
            messagebox.showinfo(sentence, parse)

    def import_lexicon(self):
        """ Import a lexicon. """
        self._import(self.lexicon)

    def import_grammar(self):
        """ Import a grammar. """
        self._import(self.grammar)

    def _import(self, obj):
        """ Import data for the given object. Shows error if the
        object fails to load from a file specified by the user. """
        file = filedialog.askopenfilename()
        # user has cancelled
        if not file:
            return
        with open(file, 'r') as f:
            try:
                obj.load(f)
            except Exception as e:
                messagebox.showerror(
                    'ERROR', 'Failed to load{}\n{}.'.format(obj.name, e))

    def add_lexical_entry(self):
        """ Prompts user to add a word and part of speech to the lexicon. """
        try:
            word = self._prompt('a word')
            pos = self._prompt('a part of speech')
        except ValueError:
            return
        word = word.strip().upper()
        pos = pos.strip().upper()
        self.lexicon.add(word, pos)

    def add_grammar_rule(self):
        """ Prompts user to add a rule to the grammar. """
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

    def _prompt(self, name):
        """ Generic looped prompt to get user to give input.
        Returns:
            answer (str) : input from user
        """
        prompt = "Please enter {}:".format(name)
        while True:
            answer = simpledialog.askstring(title="", prompt=prompt)
            # user has cancelled
            if answer is None:
                raise ValueError
            if answer.strip():
                return answer

    def search(self):
        """ Searches lexicon for word provided by user. Shows part of
        speech of word in message box if word is found otherwise shows
        an error message. """
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
        """ Exits program after prompting user to save
        grammar and/or lexicon. """
        for obj in self.lexicon, self.grammar:
            message = "Would you like to save the {}?".format(obj.name)
            if item and messagebox.askyesnocancel(message=message):
                file = filedialog.asksaveasfilename()
                with open(file, 'w') as f:
                    f.write(str(obj))
        mainframe.quit()


def main():
    """ Main loop for user interface. """
    root = Tk()
    GUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
