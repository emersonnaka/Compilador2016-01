import sys
from subprocess import call
from gen import Gen

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    codigo = Gen(code)

    saida = open('build/program.ll', 'w')
    saida.write(str(codigo.modulo))
    saida.close()
    # print("Compilando...")
    # call(["llc-3.5", "build/program.ll"])
    # call(["gcc", "build/program.s", "-o", sys.argv[2]])
    # print("Pronto.")