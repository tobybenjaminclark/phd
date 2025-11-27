from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from pydantic.config import ConfigDict


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
class BooleanExpr(BaseModel): model_config = ConfigDict(frozen=True)
class ArithExpr(BaseModel): model_config = ConfigDict(frozen=True)



# Boolean Expressions
class And(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self): return f"{self.left} ∧ {self.right}"
    def __init__(self, l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))


class Or(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __str__(self): return f"{self.left} ∨ {self.right}"
    def __init__(self, l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)
    def __iter__(self): return iter((self.left, self.right))


class Not(BooleanExpr):
    inner: BooleanExpr
    def __str__(self): return f"¬ ({self.inner})"
    def __init__(self, i: BooleanExpr):  super().__init__(inner=i)
    def __iter__(self): return iter((self.inner,))


class Cmp(BooleanExpr):
    left: ArithExpr
    op: CmpOp
    right: ArithExpr
    def __str__(self): return f"{self.left} {self.op.value} {self.right}"
    def __init__(self, l: ArithExpr, o: CmpOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))


# Arithmetic Expressions
class Binary(ArithExpr):
    left: ArithExpr
    op: ArithOp
    right: ArithExpr
    def __str__(self): return f"{self.left} {self.op.value} {self.right}"
    def __init__(self, l: ArithExpr, o: ArithOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self): return iter((self.left, self.right))

class Number(ArithExpr):
    value: int
    def __str__(self): return str(self.value)
    def __init__(self, n: int):  super().__init__(value=n)
    def __iter__(self): return iter(())

class Symbol(ArithExpr):
    iden: str
    def __str__(self): return self.iden
    def __init__(self, i: str):  super().__init__(iden=i)
    def __iter__(self): return iter(())



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


for node in walk(rule):
    print(type(node), node)


