import ply.lex as lex

reservadas = {
    'se': 'SE',
    'então': 'ENTAO',
    'senão': 'SENAO',
    'fim': 'FIM',
    'repita': 'REPITA',
    'até': 'ATE',
    'leia': 'LEIA',
    'escreva': 'ESCREVA',
    'inteiro': 'INTEIRO',
    'flutuante': 'FLUTUANTE',
    'vazio': 'VAZIO',
    'principal': 'PRINCIPAL',
    'retorna': 'RETORNA'
}

tokens = [
    'N_FLUTUANTE',
    'N_INTEIRO',
    'MAIS',
    'MENOS',
    'VEZES',
    'DIVIDIR',
    'IGUAL',
    'VIRGULA',
    'RECEBE',
    'MENOR',
    'MAIOR',
    'MENORIGUAL',
    'MAIORIGUAL',
    'ABREPARENTES',
    'FECHAPARENTES',
    'NOVALINHA',
    'DOISPONTOS',
    'ID'
] + list(reservadas.values())

t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_DIVIDIR = r'\/'
t_IGUAL = r'\='
t_VIRGULA = r'\,'
t_MENOR = r'\<'
t_MAIOR = r'\>'
t_MENORIGUAL = r'\<='
t_MAIORIGUAL = r'\>='
t_ABREPARENTES = r'\('
t_FECHAPARENTES = r'\)'
t_DOISPONTOS = r'\:'
t_RECEBE = r':\='

def t_N_FLUTUANTE(t):
    r'\d+(\.\d+)(e(\+|\-)?(\d+))?'
    t.value = float(t.value)
    return t

def t_N_INTEIRO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Zá-ñÁ-Ñ][a-zA-Zá-ñÁ-Ñ0-9]*'
    t.type = reservadas.get(t.value, 'ID')
    return t

def t_COMMENT(t):
    r'{[^\{^\}]*}'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NOVALINHA'
    return t

t_ignore = ' \t'

def t_error(t):
    print("Caracter Ilegal '%s', linha %d" % (t.value[0], t.lineno))
    exit(1)

lexico = lex.lex()

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    lex.input(code.read())
    while True:
        tok = lex.token()
        if not tok:
            break
        print(tok)