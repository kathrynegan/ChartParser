"""
Kathryn Egan
"""
import pytest
from io import StringIO
from interactive_parser import InteractiveParser
from interactive_parser import Lexicon
from interactive_parser import Grammar
from interactive_parser import Arc
from interactive_parser import Rule
from interactive_parser import Chart
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog


def test_rule_const():
    rule = Rule('NP', 'DT', 'N')
    assert rule.parent == 'NP'
    assert rule.children == ('DT', 'N')
    rule = Rule.from_string('NP --> DT N')
    assert rule.parent == 'NP'
    assert rule.children == ('DT', 'N')
    with pytest.raises(ValueError):
        Rule.from_string('--> V')
    with pytest.raises(ValueError):
        Rule.from_string('NP VP --> V')
    with pytest.raises(ValueError):
        Rule.from_string('VP -->')
    with pytest.raises(ValueError):
        Rule('VP')


def test_rule_eq():
    rule1 = 'NP --> DT N'
    rule2 = 'NP --> N'
    assert Rule.from_string(rule1) == Rule.from_string(rule1)
    assert Rule.from_string(rule1) != Rule.from_string(rule2)
    assert Rule.from_string(rule1) < Rule.from_string(rule2)


def test_rule_str():
    rules = [
        'VP --> V',
        'NP --> DT ADJ N']
    for rule in rules:
        assert str(Rule.from_string(rule)) == rule


def test_rule_len():
    assert len(Rule('VP', 'ADV', 'V')) == 3


def test_arc_string():
    assert str(Arc(Rule('NP', 'N'), 0, 0, 0, [-1])) == \
        '<0> NP --> * N [-1] <0>'
    assert str(Arc(Rule('VP', 'AUX', 'V'), 2, 4, 2, [2, 3])) ==\
        '<2> VP --> AUX V * [2, 3] <4>'


def test_arc_extend():
    key = Arc(Rule('N', 'cat'), start=0, end=1, dot=1)
    arc = Arc(Rule('NP', 'N'), start=0, end=0, dot=0)
    assert arc.history == [-1]
    ext = arc.get_extended(key)
    assert ext.rule == Rule('NP', 'N')
    assert ext.start == 0
    assert ext.end == 1
    assert ext.dot == 1
    assert ext.history == [id(key)]

    # key parent does not match current node in arc children
    with pytest.raises(ValueError):
        arc = Arc(Rule('VP', 'V'), start=0, end=0, dot=0)
        arc.get_extended(key)
    with pytest.raises(ValueError):
        arc = Arc(Rule('NP', 'N'), start=1, end=2, dot=0)
        arc.get_extended(key)
    with pytest.raises(ValueError):
        arc = Arc(Rule('NP', 'DT', 'N'), start=0, end=2, dot=1)
        arc.get_extended(key)


def test_arc_is_complete():
    arc1 = Arc(Rule('DT', 'the'), 2, 3, 1, 10)
    arc2 = Arc(Rule('NP', 'DT', 'N'), 2, 3, 1, 12)
    arc3 = Arc(Rule('NP', 'DT', 'N'), 2, 3, 2, 14)
    assert arc1.is_complete()
    assert not arc2.is_complete()
    assert arc3.is_complete()


def test_arc_eq():
    rule = Rule('NP', 'N')
    start = 1
    end = 2
    dot = 1
    assert (
        Arc(rule, start, end, dot) ==
        Arc(rule, start, end, dot))
    assert(
        Arc(rule, start, end, dot) !=
        Arc(rule, start + 1, end, dot))


def test_chart():
    chart = Chart(['I', 'SLEEP'])
    chart.add(Arc(Rule('PN', 'I'), 0, 1, 1))
    assert not chart.is_sentence
    chart.add(Arc(Rule('V', 'SLEEP'), 1, 2, 1))
    chart.add(Arc(Rule('NP', 'PN'), 0, 1, 1, [1]))
    chart.add(Arc(Rule('VP', 'V'), 1, 2, 1, [2]))
    chart.add(Arc(Rule('S', 'VP'), 1, 2, 1, [2]))
    assert not chart.is_sentence
    chart.add(Arc(Rule('S', 'NP', 'VP'), 0, 2, 2, [3, 4]))
    assert chart.is_sentence
    answer = [
        '0    1    2',
        ' ----       PN --> I',
        '      ----  V --> SLEEP',
        ' ----       NP --> PN',
        '      ----  VP --> V',
        '      ----  S --> VP',
        ' ---------  S --> NP VP']
    assert str(chart) == '\n'.join(answer)


# def test_lexicon_add():
#     lexicon = Lexicon()
#     lexicon.add('horse ', ' n ')
#     assert lexicon['HORSE'] == {'N'}
#     assert lexicon.get_tokens('N') == {'HORSE'}
#     lexicon.add(' eats ', 'V')
#     assert lexicon['EATS'] == {'V'}
#     assert lexicon.get_tokens('V') == {'EATS'}
#     lexicon.add('horSE', ' x')
#     assert lexicon['HORSE'] == {'N', 'X'}
#     assert lexicon.get_tokens('X') == {'HORSE'}
#     lexicon.add('cow', 'n')
#     assert lexicon['COW'] == {'N'}
#     assert lexicon.get_tokens('N') == {'HORSE', 'COW'}


# def test_lexicon_import():
#     lex = """
#         PN : I
#         N : can, play, guitar
#         V : play
#         AUX : can
#         DT : a, the
#         ADJ : five-string
#         """
#     f = StringIO(lex)
#     lexicon = Lexicon()
#     lexicon.import_lexicon(f)
#     assert lexicon['CAN'] == {'AUX', 'N'}
#     assert lexicon['FIVE-STRING'] == {'ADJ'}
#     assert lexicon.get_tokens('N') == {'CAN', 'PLAY', 'GUITAR'}


# def test_print_lexicon():
#     lex = """
#         PN : I
#         N : can, play, guitar
#         V : play
#         AUX : can
#         DT : a, the
#         ADJ : five-string
#         """
#     f = StringIO(lex)
#     lexicon = Lexicon()
#     lexicon.import_lexicon(f)
#     answer = [
#         "ADJ : FIVE-STRING",
#         "AUX : CAN",
#         "DT : A, THE",
#         "N : CAN, GUITAR, PLAY",
#         "PN : I",
#         "V : PLAY"]
#     answer = '\n'.join(answer)
#     assert str(lexicon) == answer


# def test_grammar_add():
#     grammar = Grammar()
#     grammar.add('np --> n')
#     assert grammar['N'] == {('NP', 'N')}
#     grammar.add('vp --> v np')
#     assert grammar['V'] == {('VP', 'V', 'NP')}
#     x = grammar.add('x')
#     assert x is False
#     assert 'X' not in grammar


# def test_grammar_import():
#     grammar = Grammar()
#     gram = """
#         S --> NP VP
#         NP --> DT N
#         NP --> PN
#         VP --> V
#         vp --> v nP
#         x
#         y
#         z --> 

#         """
#     f = StringIO(gram)
#     grammar.import_grammar(f)
#     assert grammar['NP'] == {('S', 'NP', 'VP')}
#     assert grammar['V'] == {('VP', 'V'), ('VP', 'V', 'NP')}


# def test_grammar_str():
#     grammar = Grammar()
#     gram = """
#         S --> NP VP
#         NP --> DT N
#         NP --> PN
#         VP --> V
#         vp --> v nP
#         x
#         y
#         z --> 

#         """
#     f = StringIO(gram)
#     grammar.import_grammar(f)
#     answer = [
#         "NP --> DT N",
#         "S --> NP VP",
#         "NP --> PN",
#         "VP --> V",
#         "VP --> V NP"]
#     answer = '\n'.join(answer)
#     result = str(grammar)
#     assert result == answer



def test_parser():
    gram = """
        S --> NP VP
        NP --> DT N
        NP --> DT ADJ N
        NP --> PN
        VP --> V
        VP --> VP NP
        VP --> AUX VP
        """
    lex = """
        PN : I
        ADJ : little
        N : can, play, guitar, boy
        V : play
        AUX : can
        DT : a, the
        ADJ : five-string
        """
    # gram = """
    #     S --> NP VP
    #     NP --> PN
    #     VP --> V
    #     """
    # lex = """
    #     PN : I
    #     V : sleep
    #     """
    # root = Tk()
    parser = InteractiveParser()
    parser.grammar.import_grammar(StringIO(gram))
    parser.lexicon.import_lexicon(StringIO(lex))
    # parser.sentence = 'the little boy can play the guitar'
    # assert parser.sentence == 'the little boy can play the guitar'
    chart = parser._chartparse('the little boy can play the guitar')
    print(chart)
    # chart = parser._chartparse('i i')
    # print(chart)
    assert False
#     # assert edges ==  [('I', 0, 1), ('CAN', 1, 2), ('PLAY', 2, 3), ('THE', 3, 4), ('GUITAR', 4, 5)]
