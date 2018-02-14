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
# from tkinter import Tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog
import re
import copy


lexicon = {}        # maps words to part(s) of speech
grammar = {}        # stores rules, organized by first terminal in rule
pos_set = set()       # stores parts of speech


# Returns the input as a lower case,
# tokenized list of words
def process_input():
    punc = re.compile(r'[\.,?\:;"\(\)!&$#]')  # remove punctuation
    words = sentence.get()
    words = punc.sub(r' ', words)
    words = words.lower().split()
    for word in words:
        word = word.strip()
        if not word:
            words.remove(word)
    return words


# Provides a detailed account of the chart parsing
# process. Shows the final parse in a dialog
# window if there is one.
def verbose_parse(*args):
    words = process_input()
    input_list = make_input_list(words)  # get edges of sentence
    message = "This is the input:\n\n{}".format(printed_input_list(input_list))
    message += "\nEach word will be processed in order."
    ok = messagebox.askokcancel(message=message)
    if not ok:
        return
    key_list = []
    arc_list = []
    chart = []
    name = 0
    tell_extend = True
    tell_arc = True
    for word in input_list:
        pos = lexicon[word[0]]     # get parts of speech of words
        printed = pos_to_str(pos)
        message = \
            "The word \"{}\" has the following part(s) of speech:\n\n{}\n" +\
            "Each part of speech is marked with the edges of the input " +\
            "word, making it into a 'key'. The keys are added to the key list."
        ok = messagebox.askokcancel(message=message.format(word[0], printed))
        if not ok:
            return
        # add keys for words to key list
        for pos in pos_set:
            key = [pos, word[1], word[2], name, -1]   # create key
            name += 1
            key_list.append(key)
        # assess each key on key list
        while len(key_list) != 0:
            message = "This is the current key list:\n\n{}"
            ok = messagebox.askokcancel(
                message=message.format(key_list_to_str(key_list)))
            if not ok:
                return
            key = key_list[0]
            key_list.remove(key)
            printed = key_to_str(key)
            message = "The first key on the list is removed:\n\n\t"
            ok = messagebox.askokcancel(
                message=message.format(key_to_str(key)))
            if not ok:
                return
            message = \
                "Next every rule whose right-hand side starts with {} is found. " +\
                "The index of the key's left edge becomes the index of both the " +\
                "left and right edges of the rule. A dot is placed in front. " +\
                "This new rule is called an 'arc'."
            ok = messagebox.askokcancel(message=message.format(key[0]))
            if not ok:
                return
            if key[0] in grammar:
                arcs = grammar[key[0]]  # get list of rules starting with key
                printed = ''
                # create an arc for each rule and add to arc list
                for rule in arcs:
                    tracer = (len(rule) - 1) * [-1]
                    arc = [rule, [key[1], key[1]], 0, tracer]
                    arc_list.append(arc)
                    printed += arc_to_str(arc) + '\n'
                message = \
                    "These arcs start with {} on the right side:\n\n{}\n" +\
                    "They get added to the arc list.\n\nThe dot indicates " +\
                    "progress through the arc. When the dot is at the end of " +\
                    "the arc, we've successfully found a constituent."
                messagebox.askokcancel(message=message.format(key[0], printed))
                if not ok:
                    return
            else:
                message = \
                    "This key does not start the right-hand side of any " +\
                    "rule, so nothing has been added to the arc list."
                ok = messagebox.askokcancel(message=message)
                if not ok:
                    return
            messagebox.showinfo(message="Next the arcs must be extended.")
            if tell_extend:
                response = messagebox.askyesno(
                    message="Would you like information on what 'extend' means?")
                if response:
                    message = \
                        "The arcs whose dot is to the left of a part of " +\
                        "speech matching the current key's and whose right " +\
                        "edge matches the key's left edge are extended by " +\
                        "moving the dot one to the right and making the " +\
                        "arc's right edge the equal to the key's right edge."
                    messagebox.showinfo(message=message)
                tell_extend = False
            # extend each arc and add back to arc list
            temp = []
            can_extend = False
            for arc in arc_list:
                arc2 = copy.deepcopy(arc)
                arc2 = extend_arc(arc2, key)
                # arc successfully extended
                if arc2 != []:
                    can_extend = True
                    temp.append(arc2)
                    printed1 = arc_to_str(arc)
                    printed2 = arc_to_str(arc2)
                    message = "The arc\n\n{}\n\nis now\n\n{}\n\nIt gets added to the arc list."
                    ok = messagebox.askokcancel(message=message.format(printed1, printed2))
                    if not ok:
                        return
                    # arc is successfully made into a constituent,
                    # update key list to contain constituent, remove arc
                    if arc2[2] == len(arc2[3]):
                        constituent = [
                            arc2[0][0], arc2[1][0], arc2[1][1], name, arc2[3]]
                        name += 1
                        key_list.append(constituent)
                        temp.remove(arc2)
                        printed_arc = arc_to_str(arc2)
                        message = "{}\n\nThis  arc is complete. It can now be converted to a key."
                        ok = messagebox.askokcancel(
                            message=message.format(printed_arc))
                        if not ok:
                            return
                        if tell_arc:
                            response = messagebox.askyesno(
                                message="Would you like information on how "+
                                "to turn an arc into a key?")
                            if response:
                                messagebox.showinfo(
                                    message="Remove the arrow and the right-hand " +
                                    "side of the rule. The resulting nonterminal " +
                                    "and the edges make up the new key.")
                                tell_arc = False
                        printed = key_to_str(constituent)
                        message = \
                            "The arc\n\n{}\n\nturns into\n\n{}\n\n" +\
                            "The key {} gets added to the key list and " +\
                            "is used to extend other arcs."
                        ok = messagebox.askokcancel(
                            message=message.format(printed_arc, printed, printed))
                        if not ok:
                            return
            if not can_extend:
                messagebox.showinfo(message="No arcs could be extended with this key.")
            # add extended arcs back to arc list
            arc_list += temp
            if arc_list != []:
                printed = arc_list_to_str(arc_list)
                ok = messagebox.askokcancel(message="The arc list is now:\n\n" + printed)
                if not ok:
                    return
            else:
                ok = messagebox.askokcancel(message="The arc list is empty.")
                if not ok:
                    return
            # add key to chart
            chart.append(key)
            printed1 = key_to_str(key)
            printed2 = chart_to_str(chart, len(input_list) + 1)
            message = "Lastly, the current key {} is added to the chart:\n\n{}"
            messagebox.showinfo(message=message.format(printed1, printed2))
    parsed = False
    initial_symbol = []
    message = \
        "Every possible key has been processed and the key list is " +\
        "now empty. If there is an S key in the chart that spans the " +\
        "length of the sentence, the phrase has been parsed successfully."
    ok = messagebox.askokcancel(message=message)
    if not ok:
        return
    ok = messagebox.askokcancel(message="Looking for an S key...")
    if not ok:
        return
    # check for initial symbol
    for key in chart:
        if key[:-2] == ['S', 0, len(words)]:
            parsed = True
            initial_symbol = key
    if not parsed:
        messagebox.showinfo(
            message="Unfortunately there was no parse for this sentence.")
        return([])
    else:
        ok = messagebox.askokcancel(
            message="S key found. Next we backtrace to find the right parse...")
        if not ok:
            return
        message = "This is the parse for \"{}\":\n\n{}"
        messagebox.showinfo( message=message.format(
            sentence.get(), find_parse(chart, initial_symbol, input_list)))


# Shows a successful parse in a dialog window
# if one is found, a n alternate message if not.
def regular_parse(*args):
    words = process_input()
    input_list = make_input_list(words)  # get edges of sentence
    key_list = []
    arc_list = []
    chart = []
    name = 0
    for word in input_list:
        pos = lexicon[word[0]]  # get parts of speech of words
        # add keys for words to key list
        for pos in pos:
            key = [pos, word[1], word[2], name, -1]  # create key
            name += 1
            key_list.append(key)
        # assess each key on key list
        while len(key_list) != 0:
            key = key_list[0]
            key_list.remove(key)
            if key[0] in grammar:
                arcs = grammar[key[0]]  # get list of rules starting with key
                # create an arc for each rule and add to arc list
                for rule in arcs:
                    tracer = (len(rule) - 1) * [-1]
                    arc = [rule, [key[1], key[1]], 0, tracer]
                    arc_list.append(arc)
            # extend each arc and add back to arc list
            temp = []
            for arc in arc_list:
                arc2 = copy.deepcopy(arc)
                arc2 = extend_arc(arc2, key)
                # arc successfully extended
                if arc2 != []:
                    temp.append(arc2)
                    # arc is successfully made into a constituent,
                    # update key list to contain constituent, remove arc
                    if arc2[2] == len(arc2[3]):
                        constituent = [
                            arc2[0][0], arc2[1][0], arc2[1][1], name, arc2[3]]
                        name += 1
                        key_list.append(constituent)
                        temp.remove(arc2)
            # add extended arcs back to arc list
            arc_list += temp
            # add key to chart
            chart.append(key)
    parsed = False
    initial_symbol = []
    # check for initial symbol
    for key in chart:
        if key[:-2] == ['S', 0, len(words)]:
            parsed = True
            initial_symbol = key
    if not parsed:
        messagebox.showinfo(message="That sentence did not parse.")
    else:
        string = find_parse(chart, initial_symbol, input_list)
        messagebox.showinfo(message=string)


# Backtrace the chart to get correct parse
def find_parse(chart, node, word_list):
    # leaf node found
    if node[4] == -1:
        word = get_node(node, word_list)
        if word[0] == 'i':
            word[0] = 'I'
        return '[.{} {} ] '.format(node[0], word[0])
    # explore children
    else:
        parse = '[.{} '.format(node[0])
        children = find_children(chart, node)
        for child in children:
            parse += find_parse(chart, child, word_list)
        parse += '] '
        return(parse)


# Returns the word corresponding to that node
def get_node(node, word_list):
    for word in word_list:
        if word[1] == node[1]:
            return(word)


# Returns a list of the children of the given node
def find_children(chart, node):
    children = []
    for item in chart:
        if item[3] in node[4]:
            children.append(item)
        if len(children) == len(node[4]):
            break
    return(children)


# Returns an extended arc if the arc can be
# extended, otherwise an empty list
def extend_arc(arc, key):
    # part of speech of key and next element on arc must match
    # right edge of arc and left edge of key must match
    if arc[0][arc[2] + 1] == key[0] and arc[1][1] == key[1]:
        arc[1][1] = key[2]
        arc[3][arc[2]] = key[3]
        arc[2] += 1
        return(arc)
    return([])


# Returns the keys for this sentence as a list
def make_input_list(sequence):
    input = []
    i = 0
    for word in sequence:
        key = [word, i, i + 1]
        i += 1
        input.append(key)
    return(input)


# Reads the given lexicon file into the stored lexicon
# and replaces the old one
def read_lexicon(file):
    lexicon = {}
    pos_set = set()
    # read in lexicon file
    with open(file) as f:
        while True:
            line = f.readline()
            if line == '':
                break
            line = line.split(':')
            pos = line[0]
            words = line[1].split(',')
            for word in words:
                if word != '':
                    add_word(word.lower().strip(), pos.strip())


# Reads the given grammar file into the stored grammar,
# and replaces the old one
def read_grammar(file):
    grammar = {}
    # read in grammar file
    with open(file) as f:
        while True:
            line = f.readline()
            if line == '':
                break
            add_rule(line)


# Adds the given word and its part of speech to the lexicon
def add_word(word, pos, prompt=False):
    if word not in lexicon:
        lexicon[word] = [pos]
    else:
        lis = lexicon[word]
        lis.append(pos)
        lexicon[word] = lis
    if pos not in pos_set:
        pos_set.add(pos)


# Adds the given rule to the grammar
def add_rule(rule):
    rule = rule.split('-->')
    left = rule[0].strip()
    right = [node.strip() for node in rule[1].split()]
    rule = [left] + right
    if right[0] not in grammar:
        grammar[right[0]] = [rule]
    else:
        lis = grammar[right[0]]
        lis.append(rule)
        grammar[right[0]] = lis
    return True


# Returns the parts of speech of the given
# word as a string if in the lexicon, an
# empty string otherwise
def search_word(word):
    if word in lexicon:
        output = '\t'
        index = 0
        for item in lexicon[word]:
            output += item
            if index < len(lexicon[word]) - 1:
                output += ', '
            index += 1
        return(output)
    return('')


# Returns the given arc list as a print-friendly string
def arc_list_to_str(arc_list):
    output = ''
    for arc in arc_list:
        output += '\t' + arc_to_str(arc) + '\n'
    return(output)


# Returns the given arc as a print-friendly string
def arc_to_str(arc):
    output = '<' + str(arc[1][0]) + '> ' + arc[0][0] + ' --> '
    index = 0
    dotted = False
    for i in range(1, len(arc[0])):
        if index == arc[2]:
            output += '* '
            dotted = True
        output += arc[0][i] + ' '
        index += 1
    if not dotted:
        output += '* '
    output += '<' + str(arc[1][1]) + '>'
    return(output)


# Returns the input list as a print-friendly string
def input_list_to_str(input_list):
    output = []
    for item in input_list:
        output.append('\t{}\n'.format(key_to_str(item)))
    return ''.join(output)


# Returns the key list as a print-friendly string
def key_list_to_str(key_list):
    output = []
    for item in key_list:
        output.append('\t{}\n'.format(key_to_str(item)))
    return ''.join(output)


# Returns the given key as a print-friendly string
def key_to_str(key):
    return '<{}> {} <{}>'.format(str(key[1]), key[0], str(key[2]))


# Returns the part of speech list as a print-friendly string
def pos_to_str(pos_set):
    output = '\t'
    index = 0
    for item in pos_set:
        output += item
        if index < len(pos_set) - 1:
            output += ', '
        index += 1
    output += '\n'
    return(output)


# Returns the chart as a print-friendly string
# [arc2[0][0], arc2[1][0], arc2[1][1], name, arc2[3]]
def chart_to_str(chart, length):
    output = '    ' * 2
    for i in range(length):
        output += str(i) + '    ' * 2
    output += '\n'
    for item in chart:
        output += item[0] + '  ' * (4 - len(item[0])) + '  '
        left = item[1]
        right = item[2]
        span = right - left
        left_space = '  ' * left * 4 + '  ' * left
        mid = '-' * span * 4 + '-' * (span - 1)
        output += left_space + mid + '\n'
    output += '\n'
    return(output)


# Shows the lexicon in a window
def show_lexicon():
    if not lexicon:
        messagebox.showinfo(message="There is no lexicon to show.")
        return
    messagebox.showinfo(message=lexicon_to_str())


# Shows the grammar in a window
def show_grammar():
    if not grammar:
        messagebox.showinfo(message="There is no grammar to show.")
        return
    messagebox.showinfo(message=grammar_to_str())


# Returns the grammar as a print-friendly string
def grammar_to_str():
    output = []
    for pos in grammar:
        for item in grammar[pos]:
            output += item[0] + ' -->'
            for element in item[1:]:
                output += ' ' + element
            output += '\n'
    return(output)


# Returns the lexicon as a print-friendly string
def lexicon_to_str():
    pos_dic = {}
    for word in lexicon:
        for pos in lexicon[word]:
            if pos not in pos_dic:
                pos_dic[pos] = [word]
            else:
                lis = pos_dic[pos]
                lis.append(word)
                pos_dic[pos] = lis
    output = ''
    for pos in sorted(pos_dic):
        output += pos + ' :'
        i = 0
        for word in pos_dic[pos]:
            output += ' ' + word
            if i < len(pos_dic[pos]) - 1:
                output += ','
            i += 1
        output += '\n'
    return output


# Checks whether every word in the sentence is in the lexicon.
# If there is an unknown word, prompts for user command.
# Returns true if all words in input are in the lexicon at
# the termination of the method, False otherwise
def check_lexicon(input):
    for word in input:
        if word not in lexicon:
            message = "The word \"{}\" is not in the lexicon. ".format(word)
            message += "Would you like to add it?"
            response = messagebox.askyesno(message=message)
            if response:
                pos = simpledialog.askstring(
                    title="", prompt="Please enter a part of speech:")
                pos = pos.strip().upper()
                if pos not in pos_set:
                    pos_set.add(pos)
                add_word(word, pos)
            else:
                return(False)
    return(True)


# Prompts user for lexicon file
def import_lexicon():
    if lexicon:
        answer = messagebox.askyesnocancel(
            message="Would you like to overwrite the existing lexicon?")
        if not answer:
            return
    file = filedialog.askopenfilename()
    try:
        read_lexicon(file)
    except IOError:
        messagebox.showinfo(
            message="An error occurred while reading the lexicon file. " +
            "The lexicon has not been imported properly.")
        return
    else:
        messagebox.showinfo(message="Lexicon successfully imported.")


# Prompts user for grammar file
def import_grammar():
    if grammar:
        answer = messagebox.askyesnocancel(
            message="Would you like to overwrite the existing grammar?")
        if not answer:
            return
    file = filedialog.askopenfilename()
    try:
        read_grammar(file)
    except IOError:
        messagebox.showinfo(
            message="An error occurred while reading the grammar " +
            "file. The grammar has not been imported properly.")
        return
    else:
        messagebox.showinfo(message="Grammar successfully imported.")
        print(grammar)


# Prompts user for a word to add to the lexicon
def prompt_word():
    while True:
        word = simpledialog.askstring(title="", prompt="Please enter a word:")
        # user has cancelled
        if word is None:
            return
        word = word.strip()
        if not word:
            continue
    while True:
        pos = simpledialog.askstring(
            title="", prompt="Please enter a part of speech:")
        # user has cancelled
        if pos is None:
            return
        pos = pos.strip().upper()
        if not pos:
            continue
        pos_set.add(pos)
    add_word(word, pos, True)
    message = "{} : {} has been added to the lexicon"
    messagebox.showinfo(message=message.format(pos, word))


# Prompts user for a rule to add to the grammar
def prompt_rule():
    prompt = \
        "Please enter a new rule in the form\n\n" +\
        "NONTERMINAL --> TERMINAL1 (TERMINAL2) ... (NONTERMINAL1) ... \n\n"
    rule = simpledialog.askstring(title="", prompt=prompt)
    if rule is None:
        return
    rule = rule.upper().strip()
    success = add_rule(rule)
    if success:
        messagebox.showinfo(
            message="Added {} to the grammar.".format(rule))
    else:
        messagebox.showinfo(
            message="Failed to add {} to the grammar.".format(rule))


# Prompts user for a word to search
def prompt_search():
    if lexicon == {}:
        messagebox.showinfo(message="Please import a lexicon first.")
        return
    word = simpledialog.askstring(title="", prompt="Please enter a word:")
    if word is None:
        return
    word = word.lower().strip()
    result = search_word(word)
    if result != "":
        message = "The part(s) of speech of {} is/are:\n\n{}"
        messagebox.showinfo(message=message.format(word, result))
    else:
        answer = messagebox.askyesno(
            message="That word is not in the lexicon. " +
            "Would you like to add it?")
        if answer:
            pos = simpledialog.askstring(
                title="", prompt="Please enter a part of speech:")
            if pos is None:
                return
            pos = pos.strip().upper()
            message = "\"{}\" and {} have been added to the lexicon."
            messagebox.showinfo(message=message.format(word, pos))
            if pos not in pos_set:
                pos_set.add(pos)
            add_word(word, pos, True)


# Handles user input for parsing
def parse_sentence(*args):
    if not lexicon:
        messagebox.showinfo(message="Please import a lexicon first.")
        return
    if not grammar:
        messagebox.showinfo(message="Please import a grammar first.")
        return
    input = sentence.get().split()
    proceed = check_lexicon(input)
    if proceed:
        answer = messagebox.askyesno(message="Would you like a verbose parse?")
        if answer:
            verbose_parse(sentence)
        else:
            regular_parse(sentence)
    else:
        messagebox.showinfo(message="Sentence failed to parse.")


# Asks user for save file info, exits program.
def exit(*args):
    for lang_set, name in zip((lexicon, grammar), ('lexicon', 'grammar')):
        message = "Would you like to save the {}?".format(name)
        if lang_set and messagebox.askyesnocancel(message=message):
            file = filedialog.asksaveasfilename()
            with open(file, 'w') as f:
                f.write(lexicon_to_str())
    mainframe.quit()


# constructs graphical interface
root = Tk()
root.title("Interactive Parser")

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

sentence = StringVar()
parse = StringVar()

ttk.Button(mainframe, text='Show Lexicon', width=15, command=show_lexicon).grid(column=1, row=1, sticky=W)
ttk.Button(mainframe, text='Show Grammar', width=15, command=show_grammar).grid(column=1, row=2, sticky=W)
ttk.Button(mainframe, text='Add a Word', width=15, command=prompt_word).grid(column=2, row=1, sticky=W)
ttk.Button(mainframe, text='Add a Rule', width=15, command=prompt_rule).grid(column=2, row=2, sticky=W)
ttk.Button(mainframe, text='Import Lexicon', width=15, command=import_lexicon).grid(column=3, row=1, sticky=W)
ttk.Button(mainframe, text='Import Grammar', width=15, command=import_grammar).grid(column=3, row=2, sticky=W)
ttk.Button(mainframe, text='Search for Word', width=15, command=prompt_search).grid(column=1, row=8, sticky=W)
sentence_entry = ttk.Entry(mainframe, width=15, textvariable=sentence)
sentence_entry.grid(column=2, row=5, columnspan=2, sticky=(W, E))
ttk.Button(mainframe, text='Parse', width=15, command=parse_sentence).grid(column=3, row=6, sticky=E)
ttk.Button(mainframe, text='Exit', width=10, command=exit).grid(column=3, row=8, sticky=E)
ttk.Label(mainframe, text='Enter a sentence:').grid(column=1, row=5, sticky=E)
ttk.Label(mainframe, text='').grid(column=1, row=3, sticky=E)
ttk.Label(mainframe, text='').grid(column=1, row=7, sticky=E)

for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)  # adds padding around every widget

sentence_entry.focus()  # user doesn't have to click first
root.bind('<Return>', parse_sentence)

root.mainloop()
