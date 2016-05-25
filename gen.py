# http://llvmlite.readthedocs.io/en/latest/binding/index.html
from llvmlite import ir, binding
from semantica import Semantica
from sintatica import *
from sys import exit

class Gen:

    def __init__(self, code, optz = False, debug = False):
        semantica = Semantica(code.read())
        semantica.semanticaTopo()
        self.semantica = semantica.árvore
        self.optimization = optz
        """ builder é uma instância de llvm.core.Builder e mantem o
        controle do local atual para inserir instruções e tem métodos
        para criar novas instruções. É inicializado sempre que
        começar a gerar código para uma função"""
        self.construtor = None
        self.func = None
        self.símbolos = semantica.símbolos
        self.debug = debug
        self.escopo = "main"
        """ Cria um módulo que contém todas as funções e variáveis
        globais em um pedaço de código, é a estrutura que o LLVM
        usa para ter o código"""
        self.modulo = ir.Module('programa')
        self.genTopo(self.semantica)

# def p_programa(t):
# ''' programa : declaraVarGlobal declaraFuncao funcaoPrincipal
#              | declaraFuncao funcaoPrincipal
#              | funcaoPrincipal '''
# if (len(t) == 4):
#     t[0] = AST('declaraVarGlobalPrograma', [t[1], t[2], t[3]])
# elif (len(t) == 3):
#     t[0] = AST('declaraFuncaoPrograma', [t[1], t[2]])
# else:
#     t[0] = AST('funcaoPrincipalPrograma', [t[1]])
    def genTopo(self, nó):
        if nó.nome == 'declaraVarGlobalPrograma':
            self.genDeclaraVarGlobal(nó.filho[0])
            self.genDeclaraFuncao(nó.filho[1])
            self.genFuncaoPrincipal(nó.filho[2])
        elif nó.nome == 'declaraFuncaoPrograma':
            self.genDeclaraFuncao(nó.filho[0])
            self.genFuncaoPrincipal(nó.filho[1])
        else:
            self.genFuncaoPrincipal(nó.filho[0])

# def p_declaraVarGlobal(t):
#     ''' declaraVarGlobal : declaraVarGlobal declaraVar
#                          | declaraVar '''
#     if(len(t) == 3):
#         t[0] = AST('declaraVarGlobalComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraVarGlobal', [t[1]])
    def genDeclaraVarGlobal(self, nó):
        if nó.nome == 'declaraVarGlobalComp':
            self.genDeclaraVarGlobal(nó.filho[0])
            self.genDeclaraVar(nó.filho[1])
        else:
            self.genDeclaraVar(nó.filho[0])

# def p_declaraFuncao(t):
#     '''declaraFuncao : declaraFuncao funcao
#                      | funcao '''
#     if(len(t) == 3):
#         t[0] = AST('declaraFuncaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraFuncao', [t[1]])
    def genDeclaraFuncao(self, nó):
        if nó.nome == 'declaraFuncaoComp':
            self.genDeclaraFuncao(nó.filho[0])
            self.genFuncao(nó.filho[1])
        else:
            self.genFuncao(nó.filho[0])

# def p_funcaoPrincipal(t):
#     ' funcaoPrincipal : VAZIO PRINCIPAL ABREPARENTES FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA'
#     t[0] = AST('funcaoPrincipal', [t[6]], [t[1], t[2]])
    def genFuncaoPrincipal(self, nó):
        tipo = ir.VoidType()
        função = ir.FunctionType(tipo, ())
        principal = ir.Function(self.modulo, função, name = nó.folha[1])
        bloco = principal.append_basic_block('entry')
        self.construtor = ir.IRBuilder(bloco)
        self.genConjInstrucao(nó.filho[0])

# def p_funcao(t):
#     ' funcao : tipo ID ABREPARENTES conjParametros FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA '
#     t[0] = AST('funcao', [t[1], t[4], t[7]], [t[2]])
# Inicialmente, a chave do dicionário seria o tipo da função '.' id, entretanto, se o usuário declarasse
# um ID com o tipo diferente, não daria erro. Sendo que o correto é acusar o erro
    def genFuncao(self, nó):
        tipo = genTipo(nó.filho[0])
        função = ir.FunctionType(tipo, ())
        nomeFunção = ir.Function(self.modulo, função, name = nó.folha[0])
        bloco = nomeFunção.append_basic_block('entry')
        self.genConjParametros(nó.filho[1])
        self.genConjInstrucao(nó.filho[2])

# def p_tipo(t):
#     ''' tipo : INTEIRO
#              | FLUTUANTE
#              | VAZIO '''
#     if t[1] == 'inteiro':
#         t[0] = AST('tipoInteiro', [], t[1])
#     elif t[1] == 'flutuante':
#         t[0] = AST('tipoFlutuante', [], [t[1]])
#     else:
#         t[0] = AST('tipoVazio', [], [t[1]])
    def genTipo(self, nó):
        if(nó.folha[0] == 'inteiro'):
            return ir.IntType(32)
        elif nó.folha[0] == 'flutuante':
            return ir.FloatType()
        else:
            return ir.VoidType()


# def p_conjParametros_(t):
#     ''' conjParametros : tipo DOISPONTOS ID VIRGULA conjParametros 
#                        | tipo DOISPONTOS ID
#                        | empty '''
#     if (len(t) == 6):
#         t[0] = AST('conjParametrosComp', [t[1], t[5]], [t[3]])
#     elif (len(t) == 4):
#         t[0] = AST('conjParametros', [t[1]], [t[3]])
#     else:
#         t[0] = AST('conjParametrosEmpty', [])
    def genConjParametros(self, nó):
        if nó.nome != 'conjParametrosEmpty':
            tipo = genTipo(nó.filho[0])
            idVariável = nó.folha[0]
            variável = construtor.alloca(tipo, name = idVariável)
            if nó.nome == 'conjParametrosComp':
                self.genConjParametros(nó.filho[1])

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def genDeclaraVar(self, nó):
        tipo = genTipo(nó.filho[0])
        idVariável = nó.folha[0]
        variável = construtor.alloca(tipo, name = idVariável)

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def genChamaFuncao(self, nó):


# def p_parametros(t):
#     ''' parametros : parametros VIRGULA exprArit
#                    | exprArit
#                    | empty '''
#     if (len(t) == 4):
#         t[0] = AST('parametrosComp', [t[1], t[3]])
#     else:
#         if t[1] == 'exprArit':
#             t[0] = AST('parametrosExprArit', [t[1]])
#         else:
#             t[0] = AST('parametrosEmpty', [])
    def genParametros(self, nó):


# def p_conjInstrucao(t):
#     ''' conjInstrucao : conjInstrucao instrucao
#                       | instrucao '''
#     if (len(t) == 3):
#         t[0] = AST('conjInstrucaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('conjInstrucao', [t[1]])
    def genConjInstrucao(self, nó):


# def p_instrucao(t):
#     '''instrucao : condicional
#                  | repeticao
#                  | atribuicao
#                  | leitura
#                  | escreva
#                  | chamaFuncao
#                  | declaraVar
#                  | retorna '''
#     t[0] = AST('instrucao', [t[1]])
    def genInstrucao(self, nó):
        if nó.filho[0].nome == 'condicionalSe' or nó.filho[0].nome == 'condicionalSenao':
            self.genCondicional(nó.filho[0])
        if nó.filho[0].nome == 'repeticao':
            self.genRepeticao(nó.filho[0])
        if nó.filho[0].nome == 'atribuicao':
            self.genAtribuicao(nó.filho[0])
        if nó.filho[0].nome == 'leitura':
            self.genLeitura(nó.filho[0])
        if nó.filho[0].nome == 'escreva':
            self.genEscreva(nó.filho[0])
        if nó.filho[0].nome == 'chamaFuncao':
            self.genChamaFuncao(nó.filho[0])
        if nó.filho[0].nome == 'declaraVar':
            self.genDeclaraVar(nó.filho[0])
        if nó.filho[0].nome == 'retorna':
            self.genRetorna(nó.filho[0])

# def p_condicional(t):
#     ''' condicional : SE conjExpr ENTAO NOVALINHA conjInstrucao FIM NOVALINHA
#                     | SE conjExpr ENTAO NOVALINHA conjInstrucao SENAO NOVALINHA conjInstrucao FIM NOVALINHA '''
#     if (len(t) == 8):
#         t[0] = AST('condicionalSe', [t[2], t[5]])
#     else:
#         t[0] = AST('condicionalSenao', [t[2], t[5], t[8]])
    def genCondicional(self, nó):


# def p_repeticao(t):
#     ' repeticao : REPITA NOVALINHA conjInstrucao ATE conjExpr NOVALINHA'
#     t[0] = AST('repeticao', [t[3], t[5]])
    def genRepeticao(self, nó):


# def p_atribuicao(t):
#     ''' atribuicao : ID RECEBE conjExpr NOVALINHA
#                    | ID RECEBE chamaFuncao NOVALINHA '''
#     t[0] = AST('atribuicao', [t[3]], [t[1]])
    def genAtribuicao(self, nó):


# def p_leitura(t):
#     ' leitura : LEIA ABREPARENTES ID FECHAPARENTES NOVALINHA '
#     t[0] = AST('leitura', [], [t[3]])
    def genLeitura(self, nó):


# def p_escreva(t):
#     ''' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES NOVALINHA
#                 | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES NOVALINHA '''
#     t[0] = AST('escreva', [t[3]])
    def genEscreva(self, nó):


# def p_retorna(t):
#     ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES NOVALINHA '
#     t[0] = AST('retorna', [t[3]])
    def genRetorna(self, nó):


# def p_conjExpr(t):
#     ''' conjExpr : exprArit compara exprArit
#                  | exprArit '''
#     if (len(t ) == 4):
#         t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('conjExpr', [t[1]])
    def genConjExpr(self, nó):


# def p_compara(t):
#     ''' compara : MENOR
#                 | MAIOR
#                 | MENORIGUAL
#                 | MAIORIGUAL
#                 | IGUAL '''
#     t[0] = AST('compara', [], [t[1]])
    def genCompara(self, nó):


# def p_exprArit(t):
#     ''' exprArit : exprArit soma termo 
#                  | termo '''
#     if (len(t) == 4):
#         t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('exprArit', [t[1]])
    def genExprArit(self, nó):


# def p_soma(t):
#     ''' soma : MAIS
#              | MENOS '''
#     t[0] = AST('maisMenos', [], [t[1]])
    def genSoma(self, nó):


# def p_termo(t):
#     ''' termo : termo multi fator
#               | fator '''
#     if (len(t) == 4):
#         t[0] = AST('termoComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('termo', [t[1]])
    def genTermo(self, nó):


# def p_multi(t):
#     ''' multi : VEZES
#               | DIVIDIR '''
#     t[0] = AST('vezesDividir', [], [t[1]])
    def genMulti(self, nó):


# def p_fator_1(t):
#     ' fator : ABREPARENTES exprArit FECHAPARENTES '
#     t[0] = AST('fatorExprArti', [t[1]])
# def p_fator_2(t):
#     ' fator : num '
#     t[0] = AST('num', [t[1]])
# def p_fator_3(t):
#     ' fator : ID '
#     t[0] = AST('fatorID', [], [t[1]])
    def genFator(self, nó):
