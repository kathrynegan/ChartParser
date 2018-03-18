"""
Kathryn Egan

Only tests the functionality of the parser and its component
parts. Does not text functionality of GUI.
"""
import pytest
from io import StringIO
from chartparser.parser import Parser
from chartparser.language import Grammar, Lexicon
from chartparser.rule import Terminal, NonTerminal
from chartparser.arc import Arc
from chartparser.chart import Chart
from chartparser.agenda import Agenda


###############
# NONTERMINAL #
###############


def test_nonterminal_const():
    nonterminal = NonTerminal('NP', 'DT', 'N')
    assert nonterminal.parent == 'NP'
    assert nonterminal.children == ('DT', 'N')

    nonterminal = NonTerminal.from_string('NP --> DT N')
    assert nonterminal.parent == 'NP'
    assert nonterminal.children == ('DT', 'N')

    with pytest.raises(ValueError):
        NonTerminal.from_string('--> V')
    with pytest.raises(ValueError):
        NonTerminal.from_string('NP VP --> V')
    with pytest.raises(ValueError):
        NonTerminal.from_string('VP -->')
    with pytest.raises(ValueError):
        NonTerminal('VP')
    with pytest.raises(ValueError):
        NonTerminal('VP', 'AUX V')
    with pytest.raises(ValueError):
        NonTerminal('S VP', 'V')

    assert NonTerminal('S', 'V').is_sentence
    assert not NonTerminal('VP', 'V').is_sentence
    assert not NonTerminal('VP', 'V').is_terminal


def test_nonterminal_eq():
    nonterminal1 = 'NP --> DT N'
    nonterminal2 = 'NP --> N'
    assert NonTerminal.from_string(nonterminal1) == \
        NonTerminal.from_string(nonterminal1)
    assert NonTerminal.from_string(nonterminal1) != \
        NonTerminal.from_string(nonterminal2)
    assert NonTerminal.from_string(nonterminal1) < \
        NonTerminal.from_string(nonterminal2)


def test_nonterminal_str():
    rules = [
        'VP --> V',
        'NP --> DT ADJ N']
    for nonterminal in rules:
        assert str(NonTerminal.from_string(nonterminal)) == nonterminal


def test_rule_len():
    assert len(NonTerminal('VP', 'ADV', 'V')) == 3


############
# TERMINAL #
############


def test_terminal_const():
    terminal = Terminal('NP', 'horse')
    assert terminal.parent == 'NP'
    assert terminal.pos == 'NP'
    assert terminal.children == ('HORSE',)
    assert terminal.token == 'HORSE'

    terminal = Terminal.from_string('  The : Dt  ')
    assert terminal.token == 'THE'
    assert terminal.pos == 'DT'
    assert terminal.is_terminal

    with pytest.raises(ValueError):
        Terminal.from_string(': V')
    with pytest.raises(ValueError):
        Terminal.from_string('my cat : best')
    with pytest.raises(ValueError):
        Terminal.from_string(': doge')
    with pytest.raises(ValueError):
        Terminal('hello')
    with pytest.raises(ValueError):
        Terminal('V', 'raise up')
    with pytest.raises(ValueError):
        Terminal('S VP', 'yikes')


def test_terminal_eq():
    rule1 = 'NP --> DT N'
    rule2 = 'NP --> N'
    assert NonTerminal.from_string(rule1) == NonTerminal.from_string(rule1)
    assert NonTerminal.from_string(rule1) != NonTerminal.from_string(rule2)
    assert NonTerminal.from_string(rule1) < NonTerminal.from_string(rule2)


def test_terminal_str():
    rules = [
        'VP --> V',
        'NP --> DT ADJ N']
    for rule in rules:
        assert str(NonTerminal.from_string(rule)) == rule


def test_terminal_len():
    assert len(NonTerminal('VP', 'ADV', 'V')) == 3


#######
# ARC #
#######


def test_arc_string():
    arc1 = Arc(NonTerminal('NP', 'N'), 0, 0, 0, [None])
    assert str(arc1) == '<0> NP --> *0 N [None] <0> {}'.format(id(arc1))
    arc2 = Arc(NonTerminal('VP', 'AUX', 'V'), 2, 4, 2, [arc1, None])
    assert str(arc2) == \
        '<2> VP --> AUX V *2 [{}, None] <4> {}'.format(id(arc1), id(arc2))


def test_arc_extend():
    key = Arc(NonTerminal('N', 'cat'), start=0, end=1, dot=1)
    arc = Arc(NonTerminal('NP', 'N'), start=0, end=0, dot=0)
    ext = arc.get_extended(key)
    assert ext.rule == NonTerminal('NP', 'N')
    assert ext.start == 0
    assert ext.end == 1
    assert ext.dot == 1
    assert ext.history == [key]

    # key parent does not match current node in arc children
    arc = Arc(NonTerminal('VP', 'V'), start=0, end=0, dot=0)
    with pytest.raises(ValueError):
        arc.get_extended(key)
    arc = Arc(NonTerminal('NP', 'N'), start=1, end=2, dot=0)
    with pytest.raises(ValueError):
        arc.get_extended(key)
    arc = Arc(NonTerminal('NP', 'DT', 'N'), start=0, end=2, dot=1)
    with pytest.raises(ValueError):
        arc.get_extended(key)


def test_arc_is_complete():
    arc1 = Arc(NonTerminal('DT', 'the'), 2, 3, 1, [10])
    arc2 = Arc(NonTerminal('NP', 'DT', 'N'), 2, 3, 1, [12])
    arc3 = Arc(NonTerminal('NP', 'DT', 'N'), 2, 3, 2, [14])
    assert arc1.is_complete()
    assert not arc2.is_complete()
    assert arc3.is_complete()


def test_arc_eq():
    rule = NonTerminal('NP', 'N')
    start = 1
    end = 2
    dot = 1
    assert (
        Arc(rule, start, end, dot) ==
        Arc(rule, start, end, dot))
    assert(
        Arc(rule, start, end, dot) !=
        Arc(rule, start + 1, end, dot))


#########
# CHART #
#########


def test_chart():
    chart = Chart(['I', 'SLEEP'])
    chart.add(Arc(NonTerminal('PN', 'I'), 0, 1, 1))
    assert not chart.is_sentence
    chart.add(Arc(NonTerminal('V', 'SLEEP'), 1, 2, 1))
    chart.add(Arc(NonTerminal('NP', 'PN'), 0, 1, 1, [1]))
    chart.add(Arc(NonTerminal('VP', 'V'), 1, 2, 1, [2]))
    chart.add(Arc(NonTerminal('S', 'VP'), 1, 2, 1, [2]))
    assert not chart.is_sentence
    chart.add(Arc(NonTerminal('S', 'NP', 'VP'), 0, 2, 2, [3, 4]))
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


###########
# LEXICON #
###########

test_lex = """
    I : PN
    can : N
    play : N
    guitar : N
    play : V
    can : AUX
    a : DT
    the : DT
    five-string : ADJ
    """


def test_lexicon_add():
    lexicon = Lexicon()
    lexicon.add(Terminal.from_string('HORSE : N'))
    assert lexicon['HORSE'] == {Terminal('N', 'HORSE'), }
    lexicon.add(Terminal.from_string(' eats : V'))
    assert lexicon['EATS'] == {Terminal('V', 'EATS'), }
    lexicon.add(Terminal.from_string('horSE :  x'))
    assert lexicon['HORSE'] == {Terminal('N', 'HORSE'), Terminal('X', 'HORSE')}
    lexicon.add(Terminal.from_string('cow : n'))
    assert lexicon['COW'] == {Terminal('N', 'COW'), }


def test_lexicon_import():
    lexicon = Lexicon()
    lexicon.load(StringIO(test_lex))
    assert lexicon['CAN'] == {Terminal('AUX', 'CAN'), Terminal('N', 'CAN')}
    assert lexicon['FIVE-STRING'] == {Terminal('ADJ', 'FIVE-STRING')}


def test_lexicon_len():
    lexicon = Lexicon()
    assert not lexicon
    lexicon.add(Terminal('n', 'dog'))
    assert lexicon
    assert len(lexicon) == 1
    lexicon.add(Terminal('v', 'dog'))
    lexicon.add(Terminal('n', 'horse'))
    assert len(lexicon) == 2


def test_print_lexicon():
    lexicon = Lexicon()
    lexicon.load(StringIO(test_lex))
    answer = [
        "A : DT",
        "CAN : AUX",
        "CAN : N",
        "FIVE-STRING : ADJ",
        "GUITAR : N",
        "I : PN",
        "PLAY : N",
        "PLAY : V",
        "THE : DT"]
    answer = '\n'.join(answer)
    print(str(lexicon))
    assert str(lexicon) == answer


###########
# GRAMMAR #
###########


def test_grammar_add():
    grammar = Grammar()
    grammar.add(NonTerminal.from_string('np --> n'))
    assert grammar['N'] == {NonTerminal('NP', 'N')}
    grammar.add(NonTerminal('vp', 'v', 'np'))
    assert grammar['V'] == {NonTerminal('VP', 'V', 'NP')}
    grammar.add(NonTerminal('NP', 'N', 'Y'))
    assert grammar['N'] == {
        NonTerminal('NP', 'N'), NonTerminal('NP', 'N', 'Y')}


test_gram = """
    S --> NP VP
    NP --> DT N
    NP --> PN
    VP --> V
    vp --> v nP
    """


def test_grammar_len():
    grammar = Grammar()
    assert not grammar
    grammar.load(StringIO(test_gram))
    assert grammar
    assert len(grammar) == 5


def test_grammar_import():
    grammar = Grammar()
    grammar.load(StringIO(test_gram))
    assert grammar['NP'] == {NonTerminal('S', 'NP', 'VP'), }
    assert grammar['V'] == {
        NonTerminal('VP', 'V'), NonTerminal('VP', 'V', 'NP')}
    with pytest.raises(ValueError):
        grammar.load(StringIO('S NP VP'))


def test_grammar_str():
    grammar = Grammar()
    grammar.load(StringIO(test_gram))
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


simple_grammar = Grammar()
simple_grammar.load(StringIO("""
    S --> NP VP
    NP --> PN
    VP --> V
    """))
simple_lexicon = Lexicon()
simple_lexicon.load(StringIO("""
    I : PN
    sleep : V
    """))
simple_parser = Parser(simple_grammar, simple_lexicon)
simple_sentence = ' i   sleep '
simple_tokens = ['I', 'SLEEP']
simple_parse = '[.S [.NP [.PN I]][.VP [.V SLEEP]]]'
simple_chart = [
    Arc(NonTerminal('S', 'NP', 'VP'), 0, 2, 2),
    Arc(NonTerminal('NP', 'PN'), 0, 1, 1),
    Arc(NonTerminal('VP', 'V'), 1, 2, 1),
    Arc(Terminal('PN', 'I'), 0, 1, 1),
    Arc(Terminal('V', 'SLEEP'), 1, 2, 1)]

complex_grammar = Grammar()
complex_grammar.load(StringIO("""
    S --> NP VP
    NP --> DT N
    NP --> DT ADJ N
    NP --> PN
    VP --> V
    VP --> VP NP
    VP --> AUX VP
    """))
complex_lexicon = Lexicon()
complex_lexicon.load(StringIO("""
    I : PN
    little : ADJ
    can : N
    play : N
    guitar : N
    boy : N
    can : AUX
    play : V
    a : DT
    the : DT
    five-string : ADJ
    """))
complex_parser = Parser(complex_grammar, complex_lexicon)
complex_sentence = ' the little boy CAN PLay the    GUiTAR '
complex_tokens = ['THE', 'LITTLE', 'BOY', 'CAN', 'PLAY', 'THE', 'GUITAR']
complex_parse = '[.S [.NP [.DT THE][.ADJ LITTLE][.N BOY]][.VP [.AUX CAN][.VP [.VP [.V PLAY]][.NP [.DT THE][.N GUITAR]]]]]'
complex_chart = [
    Arc(NonTerminal('S', 'NP', 'VP'), 0, 7, 2),
    Arc(NonTerminal('NP', 'DT', 'ADJ', 'N'), 0, 3, 3),
    Arc(Terminal('DT', 'THE'), 0, 1, 1),
    Arc(Terminal('ADJ', 'LITTLE'), 1, 2, 1),
    Arc(Terminal('N', 'BOY'), 2, 3, 1),
    Arc(NonTerminal('VP', 'AUX', 'VP'), 3, 7, 2),
    Arc(Terminal('AUX', 'CAN'), 3, 4, 1),
    Arc(Terminal('N', 'CAN'), 3, 4, 1),
    Arc(NonTerminal('VP', 'VP', 'NP'), 4, 7, 2),
    Arc(NonTerminal('VP', 'V'), 4, 5, 1),
    Arc(Terminal('V', 'PLAY'), 4, 5, 1),
    Arc(Terminal('N', 'PLAY'), 4, 5, 1),
    Arc(NonTerminal('NP', 'DT', 'N'), 5, 7, 2),
    Arc(Terminal('DT', 'THE'), 5, 6, 1),
    Arc(Terminal('N', 'GUITAR'), 6, 7, 1),
    Arc(NonTerminal('VP', 'AUX', 'VP'), 3, 5, 2),
    Arc(NonTerminal('S', 'NP', 'VP'), 0, 5, 2)]


def test_tokenize():
    assert Parser.tokenize(simple_sentence) == simple_tokens
    assert Parser.tokenize(complex_sentence) == complex_tokens
    assert Parser.tokenize('   ') == []


##########
# AGENDA #
##########


def test_agenda_constr():
    agenda = Agenda(simple_tokens, simple_lexicon)
    my_agenda = [
        Arc(Terminal('PN', 'I'), 0, 1, 1),
        Arc(Terminal('V', 'SLEEP'), 1, 2, 1)]
    for arc in my_agenda:
        assert arc in agenda
    for arc in agenda:
        assert arc in my_agenda


def test_choose_next():
    agenda = Agenda(simple_tokens, simple_lexicon)
    assert agenda.choose_next() == Arc(Terminal('PN', 'I'), 0, 1, 1)
    assert agenda.choose_next() == Arc(Terminal('V', 'SLEEP'), 1, 2, 1)
    agenda.agenda.append(Arc(NonTerminal('NP', 'N'), 0, 1, 0))
    # no completed arcs to select
    with pytest.raises(ValueError):
        assert agenda.choose_next()


def test_predict():
    agenda = Agenda(simple_tokens, simple_lexicon)
    current = agenda.choose_next()
    assert current == Arc(Terminal('PN', 'I'), 0, 1, 1)
    agenda.predict(simple_grammar, current)
    my_agenda = [
        Arc(Terminal('V', 'SLEEP'), 1, 2, 1),
        Arc(NonTerminal('NP', 'PN'), 0, 0, 0)]
    for arc in my_agenda:
        assert arc in agenda
    for arc in agenda:
        assert arc in my_agenda


def test_extend():
    agenda = Agenda(simple_tokens, simple_lexicon)
    current = agenda.choose_next()
    assert current == Arc(Terminal('PN', 'I'), 0, 1, 1)
    agenda.predict(simple_grammar, current)
    agenda.extend(current)
    my_agenda = [
        Arc(Terminal('V', 'SLEEP'), 1, 2, 1),
        Arc(NonTerminal('NP', 'PN'), 0, 0, 0),
        Arc(NonTerminal('NP', 'PN'), 0, 1, 1)]
    for arc in agenda:
        assert arc in my_agenda
    for arc in my_agenda:
        assert arc in agenda


#########
# PARSE #
#########


def test_simple_chartparse():
    chart = simple_parser._chartparse(*Parser.tokenize(simple_sentence))
    for arc in simple_chart:
        assert arc in chart
    for arc in chart:
        assert arc in simple_chart


def test_simple_parse():
    assert simple_parser.parse(simple_sentence) == simple_parse
    with pytest.raises(ValueError):
        simple_parser.parse('i i')


def test_complex_chartparse():
    chart = complex_parser._chartparse(*Parser.tokenize(complex_sentence))
    for arc in complex_chart:
        assert arc in chart
    for arc in chart:
        assert arc in complex_chart


def test_complex_parse():
    assert complex_parser.parse(complex_sentence) == complex_parse
