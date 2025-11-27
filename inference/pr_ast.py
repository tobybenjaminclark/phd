from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from pydantic.config import ConfigDict
import random

# Operators
class CmpOp(str, Enum):
    GT = ">"
    LT = "<"
    EQ = "="
    GE = "≥"
    LE = "≤"


class ArithOp(str, Enum):
    ADD = "+"
    SUB = "-"
    MUL = "×"
    DIV = "÷"



# Base Expressions
class BooleanExpr(BaseModel):
    model_config = ConfigDict(frozen=False)
    def mutate(self):   raise NotImplementedError()

class ArithExpr(BaseModel):
    model_config = ConfigDict(frozen=False)
    def mutate(self):   raise NotImplementedError()


# Boolean Expressions
class And(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self):  return f"{self.left} ∧ {self.right}"
    def __init__(self,  l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Or(self.left, self.right)

class Or(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self):  return f"{self.left} ∨ {self.right}"
    def __init__(self,  l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return And(self.left, self.right)


class Not(BooleanExpr):
    inner: BooleanExpr
    def __str__(self): return f"¬ ({self.inner})"
    def __init__(self, i: BooleanExpr):  super().__init__(inner=i)
    def __iter__(self): return iter((self.inner,))
    def mutate(self):   return (self.inner)



class Cmp(BooleanExpr):
    left: ArithExpr
    op: CmpOp
    right: ArithExpr
    def __str__(self):  return f"{self.left} {self.op.value} {self.right}"
    def __init__(self,  l: ArithExpr, o: CmpOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Cmp(self.left, random.choice(list(CmpOp)), self.right)

# Arithmetic Expressions
class Binary(ArithExpr):
    left: ArithExpr
    op: ArithOp
    right: ArithExpr
    def __str__(self):  return f"{self.left} {self.op.value} {self.right}"
    def __init__(self,  l: ArithExpr, o: ArithOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))
    def mutate(self):   return Cmp(self.left, random.choice(list(ArithOp)), self.right)

class Number(ArithExpr):
    value: float
    def __str__(self):  return str(self.value)
    def __init__(self,  n: float):  super().__init__(value=n)
    def __iter__(self): return iter(())
    def mutate(self):   return Number(self.n + random.randrange(-50, 50) / 100)

class Symbol(ArithExpr):
    iden: str
    def __str__(self):  return self.iden
    def __init__(self,  i: str):  super().__init__(iden=i)
    def __iter__(self): return iter(())
    def mutate(self):   return random.choice(SYMBOLS)

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
    for child in expr:
        yield from walk(child)


import random
import time

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

    # User-provided node-level mutation
    result = node.mutate()

    # No replacement needed
    if result is None or result is node:
        return expr

    # Replacement (e.g. removing NOT)
    if parent is None:
        return result  # replaced root
    setattr(parent, field, result)
    return expr


# mutate loop
def mutate_loop(expr, steps=20):
    print("Initial:", expr)
    for _ in range(steps):
        expr = mutate_one(expr)
        print("Mutated:", expr)
        time.sleep(0.2)


mutate_loop(rule)

