from gen import Gen

if __name__ == '__main__':
    import sys
    code = open(sys.argv[1])
    Gen(code)