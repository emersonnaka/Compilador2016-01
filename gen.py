# http://llvmlite.readthedocs.io/en/latest/index.html
from llvmlite import ir, binding
from semantica import Semantica
from sintatica import *
from sys import exit

class Gen:

    def __init__(self, code):
        semantica = Semantica(code.read())
        semantica.semanticaTopo()
        self.semantica = semantica.árvore
        # self.optimization = optz
        self.construtor = None
        self.func = None
        self.símbolos = semantica.símbolos
        # self.debug = debug
        self.escopo = 'global'
        self.modulo = ir.Module('programa')
        self.genTopo(self.semantica)
        print(self.modulo)

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
        self.escopo = nó.folha[1]
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
        self.escopo = nó.folha[0]
        tipo = self.genTipo(nó.filho[0])
        função = ir.FunctionType(tipo, ())
        nomeFunção = ir.Function(self.modulo, função, name = nó.folha[0])
        bloco = nomeFunção.append_basic_block('entry')
        self.construtor = ir.IRBuilder(bloco)
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
        parametros = []
        if len(nó.filho) > 0:
            tipo = self.getTipo(nó.filho[0])
            idVariável = nó.folha[0]
            parametros.append(tipo, idVariável)
            if len(nó.filho) > 1:
                parametros = parametros + self.genConjParametros(nó.filho[1])
        return parametros

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def genDeclaraVar(self, nó):
        tipo = self.genTipo(nó.filho[0])
        idVariável = nó.folha[0]
        if self.escopo == 'global':
            self.símbolos['global.' + idVariável][2] = ir.GlobalVariable(self.modulo, tipo, idVariável)
        else:
            self.símbolos[self.escopo + '.' + idVariável][2] = self.construtor.alloca(tipo, name = idVariável)

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def genChamaFuncao(self, nó):
        nomeFunção = nó.folha[0]
        tipos = self.genParametros(nó.filho[0])
        função = self.modulo.get_global(nomeFunção)
        chamaFunção = self.construtor.call(função, tipos, 'call')
        return chamaFunção

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
        tipos = []
        if nó.nome == 'parametrosEmpty':
            return tipos
        while nó:
            tipos.append(self.genExprArit(nó.filho[0]))
            if len(nó.filho) > 1:
                nó = nó.filho[1]
            else:
                break
        return tipos

# def p_conjInstrucao(t):
#     ''' conjInstrucao : conjInstrucao instrucao
#                       | instrucao '''
#     if (len(t) == 3):
#         t[0] = AST('conjInstrucaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('conjInstrucao', [t[1]])
    def genConjInstrucao(self, nó):
        if nó.nome == 'conjInstrucaoComp':
            self.genConjInstrucao(nó.filho[0])
            self.genInstrucao(nó.filho[1])
        else:
            self.genInstrucao(nó.filho[0])

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
# def genCondicional(self, nó):


# def p_repeticao(t):
#     ' repeticao : REPITA NOVALINHA conjInstrucao ATE conjExpr NOVALINHA'
#     t[0] = AST('repeticao', [t[3], t[5]])
# def genRepeticao(self, nó):


# def p_atribuicao(t):
#     ''' atribuicao : ID RECEBE conjExpr NOVALINHA
#                    | ID RECEBE chamaFuncao NOVALINHA '''
#     t[0] = AST('atribuicao', [t[3]], [t[1]])
    def genAtribuicao(self, nó):
        if nó.filho[0].nome == 'conjExpr':
            resultado = self.genConjExpr(nó.filho[0])
            self.construtor.store(resultado, self.símbolos[self.escopo + '.' + nó.folha[0]][2])
        else:
            chamaFunção = self.genChamaFuncao(nó.filho[0])
            self.construtor.store(chamaFunção, self.símbolos[self.escopo + '.' + nó.folha[0]][2])

# def p_leitura(t):
#     ' leitura : LEIA ABREPARENTES ID FECHAPARENTES NOVALINHA '
#     t[0] = AST('leitura', [], [t[3]])
# def genLeitura(self, nó):


# def p_escreva(t):
#     ''' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES NOVALINHA
#                 | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES NOVALINHA '''
#     t[0] = AST('escreva', [t[3]])
# def genEscreva(self, nó):


# def p_retorna(t):
#     ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES NOVALINHA '
#     t[0] = AST('retorna', [t[3]])
    def genRetorna(self, nó):
        expressão = self.genExprArit(nó.filho[0])
        if expressão is self.símbolos.keys():
            pass
        else:
            return self.construtor.ret(expressão)

# def p_conjExpr(t):
#     ''' conjExpr : exprArit compara exprArit
#                  | exprArit '''
#     if (len(t ) == 4):
#         t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('conjExpr', [t[1]])
    def genConjExpr(self, nó):
        if len(nó.filho) == 1:
            return self.genExprArit(nó.filho[0])

# def p_compara(t):
#     ''' compara : MENOR
#                 | MAIOR
#                 | MENORIGUAL
#                 | MAIORIGUAL
#                 | IGUAL '''
#     t[0] = AST('compara', [], [t[1]])
# def genCompara(self, nó):


# def p_exprArit(t):
#     ''' exprArit : exprArit soma termo 
#                  | termo '''
#     if (len(t) == 4):
#         t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('exprArit', [t[1]])
    def genExprArit(self, nó):
        if len(nó.filho) == 1:
            return self.genTermo(nó.filho[0])

# def p_soma(t):
#     ''' soma : MAIS
#              | MENOS '''
#     t[0] = AST('maisMenos', [], [t[1]])
    # def genSoma(self, nó):


# def p_termo(t):
#     ''' termo : termo multi fator
#               | fator '''
#     if (len(t) == 4):
#         t[0] = AST('termoComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('termo', [t[1]])
    def genTermo(self, nó):
        if len(nó.filho) == 1:
            return self.genFator(nó.filho[0])

# def p_multi(t):
#     ''' multi : VEZES
#               | DIVIDIR '''
#     t[0] = AST('vezesDividir', [], [t[1]])
    # def genMulti(self, nó):


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
        if nó.nome == 'num':
            tipo = nó.filho[0].nome
            if tipo == 'n_inteiro':
                return ir.Constant(ir.IntType(32), nó.filho[0].folha[0])
            else:
                return ir.Constant(ir.FloatType(), nó.filho[0].folha[0])