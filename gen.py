# http://llvmlite.readthedocs.io/en/latest/index.html
# http://llvm.org/docs/tutorial/
from llvmlite import ir, binding
from semantica import Semantica
from sintatica import *
from sys import exit
import os

class Gen:

    def __init__(self, code):
        semantica = Semantica(code.read())
        semantica.semanticaTopo()
        self.semantica = semantica.árvore
        # self.optimization = optz
        self.construtor = None
        self.func = None
        self.símbolos = semantica.símbolos
        self.phi = False
        self.esquerda = None
        self.direita = None
        # self.debug = debug
        self.escopo = 'global'
        self.modulo = ir.Module('programa')

        self.escrevaFlutuante = ir.Function(self.modulo, ir.FunctionType(ir.FloatType(), [ir.FloatType()]), 'escrevaFlutuante')
        self.escrevaInteiro = ir.Function(self.modulo, ir.FunctionType(ir.IntType(32), [ir.IntType(32)]), 'escrevaInteiro')
        self.leiaFlutuante = ir.Function(self.modulo, ir.FunctionType(ir.FloatType(), []), 'leiaFlutuante')
        self.leiaInteiro = ir.Function(self.modulo, ir.FunctionType(ir.IntType(32), []), 'leiaInteiro')

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
        self.func = ir.Function(self.modulo, função, name = 'main')
        bloco = self.func.append_basic_block('entry')
        self.construtor = ir.IRBuilder(bloco)
        self.genConjInstrucao(nó.filho[0])
        return self.construtor.ret_void()

# def p_funcao(t):
#     ' funcao : tipo ID ABREPARENTES conjParametros FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA '
#     t[0] = AST('funcao', [t[1], t[4], t[7]], [t[2]])
    def genFuncao(self, nó):
        self.escopo = nó.folha[0]
        tipo = self.genTipo(nó.filho[0])
        parametros = self.genConjParametros(nó.filho[1])
        função = ir.FunctionType(tipo, [parametros[i][0] for i in range(0, len(parametros))])
        self.func = ir.Function(self.modulo, função, name = nó.folha[0])
        bloco = self.func.append_basic_block('entry')
        self.construtor = ir.IRBuilder(bloco)

        for i, param in enumerate(parametros):
            self.func.args[i].name = param[1]
            self.símbolos[self.escopo + '.' + param[1]][2] = self.construtor.alloca(param[0], name = param[1])
            self.construtor.store(self.func.args[i], self.símbolos[self.escopo + '.' + param[1]][2])

        self.genConjInstrucao(nó.filho[2])
        if tipo == ir.VoidType():
            return self.construtor.ret_void()

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
        tipos = []
        if len(nó.filho) > 0:
            tipo = self.genTipo(nó.filho[0])
            tipos.append((tipo, nó.folha[0]))
            if len(nó.filho) > 1:
                tipos = tipos + self.genConjParametros(nó.filho[1])
        return tipos

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def genDeclaraVar(self, nó):
        tipo = self.genTipo(nó.filho[0])
        if self.escopo == 'global':
            self.símbolos['global.' + nó.folha[0]][2] = ir.GlobalVariable(self.modulo, tipo, nó.folha[0])
            return self.símbolos['global.' + nó.folha[0]][2]
        else:
            self.símbolos[self.escopo + '.' + nó.folha[0]][2] = self.construtor.alloca(tipo, name = nó.folha[0])
            return self.símbolos[self.escopo + '.' + nó.folha[0]][2]

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def genChamaFuncao(self, nó):
        nomeFunção = nó.folha[0]
        valores = self.genParametros(nó.filho[0])
        função = self.modulo.get_global(nomeFunção)
        tipos = self.símbolos[nó.folha[0]][2]

        i = 0
        while i < len(tipos):
            if tipos[i] == 'inteiro':
                valores[i] = self.construtor.fptosi(valores[i], ir.IntType(32))
            i = i + 1

        # self.construtor.call(self.escrevaFlutuante, [expr], name = 'call')
        chamaFunção = self.construtor.call(função, valores)
        if self.símbolos[nó.folha[0]][1] == 'inteiro':
            chamaFunção = self.construtor.sitofp(ir.Constant(ir.IntType(32), chamaFunção), ir.FloatType())
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
        valores = []
        if len(nó.filho) > 1:
            valores.append(self.genExprArit(nó.filho[1]))
            valores = valores + self.genParametros(nó.filho[0])
        elif len(nó.filho) == 1:
            valores.append(self.genExprArit(nó.filho[0]))
        return valores

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
            return self.genInstrucao(nó.filho[1])
        else:
            return self.genInstrucao(nó.filho[0])

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
            return self.genCondicional(nó.filho[0])
        elif nó.filho[0].nome == 'repeticao':
            return self.genRepeticao(nó.filho[0])
        elif nó.filho[0].nome == 'atribuicao':
            return self.genAtribuicao(nó.filho[0])
        elif nó.filho[0].nome == 'leitura':
            return self.genLeitura(nó.filho[0])
        elif nó.filho[0].nome == 'escreva':
            return self.genEscreva(nó.filho[0])
        elif nó.filho[0].nome == 'chamaFuncao':
            return self.genChamaFuncao(nó.filho[0])
        elif nó.filho[0].nome == 'declaraVar':
            return self.genDeclaraVar(nó.filho[0])
        elif nó.filho[0].nome == 'retorna':
            return self.genRetorna(nó.filho[0])

# def p_condicional(t):
#     ''' condicional : SE conjExpr ENTAO NOVALINHA conjInstrucao FIM NOVALINHA
#                     | SE conjExpr ENTAO NOVALINHA conjInstrucao SENAO NOVALINHA conjInstrucao FIM NOVALINHA '''
#     if (len(t) == 8):
#         t[0] = AST('condicionalSe', [t[2], t[5]])
#     else:
#         t[0] = AST('condicionalSenao', [t[2], t[5], t[8]])
    def genCondicional(self, nó):
        self.phi = True
        condição = self.genConjExpr(nó.filho[0])

        blocoEntão = self.func.append_basic_block('entao')
        if len(nó.filho) == 3:
            blocoSenão = self.func.append_basic_block('senao')
        blocoFim = self.func.append_basic_block('fim')

        if len(nó.filho) == 2:
            self.construtor.cbranch(condição, blocoEntão, blocoFim)
        else:
            self.construtor.cbranch(condição, blocoEntão, blocoSenão)

        self.construtor.position_at_end(blocoEntão)
        valorEntão = self.genConjInstrucao(nó.filho[1])
        self.phi = True
        self.construtor.branch(blocoFim)
        blocoEntão = self.construtor.basic_block

        if len(nó.filho) == 3:
            self.construtor.position_at_end(blocoSenão)
            valorSenão = self.genConjInstrucao(nó.filho[2])
            self.phi = True
            self.construtor.branch(blocoFim)
            blocoSenão = self.construtor.basic_block

        self.construtor.position_at_end(blocoFim)
        phi = self.construtor.phi(ir.FloatType(), 'seTmp')
        phi.add_incoming(valorEntão, blocoEntão)
        if len(nó.filho) == 3:
            phi.add_incoming(valorSenão, blocoSenão)
        self.phi = False
        return phi


# def p_repeticao(t):
#     ' repeticao : REPITA NOVALINHA conjInstrucao ATE conjExpr NOVALINHA'
#     t[0] = AST('repeticao', [t[3], t[5]])
    def genRepeticao(self, nó):
        self.phi = True
        blocoRepita = self.func.append_basic_block('repita')
        blocoFimRepita = self.func.append_basic_block('fimRepita')
        self.construtor.branch(blocoRepita)
        self.construtor.position_at_end(blocoRepita)
        valorRepita = self.genConjInstrucao(nó.filho[0])
        blocoRepita = self.construtor.basic_block

        condição = self.genConjExpr(nó.filho[1])
        self.construtor.cbranch(condição, blocoRepita, blocoFimRepita)
        self.construtor.position_at_end(blocoFimRepita)
        
        phi = self.construtor.phi(ir.FloatType(), 'repitaTmp')
        phi.add_incoming(valorRepita, blocoRepita)
        self.phi = False
        return phi


# def p_atribuicao(t):
#     ' atribuicao : ID RECEBE conjExpr NOVALINHA '
#     t[0] = AST('atribuicao', [t[3]], [t[1]])
    def genAtribuicao(self, nó):
        resultado = self.genConjExpr(nó.filho[0])

        if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
            if self.símbolos[self.escopo + '.' + nó.folha[0]][1] == 'inteiro':
                resultado = self.construtor.fptosi(resultado, ir.IntType(32))
            return self.construtor.store(resultado, self.símbolos[self.escopo + '.' + nó.folha[0]][2])
        else:
            if self.símbolos['global.' + nó.folha[0]][1] == 'inteiro':
                resultado = self.construtor.fptosi(resultado, ir.IntType(32))
            return self.construtor.store(resultado, self.símbolos['global.' + nó.folha[0]][2])
            

# def p_leitura(t):
#     ' leitura : LEIA ABREPARENTES ID FECHAPARENTES NOVALINHA '
#     t[0] = AST('leitura', [], [t[3]])
    def genLeitura(self, nó):
        if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
            if self.símbolos[self.escopo + '.' + nó.folha[0]][1] == 'inteiro':
                valor = self.construtor.call(self.leiaInteiro, [])
            else:
                valor = self.construtor.call(self.leiaFlutuante, [])
        else:
            if self.símbolos['global.' + nó.folha[0]][1] == 'inteiro':
                valor = self.construtor.call(self.leiaInteiro, [])
            else:
                valor = self.construtor.call(self.leiaFlutuante, [])
        return self.construtor.store(valor, self.símbolos[self.escopo + '.' + nó.folha[0]][2])

# def p_escreva(t):
#     ' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES NOVALINHA '
#     t[0] = AST('escreva', [t[3]])
    def genEscreva(self, nó):
        expr = self.genConjExpr(nó.filho[0])
        # expr = self.construtor.fptosi(expr, ir.IntType(32))
        # self.construtor.call(self.escrevaInteiro, [expr])
        return self.construtor.call(self.escrevaFlutuante, [expr])

# def p_retorna(t):
#     ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES NOVALINHA '
#     t[0] = AST('retorna', [t[3]])
    def genRetorna(self, nó):
        expressão = self.genExprArit(nó.filho[0])
        if self.phi:
            return expressão
        if self.símbolos[self.escopo][1] == 'inteiro':
            expressão = self.construtor.fptosi(expressão, ir.IntType(32))
        return self.construtor.ret(expressão)

# def p_conjExpr(t):
#     ''' conjExpr : exprArit compara exprArit
#                  | exprArit '''
#     if (len(t ) == 4):
#         t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('conjExpr', [t[1]])
    def genConjExpr(self, nó):
        if len(nó.filho) == 3:
            esquerda = self.genExprArit(nó.filho[0])
            operador = self.genCompara(nó.filho[1])
            direita = self.genExprArit(nó.filho[2])

            if operador == '<':
                return self.construtor.fcmp_unordered('<', esquerda, direita, name = 'fcmpMenor')
            elif operador == '>':
                return self.construtor.fcmp_unordered('>', esquerda, direita, name = 'fcmpMaior')
            elif operador == '<=':
                return self.construtor.fcmp_unordered('<=', esquerda, direita, name = 'fcmpMenorIgual')
            elif operador == '>=':
                return self.construtor.fcmp_unordered('>=', esquerda, direita, name = 'fcmpMaiorIgual')
            else:
                return self.construtor.fcmp_unordered('==', esquerda, direita, name = 'fcmpIgual')

        else:
            return self.genExprArit(nó.filho[0])

# def p_compara(t):
#     ''' compara : MENOR
#                 | MAIOR
#                 | MENORIGUAL
#                 | MAIORIGUAL
#                 | IGUAL '''
#     t[0] = AST('compara', [], [t[1]])
    def genCompara(self, nó):
        return nó.folha[0]
# def p_exprArit(t):
#     ''' exprArit : exprArit soma termo 
#                  | termo '''
#     if (len(t) == 4):
#         t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('exprArit', [t[1]])
    def genExprArit(self, nó):
        if len(nó.filho) == 3:
            esquerda = self.genExprArit(nó.filho[0])
            operador = self.genSoma(nó.filho[1])
            direita = self.genTermo(nó.filho[2])

            if operador == '+':
                return self.construtor.fadd(esquerda, direita, name = 'add')
            return self.construtor.fsub(direita, esquerda, name = 'sub')

        else:
            return self.genTermo(nó.filho[0])

# def p_soma(t):
#     ''' soma : MAIS
#              | MENOS '''
#     t[0] = AST('maisMenos', [], [t[1]])
    def genSoma(self, nó):
        return nó.folha[0]

# def p_termo(t):
#     ''' termo : termo multi fator
#               | fator '''
#     if (len(t) == 4):
#         t[0] = AST('termoComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('termo', [t[1]])
    def genTermo(self, nó):
        if len(nó.filho) == 3:
            esquerda = self.genTermo(nó.filho[0])
            operador = self.genMulti(nó.filho[1])
            direita = self.genFator(nó.filho[2])

            if operador == '*':
                return self.construtor.fmul(esquerda, direita, name = 'mul')
            return self.construtor.fdiv(direita, esquerda, name = 'div')

        else:
            return self.genFator(nó.filho[0])

# def p_multi(t):
#     ''' multi : VEZES
#               | DIVIDIR '''
#     t[0] = AST('vezesDividir', [], [t[1]])
    def genMulti(self, nó):
        return nó.folha[0]

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
        if nó.nome == 'fatorExprArit':
            return self.genExprArit(nó.filho[0])
        elif nó.nome == 'num':
            return ir.Constant(ir.FloatType(), float(nó.filho[0].folha[0]))
        elif nó.nome == 'fatorID':
            if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
                valor = self.construtor.load(self.símbolos[self.escopo + '.' + nó.folha[0]][2])
                if self.símbolos[self.escopo + '.' + nó.folha[0]][1] == 'inteiro':
                    valor = self.construtor.sitofp(valor, ir.FloatType())
            elif 'global.' + nó.folha[0] in self.símbolos.keys():
                valor = self.construtor.load(self.símbolos['global.' + nó.folha[0]][2])
                if self.símbolos['global.' + nó.folha[0]][1] == 'inteiro':
                    valor = self.construtor.sitofp(valor, ir.FloatType())
            return valor
        else:
            valor = self.genChamaFuncao(nó.filho[0])
            if self.símbolos[nó.filho[0].folha[0]][1] == 'inteiro':
                valor = self.construtor.sitofp(valor, ir.FloatType())
            return valor