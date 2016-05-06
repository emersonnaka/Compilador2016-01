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
        qtdeParam = self.conjParametros(node.children[0])
        tipo = self.getTipo(node.children[0])
        if node.leaf[0] is self.simbolos.keys():
            print("Erro semântico: função '" + node.leaf[0] + "'já foi declarado")
            exit(1)
        self.simbolos[node.leaf[0]] = ["função", tipo, qtdeParam]
        self.conjParametros(node.children[1])
        self.conjInstrucao(node.children[2])

# def p_conjParametros_(t):
#     ''' conjParametros : conjParametros VIRGULA tipo DOISPONTOS ID
#                        | tipo DOISPONTOS ID
#                        | empty '''
#     if (len(t) == 6):
#         t[0] = AST('conjParametrosComp', [t[1], t[3]], [t[5]])
#     elif (len(t) == 4):
#         t[0] = AST('conjParametros', [t[1]], [t[3]])
#     else:
#         t[0] = AST('conjParametrosEmpty', [])
    def conjParametros(self, node):
        variaveis = []
        if(len(node.children) > 0):
            tipo = self.getTipo(node.children[0])
            variaveis.append(tipo)
            key = str(self.escopo + '.' + nodel.leaf[0])
            self.simbolos[key] = ["variável", 0, tipo]
            if len(node.children) > 1:
                variaveis = variaveis + conjParametros(node.children[0])
        return variaveis

# def p_declaraVar(t):
#     ' declaraVar : tipo DOISPONTOS ID NOVALINHA '
#     t[0] = AST('declaraVar', [t[1]], [t[3]])
    def declaraVar(self, node):
        tipo = getTipo(node.children[0])
        key = self.escopo + "." + node.leaf[0]
        if key is self.simbolos.keys():
            print("Erro semântico: ID '" + node.leaf[0] + "' já foi declarado")
            exit(1)
        if node.leaf[0] is self.simbolos.keys():
            print("Erro semântico: ID '" + node.leaf[0] + "' foi declarado como função")
            exit(1)
        self.simbolos[key] = ["variável", 0, tipo]

    def getTipo(self, node):
        return node.leaf[0]

# def p_chamaFuncao(t):
#     ' chamaFuncao : ID ABREPARENTES parametros FECHAPARENTES '
#     t[0] = AST('chamaFuncao', [t[3]], [t[1]])
    def chamaFuncao(self, node):
        if node.leaf[0] not in self.simbolos.keys():
            print("Erro semântico: função '" + node.leaf[0] + "' não foi declarado")
            exit(1)
        qtdeParam = self.parametros(node.children[0])
        if len(self.simbolos[node.leaf[0]][2]) != qtdeParam:
            print("Erro semântico: esperado '" + str(len(self.simbolos[node.leaf[0]][1])) + "' parâmetro(s)")
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


    def condicional(self, node):

    def repeticao(self, node):

    def atribuicao(self, node):

    def leitura(self, node):

    def escreva(self, node):

    def retorna(self, node):