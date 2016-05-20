class AST():
    def __init__(self, nome, filho, folha=None ):
        self.nome = nome
        self.filho = filho
        self.folha = folha

    def __str__(self, level=0):
        ret = "|"*level+repr(self.nome)+"\n"
        for child in self.filho:
            ret += child.__str__(level+1)
        return ret