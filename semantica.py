from sintatica import *

class Semantica():

    def __init__ (self, codigo):
        self.árvore = parse_tree(codigo)
        self.símbolos = {}
        self.escopo = 'global'

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
    def semanticaTopo(self):
        if self.árvore.nome == 'declaraVarGlobalPrograma':
            self.declaraVarGlobal(self.árvore.filho[0])
            self.declaraFuncao(self.árvore.filho[1])
            self.funcaoPrincipal(self.árvore.filho[2])
        elif self.árvore.nome == 'declaraFuncaoPrograma':
            self.declaraFuncao(self.árvore.filho[0])
            self.funcaoPrincipal(self.árvore.filho[1])
        else:
            self.funcaoPrincipal(self.árvore.filho[0])

# def p_declaraVarGlobal(t):
#     ''' declaraVarGlobal : declaraVarGlobal declaraVar
#                          | declaraVar '''
#     if(len(t) == 3):
#         t[0] = AST('declaraVarGlobalComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraVarGlobal', [t[1]])
    def declaraVarGlobal(self, nó):
        if len(nó.filho) == 2:
            self.declaraVarGlobal(nó.filho[0])
            self.declaraVar(nó.filho[1])
        else:
            self.declaraVar(nó.filho[0])

# def p_declaraFuncao(t):
#     '''declaraFuncao : declaraFuncao funcao
#                      | funcao '''
#     if(len(t) == 3):
#         t[0] = AST('declaraFuncaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraFuncao', [t[1]])
    def declaraFuncao(self, nó):
        if len(nó.filho) == 2:
            self.declaraFuncao(nó.filho[0])
            self.funcao(nó.filho[1])
        else:
            self.funcao(nó.filho[0])

# def p_funcaoPrincipal(t):
#     ' funcaoPrincipal : VAZIO PRINCIPAL ABREPARENTES FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA'
#     t[0] = AST('funcaoPrincipal', [t[6]], [t[1], t[2]])
    def funcaoPrincipal(self, nó):
        self.escopo = 'principal'
        tipo = nó.folha[1]
        self.símbolos[nó.folha[1]] = ['funçãoPrincipal', tipo]
        self.conjInstrucao(nó.filho[0])

# def p_funcao(t):
#     ' funcao : tipo ID ABREPARENTES conjParametros FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA '
#     t[0] = AST('funcao', [t[1], t[4], t[7]], [t[2]])
# Inicialmente, a chave do dicionário seria o tipo da função '.' id, entretanto, se o usuário declarasse
# um ID com o tipo diferente, não daria erro. Sendo que o correto é acusar o erro
    def funcao(self, nó):
        self.escopo = nó.folha[0]
        qtdeParam = self.conjParametros(nó.filho[1])
        tipo = self.getTipo(nó.filho[0])
        if nó.folha[0] is self.símbolos.keys():
            print("Erro semântico: função '" + nó.folha[0] + "'já foi declarado")
            exit(1)
        self.símbolos[nó.folha[0]] = ["função", tipo, qtdeParam]
        self.conjParametros(nó.filho[1])
        self.conjInstrucao(nó.filho[2])

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
    def getTipo(self, nó):
        return nó.folha[0]

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
    def conjParametros(self, nó):
        variaveis = []
        if len(nó.filho) > 0:
            tipo = self.getTipo(nó.filho[0])
            variaveis.append(tipo)
            self.símbolos[str(self.escopo + '.' + nó.folha[0])] = ['variável', tipo, True]
            if len(nó.filho) > 1:
                variaveis = variaveis + self.conjParametros(nó.filho[1])
        return variaveis

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def declaraVar(self, nó):
        tipo = self.getTipo(nó.filho[0])
        if self.escopo + '.' + nó.folha[0] is self.símbolos.keys():
            print("Erro semântico: ID '" + nó.folha[0] + "' já foi declarado")
            exit(1)
        if nó.folha[0] is self.símbolos.keys():
            print("Erro semântico: ID '" + nó.folha[0] + "' foi declarado como função")
            exit(1)
        self.símbolos[self.escopo + '.' + nó.folha[0]] = ['variável', tipo, valor, False]

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def chamaFuncao(self, nó):
        if nó.folha[0] not in self.símbolos.keys():
            print("Erro semântico: função '" + nó.folha[0] + "' não declarada")
            exit(1)
        qtdeParam = self.parametros(nó.filho[0])
        if len(self.símbolos[nó.folha[0]][2]) != qtdeParam:
            print("Erro semântico: esperado '" + str(len(self.símbolos[nó.folha[0]][1])) + "' parâmetro(s) na função " + nó.folha[0])
            exit(1)

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
    def parametros(self, nó):
        if len(nó.filho) > 1:
            self.exprArit(nó.filho[1])
            return self.parametros(nó.filho[0]) + 1 
        elif len(nó.filho) == 1:
            self.exprArit(nó.filho[0])
            return 1
        else:
            return 0

# def p_conjInstrucao(t):
#     ''' conjInstrucao : conjInstrucao instrucao
#                       | instrucao '''
#     if (len(t) == 3):
#         t[0] = AST('conjInstrucaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('conjInstrucao', [t[1]])
    def conjInstrucao(self, nó):
        if len(nó.filho) > 1:
            self.conjInstrucao(nó.filho[0])
            self.instrucao(nó.filho[1])
        else:
            self.instrucao(nó.filho[0])

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
    def instrucao(self, nó):
        if nó.filho[0].nome == 'condicionalSe':
            self.condicional(nó.filho[0])
        if nó.filho[0].nome == 'condicionalSenao':
            self.condicional(nó.filho[0])
        if nó.filho[0].nome == 'repeticao':
            self.repeticao(nó.filho[0])
        if nó.filho[0].nome == 'atribuicao':
            self.atribuicao(nó.filho[0])
        if nó.filho[0].nome == 'leitura':
            self.leitura(nó.filho[0])
        if nó.filho[0].nome == 'escreva':
            self.escreva(nó.filho[0])
        if nó.filho[0].nome == 'retorna':
            self.retorna(nó.filho[0])
        if nó.filho[0].nome == 'declaraVar':
            self.declaraVar(nó.filho[0])
        if nó.filho[0].nome == 'chamaFuncao':
            self.chamaFuncao(nó.filho[0])

# def p_condicional(t):
#     ''' condicional : SE conjExpr ENTAO NOVALINHA conjInstrucao FIM NOVALINHA
#                     | SE conjExpr ENTAO NOVALINHA conjInstrucao SENAO NOVALINHA conjInstrucao FIM NOVALINHA '''
#     if (len(t) == 8):
#         t[0] = AST('condicionalSe', [t[2], t[5]])
#     else:
#         t[0] = AST('condicionalSenao', [t[2], t[5], t[8]])
    def condicional(self, nó):
        self.conjExpr(nó.filho[0])
        self.conjInstrucao(nó.filho[1])
        if len(nó.filho) == 3:
            self.conjInstrucao(nó.filho[2])

# def p_repeticao(t):
#     ' repeticao : REPITA NOVALINHA conjInstrucao ATE conjExpr NOVALINHA'
#     t[0] = AST('repeticao', [t[3], t[5]])
    def repeticao(self, nó):
        self.conjInstrucao(nó.filho[0])
        self.conjExpr(nó.filho[1])

# def p_atribuicao(t):
#     ''' atribuicao : ID RECEBE conjExpr NOVALINHA
#                    | ID RECEBE chamaFuncao NOVALINHA '''
#     t[0] = AST('atribuicao', [t[3]], [t[1]])
    def atribuicao(self, nó):
        if (self.escopo + '.' + nó.folha[0] not in self.símbolos.keys()) and ('global.' + nó.folha[0] not in self.símbolos.keys()):
            print("Erro semântico: ID '" + nó.folha[0] + "' não declarado")
            exit(1)
        if nó.filho[0].nome == 'chamaFuncao':
            if self.símbolos[nó.filho[0].folha[0]][1] == 'vazio':
                print("Erro semântico: função '" + nó.filho[0].folha[0] + "' é do tipo 'vazio', então não possui retorno")
                exit(1)
            if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
                if self.símbolos[self.escopo + '.' + nó.folha[0]][1] != self.símbolos[nó.filho[0].folha[0]][1]:
                    print("WARNING atribuição: ID '" + nó.folha[0] + "' é do tipo '" +
                        self.símbolos[self.escopo + '.' + nó.folha[0]][1] + "' e está recebendo a função '" +
                        nó.filho[0].folha[0] + "' do tipo '" + self.símbolos[nó.filho[0].folha[0]][1] + "'")
            elif 'global.' + nó.folha[0] in self.símbolos.keys():
                if self.símbolos['global.' + nó.folha[0]][1] != self.símbolos[nó.filho[0].folha[0]][1]:
                    print("WARNING atribuição: ID '" + nó.folha[0] + "' é do tipo '" +
                        self.símbolos['global.' + nó.folha[0]][1] + "' e está recebendo a função '" +
                        nó.filho[0].folha[0] + "' do tipo '" + self.símbolos[nó.filho[0].folha[0]][1] + "'")
            self.chamaFuncao(nó.filho[0])
        else:
            tipo = self.conjExpr(nó.filho[0])
            if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
                if self.símbolos[self.escopo + '.' + nó.folha[0]][1] != tipo:
                    print("WARNING atribuição: ID '" + nó.folha[0] + "' é do tipo '" +
                        self.símbolos[self.escopo + '.' + nó.folha[0]][1] +
                        "' está atribuindo uma expressão do tipo '" + tipo + "'")
            elif 'global.' + nó.folha[0] in self.símbolos.keys():
                if self.símbolos['global.' + nó.folha[0]][1] != tipo:
                    print("WARNING atribuição: ID '" + nó.folha[0] + "' é do tipo '" +
                        self.símbolos['global.' + nó.folha[0]][1] +
                        "' está atribuindo uma expressão do tipo '" + tipo + "'")
        if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
            if not(self.símbolos[self.escopo + '.' + nó.folha[0]][2]):
                self.símbolos[self.escopo + '.' + nó.folha[0]][3] = True
        elif 'global.' + nó.folha[0] in self.símbolos.keys():
            if not(self.símbolos['global.' + nó.folha[0]][2]):
                self.símbolos['global.' + nó.folha[0]][3] = True

# def p_leitura(t):
#     ' leitura : LEIA ABREPARENTES ID FECHAPARENTES NOVALINHA '
#     t[0] = AST('leitura', [], [t[3]])
    def leitura(self, nó):
        if (self.escopo + '.' + nó.folha[0] not in self.símbolos.keys()) and ('global.' + nó.folha[0] not in self.símbolos.keys()):   
            print("Erro semântico: ID '" + nó.folha[0] + "' não declarado")
            exit(1)

# def p_escreva(t):
#     ''' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES NOVALINHA
#                 | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES NOVALINHA '''
#     t[0] = AST('escreva', [t[3]])
    def escreva(self, nó):
        if nó.filho[0].nome == 'chamaFuncao':
            self.chamaFuncao(nó.filho[0])
        else:
            self.conjExpr(nó.filho[0])

# def p_retorna(t):
#     ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES NOVALINHA '
#     t[0] = AST('retorna', [t[3]])
    def retorna(self, nó):
        self.exprArit(nó.filho[0])

# def p_conjExpr(t):
#     ''' conjExpr : exprArit compara exprArit
#                  | exprArit '''
#     if (len(t ) == 4):
#         t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('conjExpr', [t[1]])
    def conjExpr(self, nó):
        if len(nó.filho) == 3:
            self.exprArit(nó.filho[0])
            operador = self.compara(nó.filho[1])
            self.exprArit(nó.filho[2])
        else:
            return self.exprArit(nó.filho[0])

# def p_compara(t):
#     ''' compara : MENOR
#                 | MAIOR
#                 | MENORIGUAL
#                 | MAIORIGUAL
#                 | IGUAL '''
#     t[0] = AST('compara', [], [t[1]])
    def compara(self, nó):
        return nó.folha[0]

# def p_exprArit(t):
#     ''' exprArit : exprArit soma termo 
#                  | termo '''
#     if (len(t) == 4):
#         t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('exprArit', [t[1]])
    def exprArit(self, nó):
        if len(nó.filho) == 3:
            self.exprArit(nó.filho[0])
            operador = self.soma(nó.filho[1])
            return self.termo(nó.filho[2])
        else:
            return self.termo(nó.filho[0])

# def p_soma(t):
#     ''' soma : MAIS
#              | MENOS '''
#     t[0] = AST('maisMenos', [], [t[1]])
    def soma(self, nó):
        return nó.folha[0]

# def p_termo(t):
#     ''' termo : termo multi fator
#               | fator '''
#     if (len(t) == 4):
#         t[0] = AST('termoComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('termo', [t[1]])
    def termo(self, nó):
        if len(nó.filho) == 3:
            self.termo(nó.filho[0])
            operador = self.multi(nó.filho[1])
            return self.fator(nó.filho[2])
        else:
            return self.fator(nó.filho[0])

# def p_multi(t):
#     ''' multi : VEZES
#               | DIVIDIR '''
#     t[0] = AST('vezesDividir', [], [t[1]])
    def multi(self, nó):
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
    def fator(self, nó):
        if nó.nome == 'fatorExprArit':
            self.exprArit(nó.filho[0])
        if nó.nome == 'num':
            return self.num(nó.filho[0])
        elif nó.nome == 'fatorID':
            if (self.escopo + '.' + nó.folha[0] not in self.símbolos.keys()) and ('global.' + nó.folha[0] not in self.símbolos.keys()):
                print("Erro semântico: ID '" + nó.folha[0] + "' não declarado")
                exit(1)
            if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
                if not(self.símbolos[self.escopo + '.' + nó.folha[0]][3]):
                    print("Erro semântico: ID '" + nó.folha[0] + "' não foi inicializado")
                    exit(1)
                return self.símbolos[self.escopo + '.' + nó.folha[0]][1]
            elif 'global.' + nó.folha[0] in self.símbolos.keys():
                if not(self.símbolos['global.' + nó.folha[0]][3]):
                    print("Erro semântico: ID '" + nó.folha[0] + "' não foi inicializado")
                    exit(1)
                return self.símbolos['global.' + nó.folha[0]][1]

    def num(self, nó):
        if nó.nome == 'n_inteiro':
            return 'inteiro'
        else:
            return 'flutuante'

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    s = Semantica(code.read())
    s.semanticaTopo()
    print("Tabela de símbolos:", s.símbolos)