import re
import random
import os
from lark import Lark, Transformer

class Evaluatable:
    def eval(self) -> int:
        pass

class ListEvaluatable:
    def list_eval(self) -> [int]:
        pass

class ConstExpr(Evaluatable, ListEvaluatable):
    def __init__(self, n: int):
        self.n = n
    def eval(self):
        return self.n
    def list_eval(self):
        return [self.n]

class DiceExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b, n, exploding):
        self.n = n
        self.a = a
        self.b = b
        self.exploding = exploding
    def roll(self):
        rolls = []
        a = self.a.eval()
        b = self.b.eval()
        assert (not self.exploding) or (a != b)
        for i in range(self.n.eval()):
            sm = 0
            roll = random.randint(a, b)
            if self.exploding:
                while roll == b:
                    sm += roll
                    roll = random.randint(a, b)
            sm += roll
            rolls.append(sm)
        return rolls
    def eval(self):
        return sum(self.roll())
    def list_eval(self):
        return self.roll()

class SumExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def eval(self):
        return self.a.eval() + self.b.eval()
    def list_eval(self):
        return self.a.list_eval() + self.b.list_eval()

class SubExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def eval(self):
        return self.a.eval() - self.b.eval()
    def list_eval(self):
        return self.a.list_eval() + [-x for x in self.b.list_eval()]

class MulExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        n = self.a.eval()
        sm = []
        for i in range(max(0, n)):
            sm += self.b.list_eval()
        return sm
    
class KeepHighestExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        n = max(0, self.b.eval())
        lst = self.a.list_eval()
        lst.sort()
        lst.reverse()
        n = min(n, len(lst))
        return lst[:n]

class KeepLowestExpr(Evaluatable, ListEvaluatable):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        n = max(0, b.eval())
        lst = a.list_eval()
        lst.sort()
        n = min(n, len(lst))
        return lst[:n]

class CountExpr(Evaluatable, ListEvaluatable):
    def __init__(self, p, r):
        self.p = p
        self.r = r
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        lst = self.r.list_eval()
        sat = [1 if self.p(ConstExpr(x)) else 0 for x in lst]
        return sat

class RerollExpr(Evaluatable, ListEvaluatable):
    def __init__(self, p, r1, r2):
        self.p = p
        self.r1 = r1
        self.r2 = r2
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        res = self.r1.list_eval()
        loop = 0
        max_loop = None if self.r2 is None else self.r2.eval()
        while True:
            if max_loop is not None and loop >= max_loop:
                break
            loop += 1
            if not self.p(ConstExpr(sum(res))):
                break
            res = self.r1.list_eval()
        return res

class BranchExpr(Evaluatable, ListEvaluatable):
    def __init__(self, p, r1, r2, r3):
        self.p = p
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
    def eval(self):
        return sum(self.list_eval())
    def list_eval(self):
        cond = self.r1.eval()
        if self.p(ConstExpr(cond)):
            return self.r2.list_eval()
        else:
            return self.r3.list_eval()

class TreeToRoll(Transformer):
    def start(self):
        rolls = [(self[0].eval(), self[1])]
        if self[2] is not None:
            rolls += self[2]
        return rolls
    def paren_dice(self):
        return self[0]
    def only_dice(self):
        return self[0]
    def add_rolls(self):
        return SumExpr(self[0], self[1])
    def sub_rolls(self):
        return SubExpr(self[0], self[1])
    def mul_rolls(self):
        return MulExpr(self[0], self[1])
    def keep_highest(self):
        return KeepHighestExpr(self[0], self[1])
    def keep_lowest(self):
        return KeepLowestExpr(self[0], self[1])
    def count_predicate(self):
        return CountExpr(self[1], self[0])
    def reroll_predicate(self):
        return RerollExpr(self[2], self[0], self[1])
    def branch_predicate(self):
        return BranchExpr(self[0], self[1], self[2], self[3])
    def dice(self):
        return DiceExpr(ConstExpr(1), self[1], ConstExpr(1) if self[0] is None else self[0], self[2] is not None)
    def constant(self):
        return ConstExpr(int(self[0].value))
    def paren_predicate(self, pred):
        return pred
    def eq_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() == c
        return pred
    def lt_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() < c
        return pred
    def gt_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() > c
        return pred
    def le_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() <= c
        return pred
    def ge_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() >= c
        return pred
    def ne_predicate(self):
        c = self[0].eval()
        def pred(x):
            return x.eval() != c
        return pred
    def or_predicate(self):
        def pred(x):
            return self[0](x) or self[1](x)
        return pred
    def and_predicate(self):
        def pred(x):
            return self[0](x) and self[1](x)
        return pred
    def not_predicate(self):
        def pred(x):
            return not self[0](x)
        return pred


def parselalr(s):
    dataDir = os.path.join(os.getcwd(), 'data/')
    fileDir = os.path.join(dataDir, 'rollgrammar.lark')
    try:
        with open(fileDir, 'r') as larkstr:
            lark = Lark(larkstr, parser="lalr", transformer=TreeToRoll)
    except OSError:
        return
    tree = lark.parse(s)
    return tree

def rollstrtostring(s):
    prnt = ""
    res = parselalr(s)
    for (i, (num, label)) in enumerate(res):
        prnt += "Rolled " + str(num)
        if label is not None:
            prnt += " " + label
        prnt += "."
        if i != len(res) - 1:
            prnt += "\n"
    return prnt

def rollstrtonum(s):
    return [x[0] for x in parselalr(s)]
