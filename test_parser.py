"""
Kathryn Egan
"""
import pytest
from io import StringIO
from interactive_parser import InteractiveParser
from interactive_parser import Lexicon
from interactive_parser import Grammar
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog


def test_lexicon_add():
    lexicon = Lexicon()
    lexicon.add('horse ', ' n ')
    assert lexicon['HORSE'] == {'N'}
    assert lexicon.get_tokens('N') == {'HORSE'}
    lexicon.add(' eats ', 'V')
    assert lexicon['EATS'] == {'V'}
    assert lexicon.get_tokens('V') == {'EATS'}
    lexicon.add('horSE', ' pn')
    assert lexicon['HORSE'] == {'N', 'PN'}
    assert lexicon.get_tokens('PN') == {'HORSE'}
    lexicon.add('cow', 'n')
    assert lexicon['COW'] == {'N'}
    assert lexicon.get_tokens('N') == {'HORSE', 'COW'}


def test_lexicon_import():
    lex = """
        PN : I
        N : can, play, guitar
        V : play
        AUX : can
        DT : a, the
        ADJ : five-string
        """
    f = StringIO(lex)
    lexicon = Lexicon()
    lexicon.import_lexicon(f)
    assert lexicon['CAN'] == {'AUX', 'N'}
    assert lexicon['FIVE-STRING'] == {'ADJ'}
    assert lexicon.get_tokens('N') == {'CAN', 'PLAY', 'GUITAR'}


def test_print_lexicon():
    lex = """
        PN : I
        N : can, play, guitar
        V : play
        AUX : can
        DT : a, the
        ADJ : five-string
        """
    f = StringIO(lex)
    lexicon = Lexicon()
    lexicon.import_lexicon(f)
    answer = [
        "ADJ : FIVE-STRING",
        "AUX : CAN",
        "DT : A, THE",
        "N : CAN, GUITAR, PLAY",
        "PN : I",
        "V : PLAY"]
    answer = '\n'.join(answer)
    assert str(lexicon) == answer


def test_grammar_add():
    grammar = Grammar()
    grammar.add('np --> n')
    assert grammar['N'] == {('NP', 'N')}
    grammar.add('vp --> v np')
    assert grammar['V'] == {('VP', 'V', 'NP')}
    x = grammar.add('x')
    assert x is False
    assert 'X' not in grammar


def test_grammar_import():
    grammar = Grammar()
    gram = """
        S --> NP VP
        NP --> DT N
        NP --> PN
        VP --> V
        vp --> v nP
        x
        y
        z --> 

        """
    f = StringIO(gram)
    grammar.import_grammar(f)
    assert grammar['NP'] == {('S', 'NP', 'VP')}
    assert grammar['V'] == {('VP', 'V'), ('VP', 'V', 'NP')}


def test_grammar_str():
    grammar = Grammar()
    gram = """
        S --> NP VP
        NP --> DT N
        NP --> PN
        VP --> V
        vp --> v nP
        x
        y
        z --> 

        """
    f = StringIO(gram)
    grammar.import_grammar(f)
    answer = [
        "S --> NP VP",
        "NP --> DT N",
        "NP --> PN",
        "VP --> V",
        "VP --> V NP"]
    answer = '\n'.join(answer)
    assert str(grammar) == answer

def test_parser():
    # root = Tk()
    parser = InteractiveParser()
    parser.sentence = 'i have no time for this'
    
