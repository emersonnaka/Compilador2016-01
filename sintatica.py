import ply.yacc as yacc
from lexica import tokens
from ast import *

precedence = (
    ('left', 'MAIS', 'MENOS'),
    ('left', 'VEZES', 'DIVIDIR'),
)

# programa -> declaraVarGlobal declaraFuncao funcaoPrincipal
#           | declaraFuncao funcaoPrincipal
#           | funcaoPrincipal
def p_programa(t):
    ''' programa : declaraVarGlobal declaraFuncao funcaoPrincipal
                 | declaraFuncao funcaoPrincipal
                 | funcaoPrincipal '''
    if (len(t) == 4):
        t[0] = AST('declaraVarGlobalPrograma', [t[1], t[2], t[3]])
    elif (len(t) == 3):
        t[0] = AST('declaraFuncaoPrograma', [t[1], t[2]])
    else:
        t[0] = AST('funcaoPrincipalPrograma', [t[1]])

# declaraVarGlobal -> declaraVarGlobal declaraVar
#                | declaraVar
def p_declaraVarGlobal(t):
    ''' declaraVarGlobal : declaraVarGlobal declaraVar
                         | declaraVar '''
    if(len(t) == 3):
        t[0] = AST('declaraVarGlobalComp', [t[1], t[2]])
    else:
        t[0] = AST('declaraVarGlobal', [t[1]])

# declaraFuncao -> funcao declaraFuncao
#                | funcao
def p_declaraFuncao(t):
    '''declaraFuncao : declaraFuncao funcao
                     | funcao '''
    if(len(t) == 3):
        t[0] = AST('declaraFuncaoComp', [t[1], t[2]])
    else:
        t[0] = AST('declaraFuncao', [t[1]])

# funcaoPrincipal -> VAZIO PRINCIPAL ABREPARENTES FECHAPARENTES novaLinha conjInstrucao FIM
def p_funcaoPrincipal(t):
    ' funcaoPrincipal : VAZIO PRINCIPAL ABREPARENTES FECHAPARENTES novaLinha conjInstrucao FIM novaLinha'
    t[0] = AST('funcaoPrincipal', [t[6]], [t[1], t[2]])

# funcao -> tipo ID ABREPARENTES conjParametros FECHAPARENTES novaLinha conjInstrucao FIM novaLinha
def p_funcao(t):
    ' funcao : tipo ID ABREPARENTES conjParametros FECHAPARENTES novaLinha conjInstrucao FIM novaLinha '
    t[0] = AST('funcao', [t[1], t[4], t[7]], [t[2]])

# conjParametros -> tipo DOISPONTOS ID VIRGULA conjParametros
#                 | tipo DOISPONTOS ID
#                 | vazio
def p_conjParametros_(t):
    ''' conjParametros : tipo DOISPONTOS ID VIRGULA conjParametros 
                       | tipo DOISPONTOS ID
                       | empty '''
    if (len(t) == 6):
        t[0] = AST('conjParametrosComp', [t[1], t[5]], [t[3]])
    elif (len(t) == 4):
        t[0] = AST('conjParametros', [t[1]], [t[3]])
    else:
        t[0] = AST('conjParametrosEmpty', [])

# declaraVar -> tipo DOISPONTOS ID novaLinha
def p_declaraVar(t):
    ' declaraVar : tipo DOISPONTOS ID novaLinha '
    t[0] = AST('declaraVar', [t[1]], [t[3]])

# tipo -> INTEIRO
#       | FLUTUANTE
#       | VAZIO
def p_tipo(t):
    ''' tipo : INTEIRO
             | FLUTUANTE
             | VAZIO '''
    if t[1] == 'inteiro':
        t[0] = AST('tipoInteiro', [], [t[1]])
    elif t[1] == 'flutuante':
        t[0] = AST('tipoFlutuante', [], [t[1]])
    else:
        t[0] = AST('tipoVazio', [], [t[1]])

# chamaFuncao -> ID ABREPARENTES parametros FECHAPARENTES
def p_chamaFuncao(t):
    ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
    t[0] = AST('chamaFuncao', [t[3]], [t[1]])

# parametros -> parametros VIRGULA exprArit
#             | exprArit
#             | vazio
def p_parametros1(t):
    ' parametros : parametros VIRGULA exprArit '
    t[0] = AST('parametrosComp', [t[1], t[3]])

def p_parametros2(t):
    ' parametros : exprArit '
    t[0] = AST('parametrosExprArit', [t[1]])

def p_parametros3(t):
    ' parametros : empty '
    t[0] = AST('parametrosEmpty', [])

# conjInstrucao -> conjInstrucao instrucao
#                | instrucao
def p_conjInstrucao(t):
    ''' conjInstrucao : conjInstrucao instrucao
                      | instrucao '''
    if (len(t) == 3):
        t[0] = AST('conjInstrucaoComp', [t[1], t[2]])
    else:
        t[0] = AST('conjInstrucao', [t[1]])

# instrucao -> condicional
#            | repeticao
#            | atribuicao
#            | leitura
#            | escreva
#            | chamaFuncao
#            | declaraVar
#            | retorna
def p_instrucao(t):
    '''instrucao : condicional
                 | repeticao
                 | atribuicao
                 | leitura
                 | escreva
                 | chamaFuncao novaLinha
                 | declaraVar
                 | retorna '''
    t[0] = AST('instrucao', [t[1]])

# condicional -> SE conjExpr ENTAO novaLinha conjInstrucao FIM novaLinha
#              | SE conjExpr ENTAO novaLinha conjInstrucao SENAO novaLinha conjInstrucao FIM novaLinha
def p_condicional(t):
    ''' condicional : SE conjExpr ENTAO novaLinha conjInstrucao FIM novaLinha
                    | SE conjExpr ENTAO novaLinha conjInstrucao SENAO novaLinha conjInstrucao FIM novaLinha '''
    if (len(t) == 8):
        t[0] = AST('condicionalSe', [t[2], t[5]])
    else:
        t[0] = AST('condicionalSenao', [t[2], t[5], t[8]])

# repeticao -> REPITA conjInstrucao ATE conjExpr novaLinha
def p_repeticao(t):
    ' repeticao : REPITA novaLinha conjInstrucao ATE conjExpr novaLinha'
    t[0] = AST('repeticao', [t[3], t[5]])

# atribuicao -> ID RECEBE conjExpr novaLinha
def p_atribuicao(t):
    ''' atribuicao : ID RECEBE conjExpr novaLinha
                   | ID RECEBE chamaFuncao novaLinha '''
    t[0] = AST('atribuicao', [t[3]], [t[1]])

# leitura -> LEIA ABREPARENTES ID FECHAPARENTES novaLinha
def p_leitura(t):
    ' leitura : LEIA ABREPARENTES ID FECHAPARENTES novaLinha '
    t[0] = AST('leitura', [], [t[3]])

# escreva -> ESCREVA ABREPARENTES conjExpr FECHAPARENTES novaLinha
#          | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES novaLinha
def p_escreva(t):
    ''' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES novaLinha
                | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES novaLinha '''
    t[0] = AST('escreva', [t[3]])

# retorna -> RETORNA ABREPARENTES exprArit FECHAPARENTES novaLinha
def p_retorna(t):
    ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES novaLinha '
    t[0] = AST('retorna', [t[3]])

# conjExpr -> exprArit compara exprArit
#           | exprArit
def p_conjExpr(t):
    ''' conjExpr : exprArit compara exprArit
                 | exprArit '''
    if (len(t) == 4):
        t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
    else:
        t[0] = AST('conjExpr', [t[1]])

# compara -> MENOR
#          | MAIOR
#          | MENORIGUAL
#          | MAIORIGUAL
#          | IGUAL
def p_compara(t):
    ''' compara : MENOR
                | MAIOR
                | MENORIGUAL
                | MAIORIGUAL
                | IGUAL '''
    t[0] = AST('compara', [], [t[1]])

# exprArit -> exprArit soma termo
#          | termo
def p_exprArit(t):
    ''' exprArit : exprArit soma termo 
                 | termo '''
    if (len(t) == 4):
        t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
    else:
        t[0] = AST('exprArit', [t[1]])

# soma -> MAIS
#      | MENOS
def p_soma(t):
    ''' soma : MAIS
             | MENOS '''
    t[0] = AST('maisMenos', [], [t[1]])

# termo -> termo multi fator
#       | fator
def p_termo(t):
    ''' termo : termo multi fator
              | fator '''
    if (len(t) == 4):
        t[0] = AST('termoComp', [t[1], t[2], t[3]])
    else:
        t[0] = AST('termo', [t[1]])

# multi -> VEZES
#       | DIVIDIR
def p_multi(t):
    ''' multi : VEZES
              | DIVIDIR '''
    t[0] = AST('vezesDividir', [], [t[1]])

# fator -> ABREPARENTES exprArit FECHAPARENTES
#       | num
#       | ID
def p_fator_1(t):
    ' fator : ABREPARENTES exprArit FECHAPARENTES '
    t[0] = AST('fatorExprArit', [t[1]])

def p_fator_2(t):
    ' fator : num '
    t[0] = AST('num', [t[1]])

def p_novaLinha(t):
    ''' novaLinha : NOVALINHA 
                  | NOVALINHA novaLinha '''

def p_fator_3(t):
    ' fator : ID '
    t[0] = AST('fatorID', [], [t[1]])

# num -> N_INTEIRO
#      | N_FLUTUANTE
def p_num_1(t):
    ' num : N_INTEIRO '
    t[0] = AST('n_inteiro', [], [t[1]])

def p_num_2(t):
    ' num : N_FLUTUANTE '
    t[0] = AST('n_flutuante', [], [t[1]])

def p_empty(t):
    ' empty : '

def p_error(t):
    if t:
        print ("Erro sintático: '%s' Linha '%d" % (t.value, t.lineno))
        exit(1)
    else:
        yacc.restart()
        print ("Erro sintático")
        exit(1)

def parse_tree(code):
    parser = yacc.yacc(debug=True)
    return parser.parse(code)

if __name__ == '__main__':
    import sys
    parser = yacc.yacc(debug=True)
    code = open(sys.argv[1])
    if 'a' in sys.argv:
        print(parser.parse(code.read()))
    else:
        parser.parse(code.read())