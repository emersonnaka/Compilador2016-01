from sintatica import *

class Semantica():

    def __init__ (self, codigo):
        self.árvore = parse_tree(codigo)
        self.símbolos = {}
        self.escopo = 'global'

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

    def declaraVarGlobal(self, nó):
        if len(nó.filho) == 2:
            self.declaraVarGlobal(nó.filho[0])
            self.declaraVar(nó.filho[1])
        else:
            self.declaraVar(nó.filho[0])

    def declaraFuncao(self, nó):
        if len(nó.filho) == 2:
            self.declaraFuncao(nó.filho[0])
            self.funcao(nó.filho[1])
        else:
            self.funcao(nó.filho[0])

    def funcaoPrincipal(self, nó):
        self.escopo = 'principal'
        tipo = nó.folha[1]
        self.símbolos[nó.folha[1]] = ['funçãoPrincipal', tipo]
        self.conjInstrucao(nó.filho[0])

    def funcao(self, nó):
        self.escopo = nó.folha[0]
        qtdeParam = self.conjParametros(nó.filho[1])
        tipo = self.getTipo(nó.filho[0])
        if nó.folha[0] is self.símbolos.keys():
            print("Erro semântico: função '" + nó.folha[0] + "'já foi declarado")
            exit(1)
        self.símbolos[nó.folha[0]] = ["função", tipo, qtdeParam]
        self.conjInstrucao(nó.filho[2])

    def getTipo(self, nó):
        return nó.folha[0]

    def conjParametros(self, nó):
        variaveis = []
        if len(nó.filho) > 0:
            tipo = self.getTipo(nó.filho[0])
            variaveis.append(tipo)
            self.símbolos[str(self.escopo + '.' + nó.folha[0])] = ['variável', tipo, 0, True]
            if len(nó.filho) > 1:
                variaveis = variaveis + self.conjParametros(nó.filho[1])
        return variaveis

    def declaraVar(self, nó):
        tipo = self.getTipo(nó.filho[0])
        if tipo == 'vazio':
            print("Erro semântico: ID '" + nó.folha[0] + "' não pode ser do tipo 'vazio'")
            exit(1)
        if self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
            print("Erro semântico: ID '" + nó.folha[0] + "' já foi declarado")
            exit(1)
        if nó.folha[0] is self.símbolos.keys():
            print("Erro semântico: ID '" + nó.folha[0] + "' foi declarado como função")
            exit(1)
        self.símbolos[self.escopo + '.' + nó.folha[0]] = ['variável', tipo, 0, False]

    def chamaFuncao(self, nó):
        if nó.folha[0] not in self.símbolos.keys():
            print("Erro semântico: função '" + nó.folha[0] + "' não declarada")
            exit(1)
        qtdeParam = self.parametros(nó.filho[0])
        if len(self.símbolos[nó.folha[0]][2]) != len(qtdeParam):
            print("Erro semântico: esperado '" + str(len(self.símbolos[nó.folha[0]][2])) +
                "' parâmetro(s) na função '" + nó.folha[0] + "'")
            exit(1)
        if self.símbolos[nó.folha[0]][2] != qtdeParam:
            print("WARNING chamada de função: espera parâmetros dos tipos " + str(self.símbolos[nó.folha[0]][2]) +
                " e está sendo passado " + str(qtdeParam) + " na função '"  + nó.folha[0] + "'")
        return self.símbolos[nó.folha[0]][1]


    def parametros(self, nó):
        tipos = []
        if len(nó.filho) > 1:
            tipos.append(self.exprArit(nó.filho[1]))
            tipos = tipos + self.parametros(nó.filho[0])
        elif len(nó.filho) == 1:
            tipos.append(self.exprArit(nó.filho[0]))
        return tipos

    def conjInstrucao(self, nó):
        if len(nó.filho) > 1:
            self.conjInstrucao(nó.filho[0])
            self.instrucao(nó.filho[1])
        else:
            self.instrucao(nó.filho[0])

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

    def condicional(self, nó):
        self.conjExpr(nó.filho[0])
        self.conjInstrucao(nó.filho[1])
        if len(nó.filho) == 3:
            self.conjInstrucao(nó.filho[2])

    def repeticao(self, nó):
        self.conjInstrucao(nó.filho[0])
        self.conjExpr(nó.filho[1])

    def atribuicao(self, nó):
        if (self.escopo + '.' + nó.folha[0] not in self.símbolos.keys()) and ('global.' + nó.folha[0] not in self.símbolos.keys()):
            print("Erro semântico: ID '" + nó.folha[0] + "' não declarado")
            exit(1)
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

    def leitura(self, nó):
        if (self.escopo + '.' + nó.folha[0] not in self.símbolos.keys()) and ('global.' + nó.folha[0] not in self.símbolos.keys()):   
            print("Erro semântico: ID '" + nó.folha[0] + "' não declarado")
            exit(1)
        elif self.escopo + '.' + nó.folha[0] in self.símbolos.keys():
            self.símbolos[self.escopo + '.' + nó.folha[0]][3] = True
        else:
            self.símbolos['global.' + nó.folha[0]][3] = True

    def escreva(self, nó):
        self.conjExpr(nó.filho[0])

    def retorna(self, nó):
        if self.símbolos[self.escopo][1] == 'vazio':
            print("WARNING: função '" + self.escopo + "' é do tipo '" + self.símbolos[self.escopo][1] +
                "', então não pode ter chamada de retorno ")
            exit(1)
        tipo = self.exprArit(nó.filho[0])
        if self.símbolos[self.escopo][1] != tipo:
            print("WARNING: função '" + self.escopo + "' é do tipo '" + self.símbolos[self.escopo][1] +
                "' e está retornando uma expressão do tipo '" + tipo + "'")

    def conjExpr(self, nó):
        if len(nó.filho) == 3:
            esquerda = self.exprArit(nó.filho[0])
            operador = self.compara(nó.filho[1])
            direita = self.exprArit(nó.filho[2])

            if(esquerda == direita):
                return esquerda
            return 'flutuante'

        else:
            return self.exprArit(nó.filho[0])

    def compara(self, nó):
        return nó.folha[0]

    def exprArit(self, nó):
        if len(nó.filho) == 3:
            esquerda =self.exprArit(nó.filho[0])
            operador = self.soma(nó.filho[1])
            direita = self.termo(nó.filho[2])

            if(esquerda == direita):
                return esquerda
            return 'flutuante'
        else:
            return self.termo(nó.filho[0])

    def soma(self, nó):
        return nó.folha[0]

    def termo(self, nó):
        if len(nó.filho) == 3:
            esquerda = self.termo(nó.filho[0])
            operador = self.multi(nó.filho[1])
            direita = self.fator(nó.filho[2])

            if operador == '/':
                return 'flutuante'

            if(esquerda == direita):
                return esquerda
            return 'flutuante'

        else:
            return self.fator(nó.filho[0])

    def multi(self, nó):
        return nó.folha[0]

    def fator(self, nó):
        if nó.nome == 'fatorExprArit':
            return self.exprArit(nó.filho[0])
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
        else:
            if not(nó.filho[0].folha[0] in self.símbolos.keys()):
                print("Erro semântico: função '" + nó.filho[0].folha[0] + "' não foi declarado")
                exit(1)
            if self.símbolos[nó.filho[0].folha[0]][1] == 'vazio':
                print("Erro semântico: função '" + nó.filho[0].folha[0] + "' é do tipo 'vazio', então não possui retorno")
                exit(1)
            return self.chamaFuncao(nó.filho[0])

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