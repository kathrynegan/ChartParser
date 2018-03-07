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
from chart import Chart
from agenda import Agenda


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
        message = str(obj) if obj else "ERROR: Nothing to show."
        messagebox.showinfo(message=message)

    def parse(self):
        if not self.sentence:
            return
        try:
            chart = self._chartparse(self.sentence)
        except KeyError:
            messagebox.showinfo(message="ERROR: Unknown words.")
        except IndexError:
            messagebox.showinfo(message="ERROR: No grammar.")
        except ValueError:
            messagebox.showinfo(message="ERROR: Sentence failed to parse.")
        else:
            parse = self._backtrace(chart)
            parse = self._to_string(parse)
            messagebox.showinfo(message=parse)

    def _to_string(self, parse):
        # leaf node found
        if node[4] == -1:
            word = get_node(node, word_list)
            if word[0] == 'i':
                word[0] = 'I'
            return('[.' + node[0] + ' ' + word[0] + ' ] ')
        # explore children
        else:
            parse = '[.' + node[0] + ' '
            children = find_children(chart, node)
            for child in children:
                parse += find_parse(chart, child, word_list)
            parse += '] '
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
                    message="ERROR: File did not load\n{}".format(name, e))
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
            messagebox.showinfo(message="Not found.")
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
