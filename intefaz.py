import tkinter as tk
from tkinter import END, Text, ttk
from tkinter import filedialog
import ply.lex as lex
import ply.yacc as yacc
import subprocess
from tkinter.filedialog import askopenfilename
import os
import graphviz
from PIL import Image, ImageTk

lexerErrors = ""
image_path = r'C:\Users\luisa\Documents\Semestre 2023\compiladores\proyecto\syntax_tree.png'

def print_tree(node):
    if isinstance(node, tuple):
        label = node[0]
        children = node[1:]
        dot.node(str(node), label)
        for child in children:
            if isinstance(child, tuple):
                child_label = child[0]
                child_node = str(child)
                dot.node(child_node, child_label)
                dot.edge(str(node), child_node)
                print_tree(child)
            else:
                child_node = str(child)
                dot.node(child_node, str(child))
                dot.edge(str(node), child_node)
    else:
        dot.node(str(node), str(node))

def p_error(p):
    print("Error!!",p)
    errorBox.delete(1.0,END)
    errorBox.insert(1.0,"Error de semantica: "+str(p)+"\n")
    archivo_salida = open("erroresYacc.txt", "a")
    # Escribir contenido en el archivo
    archivo_salida.write("Error de semantica: "+str(p)+"\n")
    # Cerrar el archivo
    archivo_salida.close()
    
def p_program(p):
    '''program : PROGRAM OBRACKET statement_list CBRACKET
            |    PROGRAM OBRACKET CBRACKET'''
    if len(p) == 4:
        p[0] = ('program',p[1])
    else:
        p[0] = ('program', p[3])

def p_statement_list(p):
    '''statement_list : statement 
            | statement_list statement'''
    if len(p) == 2:
        p[0] = ('statement_list',p[1])
    else: 
        p[0] = ('statement_list',p[1],p[2])

def p_statement(p):
    '''statement : sent_assign
            |      write_statement
            |      var_declaration_statement
            |      if_statement
            |      iteration_statement
        '''
    p[0] = ('statement',p[1])

def p_do_while_statement(p):
    '''do_while_statement : DO OBRACKET statement_list CBRACKET UNTIL LPAREN sent_assign RPAREN'''
    p[0] = ('do_while_statement', p[1], p[3], p[5], p[7])

def p_for_statement(p):
    'for_statement : FOR LPAREN sent_assign sent_assign RPAREN OBRACKET statement_list CBRACKET'
    p[0] = ('for_statement', p[3], p[4], p[7])
def p_while_statement(p):
    'while_statement : WHILE LPAREN sent_assign RPAREN OBRACKET statement_list CBRACKET' 
    p[0] = ('while_statement', p[3], p[6])
    
def p_iteration_statement(p):
    '''iteration_statement : for_statement
                           | while_statement
                           | do_while_statement '''
    p[0] = ('iteration_statement', p[1])

def p_if_statement(p):
    '''if_statement : IF LPAREN sent_assign RPAREN OBRACKET statement_list CBRACKET FI
                    | IF LPAREN sent_assign RPAREN OBRACKET statement_list CBRACKET ELSE OBRACKET statement_list CBRACKET FI'''
    if len(p) == 9:
        p[0] = ('if_statement', p[1], p[3], p[6])
    else:
        p[0] = ('if_statement', p[1], p[3], p[6], p[8], p[10])

def p_var_declaration_statement(p):
    '''var_declaration_statement : type_declaration ID COMA var_declaration_statement
                                |  ID COMA var_declaration_statement
                                |  ID SEMICOLON 
                                |  type_declaration ID SEMICOLON'''
    if len(p) == 5:
        p[0] = ('var_declaration_statement',p[1],p[2],p[4])
    elif len(p) == 4:
        if (p[1][0] == 'type_declaration'):
            p[0] = ('var_declaration_statement1',p[1],p[2])
        else:
            p[0] = ('var_declaration_statement2',p[1],p[3])
    else :
        p[0] = ('var_declaration_statement',p[1])

def p_type_declaration(p):
    '''type_declaration : INT 
                        | CHAR
                        | FLOAT
                        | BOOL'''
    p[0] = ('type_declaration',p[1])
def p_write_statement(p):
    '''write_statement : WRITE ID SEMICOLON'''

    p[0] = ("write_statement",p[1],p[2])

def p_sent_assign(p):
    '''sent_assign : ID EQUAL exp_bool SEMICOLON
                | exp_bool SEMICOLON'''
    if len(p) == 3:
        p[0] = ("sent_assign",p[1])  # El árbol de análisis sintáctico simplemente toma la comb directamente
    else:
        p[0] = ("sent_assign", p[1], p[3])  # El árbol de análisis sintáctico tiene el operador de asignación, el identificador y la expresión booleana correspondiente

def p_exp_bool(p):
    '''exp_bool : exp_bool OR comb
                | comb'''
    if len(p) == 2:
        p[0] = ("exp_bool",p[1])  # El árbol de análisis sintáctico simplemente toma la comb directamente
    else:
        p[0] = ("exp_bool",p[2], p[1], p[3])  # El árbol de análisis sintáctico tiene el operador lógico OR y las comb correspondientes

def p_comb(p):
    '''comb : comb AND igualdad
            | igualdad'''
    if len(p) == 2:
        p[0] = ("comb", p[1])  # El árbol de análisis sintáctico simplemente toma la igualdad directamente
    else:
        p[0] = ("comb", p[2], p[1], p[3])  # El árbol de análisis sintáctico tiene el operador lógico AND y las igualdades correspondientes

def p_igualdad(p):
    '''igualdad : igualdad EQUALEQUAL rel
                | igualdad DIFFEQUAL rel
                | rel'''
    if len(p) == 2:
        p[0] = ("igualdad", p[1]) # El árbol de análisis sintáctico simplemente toma el rel directamente
    else:
        p[0] = ("igualdad",p[2], p[1], p[3])
def p_rel(p):
    '''rel : expr op_rel expr
            | expr'''
    if len(p) == 2:
        p[0] = ("rel", p[1]) # El árbol de análisis sintáctico simplemente toma el rel directamente
    else:
        p[0] = ("rel",p[2], p[1], p[3]) 
     # El árbol de análisis sintáctico tiene el operador de comparación y las expresiones correspondientes

def p_op_rel(p):
    '''op_rel : LEESTHAN
              | MORETHAN
              | LEESETHAN
              | MOREETHAN'''
    p[0] = ('op_rel',p[1])   # El árbol de análisis sintáctico simplemente toma el operador de comparación directamente

def p_expr(p):
    '''expr : expr MINUS term
            | expr PLUS term
            | term'''
    if len(p) == 2:
        p[0] = ('expr',p[1])  # El árbol de análisis sintáctico simplemente toma el term directamente
    else:
        p[0] = ('expr',p[2], p[1], p[3])  # El árbol de análisis sintáctico tiene el operador y los términos correspondientes

def p_term(p):
    '''term : term TIMES unario
            | term DIVIDE unario
            | unario'''
    if len(p) == 2:
        p[0] = ('term',p[1])  # El árbol de análisis sintáctico simplemente toma el unario directamente
    else:
        p[0] = ('term', p[2], p[1], p[3])  # El árbol de análisis sintáctico tiene el operador y los términos correspondientes

def p_unario(p):
    '''unario : NOT unario
              | MINUS unario
              | factor'''
    if len(p) == 2:
        p[0] = ('unario', p[1])
    else:
        p[0] = ('unario', p[1], p[2]) 
def p_factor(p):
    '''factor : LPAREN RPAREN
              | ID
              | NUMBER
              | DOUBLE
              | TRUE
              | FALSE'''
    if len(p) == 2:
        p[0] = ('factor', p[1])
    else:
        p[0] = ('factor', p[2])

reserved = {
    'program' : 'PROGRAM',
    'if': 'IF',
    'else': 'ELSE',
    'fi' : 'FI',
    'do' : 'DO',
    'until' : 'UNTIL',
    'for': 'FOR',
    'while': 'WHILE',
    'read' : 'READ',
    'write': 'WRITE',
    'int' : 'INT',
    'char': 'CHAR',
    'float' : 'FLOAT',
    'bool' : 'BOOL',
    'not' : 'NOT',
    'and' : 'AND',
    'or' : 'OR',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'break' : 'BREAK'
}

tokens = [
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'EXPONENT',
    'DOUBLE',
    'ID',
    'EQUAL',
    'POINT',
    'RESERVED',
    'LEESTHAN',
    'MORETHAN',
    'OBRACKET',
    'CBRACKET',
    'SEMICOLON',
    'COLON',
    'MARK',
    'DOUBLEMARK',
    'MOREETHAN',
    'LEESETHAN',
    'EQUALEQUAL',
    'DIFFEQUAL',
    'COMA'
] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_MARK = r'\''
t_DOUBLEMARK = r'\"'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EXPONENT = r'\^'
t_EQUAL = r'='
t_EQUALEQUAL = r'=='
t_DIFFEQUAL = r'!='
t_LEESTHAN = r'<'
t_MORETHAN = r'>'
t_LEESETHAN = r'<='
t_MOREETHAN = r'>='
t_OBRACKET = r'\{'
t_CBRACKET = r'\}'
t_SEMICOLON = r';'
t_COLON = r':'
t_COMA = r','

def t_DOUBLE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
def t_COMMENT(t):
    r'\//.*'
    pass

t_ignore = ' \t'

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    print(t)
    errorBox.delete(1.0,END)
    errorBox.insert(1.0,"Illegal character '%s'" % t.value[0]+"at line: "+str(t.lineno)+"\n")
    archivo_salida = open("erroresLexer.txt", "a")
    # Escribir contenido en el archivo
    archivo_salida.write("Illegal character '%s'" % t.value[0]+"at line: "+str(t.lineno)+"\n")
    # Cerrar el archivo
    archivo_salida.close()
    t.lexer.skip(1)


def cambiaPalabra():   
    os.chdir("c:/Users/luisa/Documents/Semestre 2023/compiladores/proyecto/")
    print(os.getcwd())
    archivo_salida = open("erroresLexer.txt", "w")
    archivo_salida.write("")
    
    entry1.delete(1.0,END)
    entry2.delete(1.0,END)
    lexString = ""
    result = ""
    parser = ""
    dataForYacc = ""
    image = ""
    photo = ""
    tokens_formateados = []
    dataForLexer = textBox.get(1.0,END)
    dataForYacc = textBox.get(1.0,END)
    print(dataForLexer)
    lexer = lex.lex()
    lexer.input(dataForLexer)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
        lexString += str(tok)+"\n"
        token_formateado = f"{tok.type}\t\t{tok.value}\t\t{tok.lineno}\t\t{tok.lexpos}\n"
        tokens_formateados.append(token_formateado)
        
    dataForLexer = "Clave\t\tLexema\t\tFila\t\tColumna\n" + "".join(tokens_formateados)
    #ANALIZADOR SINTACTICO
    try:
        parser = yacc.yacc()
        result = parser.parse(dataForYacc)
        print(result)
        print_tree(result)
        dot.format = 'png'  # Puedes cambiar el formato a 'pdf', 'svg', etc.
        dot.render('C:/Users/luisa/Documents/Semestre 2023/compiladores/proyecto/syntax_tree')
    except Exception as exception:
        print('error', exception)
    entry1.insert(1.0, dataForLexer)
    entry2.insert(1.0, result)
    image = Image.open('C:/Users/luisa/Documents/Semestre 2023/compiladores/proyecto/syntax_tree.png')  # Reemplaza con la ruta de tu imagen
    image = image.resize((200, 200))  # Ajusta el tamaño de la imagen según tus necesidades

    print(image)
    photo = ImageTk.PhotoImage(image)
    print(photo)
    entry3.image_create(1.0, image=photo)
    subprocess.run(['cmd', '/c', 'start', '', image_path], shell=True)

    errorBox.delete(1.0,END)
    archivo_salida = open("salidaLexer.txt", "w")
    archivo_salida2 = open("salidaYacc.txt", "w")
    # Escribir contenido en el archivo
    archivo_salida.write(dataForLexer)
    archivo_salida2.write(str(result))
    # Cerrar el archivo
    archivo_salida.close()
    archivo_salida2.close()

def abrirArchivo():
     # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)
    f = open(filename, "r")
    # Leer el contenido del archivo y guardarlo en una variable
    contenido = f.read()
    # Imprimir el contenido del archivo
    print(contenido)
    textBox.insert(1.0,contenido)
    # Cerrar el archivo
    f.close()
def guardarArchivo():
    f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return
    text2save = str(textBox.get(1.0, END)) # starts from `1.0`, not `0.0`
    f.write(text2save)
    f.close() # `()` was missing.

dot = graphviz.Digraph()

app = tk.Tk()
app.geometry("1200x800") #Anchura por altura
app.configure(background="#282c34")
app.title("Interfaz")
app.columnconfigure(index=0,weight=3)
app.rowconfigure(index=1,weight= 3)

textBox = tk.Text(app)
textBox.grid(row=1,column=0, columnspan = 2, sticky = "N",padx = (30,5) )

notebook = ttk.Notebook(app)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)

notebook.add(tab1, text="Analisis Lexico")
notebook.add(tab2, text="Analisis Sintactico")
notebook.add(tab3, text="Analisis Semantico")

entry1 = tk.Text(tab1)
entry2 = tk.Text(tab2)
entry3 = tk.Text(tab3)

entry1.pack()
entry2.pack()
entry3.pack()

notebook.grid(row=0,column=2, rowspan = 2, sticky="NW",padx=(5,30),pady=(20,0) )

errorBox = Text(app,height=10)
errorBox.grid(row=2,column=0,columnspan=3,sticky="EW",padx=30, pady=30)

tk.Button(app,
          text="Run",
          font=("Courier",14),
          bg="#00a8e8",
          fg="white",width=10,
          command=cambiaPalabra).grid(row=0, column=1,padx = (0,320))
tk.Button(app,
          text="Open File",
          font=("Courier",14),
          bg="#00a8e8",width=10,
          fg="white",command=abrirArchivo).grid(row=0,column=1,sticky = "W",padx =(130,0),pady = 5)
tk.Button(app,
          text="Save File",
          font=("Courier",14),
          bg="#00a8e8",width=10,
          fg="white",command=guardarArchivo).grid(row=0,column=0,sticky = "W",padx =(30,0),pady = 5)


app.mainloop()
