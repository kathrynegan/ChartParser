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

    rule = Rule.from_pair('NP', 'N')
    assert rule.parent == 'NP'
    assert rule.children == ('N',)

    rule = Rule.from_pair('VP', 'VP NP')
    assert rule.parent == 'VP'
    assert rule.children == ('VP', 'NP')

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
    arc1 = Arc(Rule('NP', 'N'), 0, 0, 0, [None])
    assert str(arc1) == '<0> NP --> *0 N [None] <0> {}'.format(id(arc1))
    arc2 = Arc(Rule('VP', 'AUX', 'V'), 2, 4, 2, [arc1, None])
    assert str(arc2) == \
        '<2> VP --> AUX V *2 [{}, None] <4> {}'.format(id(arc1), id(arc2))


def test_arc_extend():
    key = Arc(Rule('N', 'cat'), start=0, end=1, dot=1)
    arc = Arc(Rule('NP', 'N'), start=0, end=0, dot=0)
    ext = arc.get_extended(key)
    assert ext.rule == Rule('NP', 'N')
    assert ext.start == 0
    assert ext.end == 1
    assert ext.dot == 1
    assert ext.history == [key]

    # key parent does not match current node in arc children
    arc = Arc(Rule('VP', 'V'), start=0, end=0, dot=0)
    with pytest.raises(ValueError):
        arc.get_extended(key)
    arc = Arc(Rule('NP', 'N'), start=1, end=2, dot=0)
    with pytest.raises(ValueError):
        arc.get_extended(key)
    arc = Arc(Rule('NP', 'DT', 'N'), start=0, end=2, dot=1)
    with pytest.raises(ValueError):
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


def test_lexicon_add():
    lexicon = Lexicon()
    lexicon.add('horse ', ' n ')
    assert lexicon['HORSE'] == {'N'}
    assert lexicon.get_tokens('N') == {'HORSE'}
    lexicon.add(' eats ', 'V')
    assert lexicon['EATS'] == {'V'}
    assert lexicon.get_tokens('V') == {'EATS'}
    lexicon.add('horSE', ' x')
    assert lexicon['HORSE'] == {'N', 'X'}
    assert lexicon.get_tokens('X') == {'HORSE'}
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


def test_lexicon_nonzero():
    lexicon = Lexicon()
    assert not lexicon
    lexicon.add('dog', 'n')
    assert lexicon


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
    assert grammar['N'] == {Rule('NP', 'N')}
    grammar.add('vp', ' v np')
    assert grammar['V'] == {Rule('VP', 'V', 'NP')}
    grammar.add('NP', 'N', 'Y')
    assert grammar['N'] == {Rule('NP', 'N'), Rule('NP', 'N', 'Y')}
    with pytest.raises(ValueError):
        grammar.add('x')


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
    assert grammar['NP'] == {Rule('S', 'NP', 'VP')}
    assert grammar['V'] == {Rule('VP', 'V'), Rule('VP', 'V', 'NP')}


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
        "NP --> DT N",
        "NP --> PN",
        "S --> NP VP",
        "VP --> V",
        "VP --> V NP"]
    answer = '\n'.join(answer)
    result = str(grammar)
    print(result)
    assert result == answer


def test_parser_simple():
    gram = """
        S --> NP VP
        NP --> PN
        VP --> V
        """
    lex = """
        PN : I
        V : sleep
        """
    parser = InteractiveParser()
    parser.grammar.import_grammar(StringIO(gram))
    parser.lexicon.import_lexicon(StringIO(lex))
    chart = parser._chartparse('i sleep')
    arcs = [
        Arc(Rule('S', 'NP', 'VP'), 0, 2, 2),
        Arc(Rule('NP', 'PN'), 0, 1, 1),
        Arc(Rule('VP', 'V'), 1, 2, 1),
        Arc(Rule('PN', 'I'), 0, 1, 1),
        Arc(Rule('V', 'SLEEP'), 1, 2, 1)]
    for arc in arcs:
        assert arc in chart
    for arc in chart:
        assert arc in arcs
    parse = parser._backtrace(chart)
    for arc in arcs:
        assert arc in parse
    for arc in parse:
        assert arc in arcs
    chart = parser._chartparse('i i')
    assert chart is None
    parse = parser._backtrace(chart)
    assert parse is None


# def test_parser_complex():
#     gram = """
#         S --> NP VP
#         NP --> DT N
#         NP --> DT ADJ N
#         NP --> PN
#         VP --> V
#         VP --> VP NP
#         VP --> AUX VP
#         """
#     lex = """
#         PN : I
#         ADJ : little
#         N : can, play, guitar, boy
#         V : play
#         AUX : can
#         DT : a, the
#         ADJ : five-string
#         """
#     parser = InteractiveParser()
#     parser.grammar.import_grammar(StringIO(gram))
#     parser.lexicon.import_lexicon(StringIO(lex))
#     chart = parser._chartparse('the little boy can play the guitar')
#                             #  0   1      2   3   4    5   6      7
#     my_chart = [
#         Arc(Rule('S', 'NP', 'VP'), 0, 7, 2),
#         Arc(Rule('NP', 'DT', 'ADJ', 'N'), 0, 3, 3),
#         Arc(Rule('DT', 'THE'), 0, 1, 1),
#         Arc(Rule('ADJ', 'LITTLE'), 1, 2, 1),
#         Arc(Rule('N', 'BOY'), 2, 3, 1),
#         Arc(Rule('VP', 'AUX', 'VP'), 3, 7, 2),
#         Arc(Rule('AUX', 'CAN'), 3, 4, 1),
#         Arc(Rule('N', 'CAN'), 3, 4, 1),
#         Arc(Rule('VP', 'VP', 'NP'), 4, 7, 2),
#         Arc(Rule('VP', 'V'), 4, 5, 1),
#         Arc(Rule('V', 'PLAY'), 4, 5, 1),
#         Arc(Rule('N', 'PLAY'), 4, 5, 1),
#         Arc(Rule('NP', 'DT', 'N'), 5, 7, 2),
#         Arc(Rule('DT', 'THE'), 5, 6, 1),
#         Arc(Rule('N', 'GUITAR'), 6, 7, 1),
#         Arc(Rule('VP', 'AUX', 'VP'), 3, 5, 2),
#         Arc(Rule('S', 'NP', 'VP'), 0, 5, 2)]
#     for arc in my_chart:
#         assert arc in chart
#     for arc in chart:
#         assert arc in my_chart
#     my_parse = [
#         Arc(Rule('S', 'NP', 'VP'), 0, 7, 2),
#         Arc(Rule('NP', 'DT', 'ADJ', 'N'), 0, 3, 3),
#         Arc(Rule('DT', 'THE'), 0, 1, 1),
#         Arc(Rule('ADJ', 'LITTLE'), 1, 2, 1),
#         Arc(Rule('N', 'BOY'), 2, 3, 1),
#         Arc(Rule('VP', 'AUX', 'VP'), 3, 7, 2),
#         Arc(Rule('AUX', 'CAN'), 3, 4, 1),
#         Arc(Rule('VP', 'VP', 'NP'), 4, 7, 2),
#         Arc(Rule('VP', 'V'), 4, 5, 1),
#         Arc(Rule('V', 'PLAY'), 4, 5, 1),
#         Arc(Rule('NP', 'DT', 'N'), 5, 7, 2),
#         Arc(Rule('DT', 'THE'), 5, 6, 1),
#         Arc(Rule('N', 'GUITAR'), 6, 7, 1)]
#     parse = parser._backtrace(chart)
#     for arc in my_parse:
#         assert arc in parse
#     for arc in parse:
#         assert arc in my_parse
