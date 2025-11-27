from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from pydantic.config import ConfigDict
import random
import time
import z3



class SMTConvertible:
    def to_z3(self):    raise NotImplementedError()


class Genetic:
    def mutate(self):   raise NotImplementedError()

    @classmethod
    def random(cls):    raise NotImplementedError()





# Operators
class CmpOp(SMTConvertible, str, Enum):
    GT = ">"
    LT = "<"
    EQ = "="
    GE = "≥"
    LE = "≤"

    def to_z3(self, left, right):
        match self:
            case CmpOp.GT: return left > right
            case CmpOp.LT: return left < right
            case CmpOp.EQ: return left == right
            case CmpOp.GE: return left >= right
            case CmpOp.LE: return left <= right


class ArithOp(SMTConvertible, str, Enum):
    ADD = "+"
    SUB = "-"
    MUL = "×"
    DIV = "÷"

    def to_z3(self, left, right):
        match self:
            case ArithOp.ADD: return left + right
            case ArithOp.SUB: return left - right
            case ArithOp.MUL: return left * right
            case ArithOp.DIV: return left / right



# Base Expressions
class BooleanExpr(BaseModel, Genetic, SMTConvertible):
    model_config = ConfigDict(frozen=False)
    def mutate(self):   raise NotImplementedError()

    @classmethod
    def random(_):    return random.choice([And, Or, Not, Cmp]).random()

class ArithExpr(BaseModel, Genetic, SMTConvertible):
    model_config = ConfigDict(frozen=False)
    def mutate(self):   raise NotImplementedError()

    @classmethod
    def random(_):      return random.choice([Binary, Number, Symbol]).random()





# Boolean Expressions
class And(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self):  return f"{self.left} ∧ {self.right}"
    def __init__(self,  l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Or(self.left, self.right)
    def to_z3(self):    return z3.And(self.left.to_z3(), self.right.to_z3())

    @classmethod
    def random(_):      return And(BooleanExpr.random(), BooleanExpr.random())


class Or(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self):  return f"{self.left} ∨ {self.right}"
    def __init__(self,  l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return And(self.left, self.right)
    def to_z3(self):    return z3.Or(self.left.to_z3(), self.right.to_z3())

    @classmethod
    def random(_):      return Or(BooleanExpr.random(), BooleanExpr.random())


class Not(BooleanExpr):
    inner: BooleanExpr
    def __str__(self): return f"¬ ({self.inner})"
    def __init__(self, i: BooleanExpr):  super().__init__(inner=i)
    def __iter__(self): return iter((self.inner,))
    def mutate(self):   return (self.inner)
    def to_z3(self):    return z3.Not(self.inner.to_z3())

    @classmethod
    def random(_):      return Not(BooleanExpr.random())


class Cmp(BooleanExpr):
    left: ArithExpr
    op: CmpOp
    right: ArithExpr
    def __str__(self):  return f"{self.left} {self.op.value} {self.right}"
    def __init__(self,  l: ArithExpr, o: CmpOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Cmp(self.left, random.choice(list(CmpOp)), self.right)
    def to_z3(self):    return self.op.to_z3(self.left.to_z3(), self.right.to_z3())

    @classmethod
    def random(_):      return Cmp(ArithExpr.random(), random.choice(list(CmpOp)), ArithExpr.random())





# Arithmetic Expressions
class Binary(ArithExpr):
    left: ArithExpr
    op: ArithOp
    right: ArithExpr
    def __str__(self):  return f"{self.left} {self.op.value} {self.right}"
    def __init__(self,  l: ArithExpr, o: ArithOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Binary(self.left, random.choice(list(ArithOp)), self.right)
    def to_z3(self):    return self.op.to_z3(self.left.to_z3(), self.right.to_z3())

    @classmethod
    def random(_):      return Binary(ArithExpr.random(), random.choice(list(ArithOp)), ArithExpr.random())

class Number(ArithExpr):
    value: float
    def __str__(self):  return str(self.value)
    def __init__(self,  n: float):  super().__init__(value=n)
    def __iter__(self): return iter(())
    def mutate(self):   return Number(self.value + random.randrange(-50, 50) / 100)
    def to_z3(self):    return z3.RealVal(self.value)

    @classmethod
    def random(cls):    return Number(random.uniform(-5, 5))

class Symbol(ArithExpr):
    iden: str
    def __str__(self):  return self.iden
    def __init__(self,  i: str):  super().__init__(iden=i)
    def __iter__(self): return iter(())
    def mutate(self):   return random.choice(SYMBOLS)
    def to_z3(self):    return z3.Real(self.iden)

    @classmethod
    def random(cls):    return random.choice(SYMBOLS)





SYMBOLS = list(map(lambda x: Symbol(x), ["A", "B", "C", "D"]))





rule = Not(
    Cmp(
        Symbol("r_i"),
        CmpOp.GE,
        Symbol("r_j")
    )
)


print(rule)

def walk(expr):
    yield expr
    for child in expr: yield from walk(child)

# indexed walk
def indexed_walk(expr):
    stack = [(None, None, expr)]
    while stack:
        parent, field, node = stack.pop()
        yield parent, field, node
        for child in node:
            for k, v in node.__dict__.items():
                if v is child:
                    stack.append((node, k, child))
                    break


# mutate one
def mutate_one(expr):
    nodes = list(indexed_walk(expr))
    parent, field, node = random.choice(nodes)

    # 30% chance: subtree replacement with same type
    if random.random() < 0.3:
        new_node = node.__class__.random()
        if parent is None:
            return new_node
        setattr(parent, field, new_node)
        return expr

    # Otherwise use node's local mutate()
    result = node.mutate()

    if result is None or result is node:
        return expr

    if parent is None:
        return result
    setattr(parent, field, result)
    return expr


# mutate loop
def mutate_loop(expr, steps=20):
    print("Initial:", expr)
    for _ in range(steps):
        expr = mutate_one(expr)
        print("Mutated:", expr)
        time.sleep(0.2)



def implies(rule_expr):
    A = z3.Real("A")

    # 1. Check that the rule is satisfiable at all (not vacuous)
    sat_solver = z3.Solver()
    sat_solver.add(rule_expr.to_z3())
    if sat_solver.check() != z3.sat:
        return False   # rule is contradictory → reject

    # 2. Check implication validity:
    #    R ∧ ¬(A > 10) is UNSAT
    imp_solver = z3.Solver()
    imp_solver.add(rule_expr.to_z3())
    imp_solver.add(A <= 10)

    return imp_solver.check() == z3.unsat




def search_for_implication(initial, max_iters=1000, reset_prob=0.01):
    expr = initial

    for i in range(max_iters):

        # random restart
        if random.random() < reset_prob:
            expr = initial
        else:
            try:
                expr = mutate_one(expr)
            except:
                pass

        if implies(expr):
            print(f"\nFound rule after {i} mutations:\n{expr}")
            print(f"\nRule Simplified: {z3.simplify(expr.to_z3())}")
            return expr

        if i % 50 == 0:
            print(f"[{i}] still searching… (maybe resetting) \t \t \t")

    print("No rule found")
    return None


found = search_for_implication(rule, max_iters=5000)
