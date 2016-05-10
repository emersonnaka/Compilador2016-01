from sintatica import *
import collections

class Semantica():

    def __init__ (self, codigo):
        self.arvore = parse_tree(codigo)
        self.simbolos = collections.OrderedDict()
        self.escopo = "global"

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
        if self.arvore.name == 'declaraVarGlobalPrograma':
            self.declaraVarGlobal(self.arvore.children[0])
            self.declaraFuncao(self.arvore.children[1])
            self.escopo = "principal"
            self.funcaoPrincipal(self.arvore.children[2])
        elif self.arvore.name == 'declaraFuncaoPrograma':
            self.declaraFuncao(self.arvore.children[0])
            self.escopo = "principal"
            self.funcaoPrincipal(self.arvore.children[1])
        else:
            self.funcaoPrincipal(self.arvore.children[0])

# def p_declaraVarGlobal(t):
#     ''' declaraVarGlobal : declaraVarGlobal declaraVar
#                          | declaraVar '''
#     if(len(t) == 3):
#         t[0] = AST('declaraVarGlobalComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraVarGlobal', [t[1]])
    def declaraVarGlobal(self, node):
        if len(node.children) == 2:
            self.declaraVarGlobal(node.children[0])
            self.declaraVar(node.children[1])
        else:
            self.declaraVar(node.children[0])

# def p_declaraFuncao(t):
#     '''declaraFuncao : declaraFuncao funcao
#                      | funcao '''
#     if(len(t) == 3):
#         t[0] = AST('declaraFuncaoComp', [t[1], t[2]])
#     else:
#         t[0] = AST('declaraFuncao', [t[1]])
    def declaraFuncao(self, node):
        if len(node.children) == 2:
            self.declaraFuncao(node.children[0])
            self.funcao(node.children[1])
        else:
            self.funcao(node.children[0])

# def p_funcaoPrincipal(t):
#     ' funcaoPrincipal : VAZIO PRINCIPAL ABREPARENTES FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA'
#     t[0] = AST('funcaoPrincipal', [t[6]], [t[1], t[2]])
    def funcaoPrincipal(self, node):
        self.conjInstrucao(node.children[0])

# def p_funcao(t):
#     ' funcao : tipo ID ABREPARENTES conjParametros FECHAPARENTES NOVALINHA conjInstrucao FIM NOVALINHA '
#     t[0] = AST('funcao', [t[1], t[4], t[7]], [t[2]])
# Inicialmente, a chave do dicionário seria o tipo da função '.' id, entretanto, se o usuário declarasse
# um ID com o tipo diferente, não daria erro. Sendo que o correto é acusar o erro
    def funcao(self, node):
        self.escopo = node.leaf[0]
        qtdeParam = self.conjParametros(node.children[1])
        tipo = self.getTipo(node.children[0])
        if node.leaf[0] is self.simbolos.keys():
            print("Erro semântico: função '" + node.leaf[0] + "'já foi declarado")
            exit(1)
        self.simbolos[node.leaf[0]] = ["função", tipo, qtdeParam]
        self.conjParametros(node.children[1])
        self.conjInstrucao(node.children[2])

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
    def getTipo(self, node):
        return node.leaf[0]

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
    def conjParametros(self, node):
        variaveis = []
        if len(node.children) > 0:
            tipo = self.getTipo(node.children[0])
            variaveis.append(tipo)
            self.simbolos[str(self.escopo + '.' + node.leaf[0])] = ['variável', tipo]
            if len(node.children) > 1:
                variaveis = variaveis + self.conjParametros(node.children[1])
        return variaveis

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def declaraVar(self, node):
        tipo = self.getTipo(node.children[0])
        if self.escopo + "." + node.leaf[0] is self.simbolos.keys():
            print("Erro semântico: ID '" + node.leaf[0] + "' já foi declarado")
            exit(1)
        if node.leaf[0] is self.simbolos.keys():
            print("Erro semântico: ID '" + node.leaf[0] + "' foi declarado como função")
            exit(1)
        self.simbolos[self.escopo + "." + node.leaf[0]] = ["variável", tipo]

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def chamaFuncao(self, node):
        if node.leaf[0] not in self.simbolos.keys():
            print("Erro semântico: função '" + node.leaf[0] + "' não declarada")
            exit(1)
        qtdeParam = self.parametros(node.children[0])
        if len(self.simbolos[node.leaf[0]][2]) != qtdeParam:
            print("Erro semântico: esperado '" + str(len(self.simbolos[node.leaf[0]][1])) + "' parâmetro(s) na função " + node.leaf[0])
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
    def parametros(self, node):
        if len(node.children) > 1:
            return self.parametros(node.children[0]) + 1 
        elif len(node.children) == 1:
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
    def conjInstrucao(self, node):
        if len(node.children) > 1:
            self.conjInstrucao(node.children[0])
            self.instrucao(node.children[1])
        else:
            self.instrucao(node.children[0])

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
    def instrucao(self, node):
        if (node.children[0].name == 'condicionalSe'):
            self.condicional(node.children[0])
        if (node.children[0].name == 'condicionalSenao'):
            self.condicional(node.children[0])
        if node.children[0].name == 'repeticao':
            self.repeticao(node.children[0])
        if node.children[0].name == 'atribuicao':
            self.atribuicao(node.children[0])
        if node.children[0].name == 'leitura':
            self.leitura(node.children[0])
        if node.children[0].name == 'escreva':
            self.escreva(node.children[0])
        if node.children[0].name == 'retorna':
            self.retorna(node.children[0])
        if node.children[0].name == 'declaraVar':
            self.declaraVar(node.children[0])
        if node.children[0].name == 'chamaFuncao':
            self.chamaFuncao(node.children[0])

# def p_condicional(t):
#     ''' condicional : SE conjExpr ENTAO NOVALINHA conjInstrucao FIM NOVALINHA
#                     | SE conjExpr ENTAO NOVALINHA conjInstrucao SENAO NOVALINHA conjInstrucao FIM NOVALINHA '''
#     if (len(t) == 8):
#         t[0] = AST('condicionalSe', [t[2], t[5]])
#     else:
#         t[0] = AST('condicionalSenao', [t[2], t[5], t[8]])
    def condicional(self, node):
        self.conjExpr(node.children[0])
        self.conjInstrucao(node.children[1])
        if len(node.children) == 3:
            self.conjInstrucao(node.children[2])

# def p_repeticao(t):
#     ' repeticao : REPITA NOVALINHA conjInstrucao ATE conjExpr NOVALINHA'
#     t[0] = AST('repeticao', [t[3], t[5]])
    def repeticao(self, node):
        self.conjInstrucao(node.children[0])
        self.conjExpr(node.children[1])

# def p_atribuicao(t):
#     ''' atribuicao : ID RECEBE conjExpr NOVALINHA
#                    | ID RECEBE chamaFuncao NOVALINHA '''
#     t[0] = AST('atribuicao', [t[3]], [t[1]])
    def atribuicao(self, node):
        if (self.escopo + "." + node.leaf[0] not in self.simbolos.keys()) and ('global.' + node.leaf[0] not in self.simbolos.keys()):
            print("Erro semântico: ID '" + node.leaf[0] + "' não declarado")
            exit(1)
        if node.children[0].name == 'chamaFuncao':
            if self.simbolos[self.escopo + '.' + node.leaf[0]][1] != self.simbolos[node.children[0].leaf[0]][1]:
                print("WARNING: ID '" + node.leaf[0] + "' é do tipo '" + self.simbolos[self.escopo + '.' + node.leaf[0]][1] +
                 "' e está recebendo a função '" + node.children[0].leaf[0] + "' do tipo " + self.simbolos[node.children[0].leaf[0]][1])
            self.chamaFuncao(node.children[0])
        else:
            self.conjExpr(node.children[0])

# def p_leitura(t):
#     ' leitura : LEIA ABREPARENTES ID FECHAPARENTES NOVALINHA '
#     t[0] = AST('leitura', [], [t[3]])
    def leitura(self, node):
        if (self.escopo + "." + node.leaf[0] not in self.simbolos.keys()) and ('global.' + node.leaf[0] not in self.simbolos.keys()):   
            print("Erro semântico: ID '" + node.leaf[0] + "' não declarado")
            exit(1)

# def p_escreva(t):
#     ''' escreva : ESCREVA ABREPARENTES conjExpr FECHAPARENTES NOVALINHA
#                 | ESCREVA ABREPARENTES chamaFuncao FECHAPARENTES NOVALINHA '''
#     t[0] = AST('escreva', [t[3]])
    def escreva(self, node):
        if node.children[0].name == 'chamaFuncao':
            self.chamaFuncao(node.children[0])
        else:
            self.conjExpr(node.children[0])

# def p_retorna(t):
#     ' retorna : RETORNA ABREPARENTES exprArit FECHAPARENTES NOVALINHA '
#     t[0] = AST('retorna', [t[3]])
    def retorna(self, node):
        self.exprArit(node.children[0])

# def p_conjExpr(t):
#     ''' conjExpr : exprArit compara exprArit
#                  | exprArit '''
#     if (len(t ) == 4):
#         t[0] = AST('conjExprComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('conjExpr', [t[1]])
    def conjExpr(self, node):
        if len(node.children) == 3:
            self.exprArit(node.children[0])
            operador = self.compara(node.children[1])
            self.exprArit(node.children[2])
        else:
            self.exprArit(node.children[0])

# def p_compara(t):
#     ''' compara : MENOR
#                 | MAIOR
#                 | MENORIGUAL
#                 | MAIORIGUAL
#                 | IGUAL '''
#     t[0] = AST('compara', [], [t[1]])
    def compara(self, node):
        return node.leaf[0]

# def p_exprArit(t):
#     ''' exprArit : exprArit soma termo 
#                  | termo '''
#     if (len(t) == 4):
#         t[0] = AST('exprAritComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('exprArit', [t[1]])
    def exprArit(self, node):
        if len(node.children) == 3:
            self.exprArit(node.children[0])
            operador = self.soma(node.children[1])
            self.termo(node.children[2])
        else:
            self.termo(node.children[0])

# def p_soma(t):
#     ''' soma : MAIS
#              | MENOS '''
#     t[0] = AST('maisMenos', [], [t[1]])
    def soma(self, node):
        return node.leaf[0]

# def p_termo(t):
#     ''' termo : termo multi fator
#               | fator '''
#     if (len(t) == 4):
#         t[0] = AST('termoComp', [t[1], t[2], t[3]])
#     else:
#         t[0] = AST('termo', [t[1]])
    def termo(self, node):
        if len(node.children) == 3:
            self.termo(node.children[0])
            operador = self.multi(node.children[1])
            self.fator(node.children[2])
        else:
            self.fator(node.children[0])

# def p_multi(t):
#     ''' multi : VEZES
#               | DIVIDIR '''
#     t[0] = AST('vezesDividir', [], [t[1]])
    def multi(self, node):
        return node.leaf[0]

# def p_fator_1(t):
#     ' fator : ABREPARENTES exprArit FECHAPARENTES '
#     t[0] = AST('fatorExprArti', [t[1]])
# def p_fator_2(t):
#     ' fator : num '
#     t[0] = AST('num', [t[1]])
# def p_fator_3(t):
#     ' fator : ID '
#     t[0] = AST('fatorID', [], [t[1]])
    def fator(self, node):
        if node.name == 'fatorID':
            if self.escopo + '.' + node.leaf[0] not in self.simbolos.keys():
                print("Erro semântico: ID '" + node.leaf[0] + "' não declarado")
                exit(1)
        elif node.name =='fatorExprArit':
            self.exprArit(node.children[0])

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    s = Semantica(code.read())
    s.semanticaTopo()
    print("Tabela de Simbolos:", s.simbolos)