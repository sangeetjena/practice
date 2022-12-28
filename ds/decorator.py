import logging
def capturelog(func):
    print("capturing log")
    def iner(*args):
        func(*args)
    return iner


@capturelog
def cal(x,*arg):
    print("sum = {0}".format(x+arg[0]))

cal(1,3)