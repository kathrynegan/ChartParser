from Tkinter import *

class parser_app:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack
    
        self.lex_button = Button(frame, text = 'Show Lexicon',\
            command = self.print_lexicon)
        self.lex_button.pack()
    
        self.gram_button = Button(frame, text = 'Show Grammar',\
            command = self.print_grammar)
        self.gram_button.pack()
    
        self.add_word_button = Button(frame, text = 'Add Word',\
            command = self.add_word)
        self.add_word_button.pack()
    
        self.add_rule_button = Button(frame, text = 'Add Rule',\
            command = self.add_rule)
        self.add_rule_button.pack()
    
        self.search_button = Button(frame, text = 'Search for Word',\
            command = self.search_word)
        self.search_button.pack()
        
        self.parse_box = Entry(frame, width = 5)
        self.parse_box.pack()
    
        self.exit = Button(Frame, text = 'Exit', command = frame.quit)
        self.exit.pack()

    def ..(self):


root = Tk()

app = parser_app(root)

root.mainloop()


from tkinter import *
from tkinter import ttk

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set((0.3048 * value * 10000.0 + 0.5)/10000.0)
    except ValueError:
        pass
    
root = Tk()
root.title("Feet to Meters")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

feet = StringVar()
meters = StringVar()

feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))
ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind('<Return>', calculate)

root.mainloop()


    toolbar = Frame(root)
    lex_button = Button(toolbar, text = 'Show Lexicon',\
            command = print_lexicon())
    lex_button.pack()
    
    gram_button = Button(toolbar, text = 'Show Grammar',\
            command = print_grammar())
    gram_button.pack()
    
    add_word_button = Button(toolbar, text = 'Add Word',\
            command = add_word())
    add_word_button.pack()
    
    add_rule_button = Button(toolbar, text = 'Add Rule',\
            command = add_rule())
    add_rule_button.pack()
    
    search_button = Button(toolbar, text = 'Search for Word',\
            command = search_word())
    search_button.pack()























