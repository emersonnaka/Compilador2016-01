import ply.lex as lex

# Palavras Reservadas
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

# Tokens
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

# Expressões regulares simples.
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

# Expressão regular de ponto flutuante
def t_N_FLUTUANTE(t):
    r'\d+(\.\d+)(e(\+|\-)?(\d+))?'
    t.value = float(t.value)    # parsing para ponto flutuante
    return t

# Expressão regular de inteiros
def t_N_INTEIRO(t):
    r'\d+'
    t.value = int(t.value)  # parsing para inteiro
    return t

# Expressão regular do ID
def t_ID(t):
    # r'[a-zA-Zà-ú][0-9a-zà-úA-Z]*' Aceitou um caracter que deveria ser ilegal: ÷
    r'[a-zA-Zá-ñÁ-Ñ][a-zA-Zá-ñÁ-Ñ0-9]*'
    t.type = reservadas.get(t.value, 'ID')
    return t

# Ignorar Comentarios
def t_COMMENT(t):
    r'{[^\{^\}]*}'

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NOVALINHA'
    return t

# Ignora espaços e tabulações
t_ignore = ' \t'

# Erro
# A coluna (t.lexpos) não zerava a cada linha, por isso foi retirado
def t_error(t):
    print("Caracter Ilegal '%s', linha %d" % (t.value[0], t.lineno))
    exit(1)

# Build the lexer
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