from __future__ import annotations
from enum import Enum
from unittest import case

from pydantic import BaseModel
from pydantic.config import ConfigDict
import random
import operator
import time
import z3





# Define a trait necessitating an object must convert to SMT
class SMTConvertible:
    def to_z3(self):    raise NotImplementedError()

# Define a trait necessitating an object must mutate (and support random creation)
class Genetic:
    def mutate(self):   raise NotImplementedError()

    @classmethod
    def random(cls):    raise NotImplementedError()





# Enumerations to denote comparison and arithmetic operators
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

    def get_op(self):
        match self:
            case CmpOp.GT: return operator.gt
            case CmpOp.LT: return operator.lt
            case CmpOp.EQ: return operator.eq
            case CmpOp.GE: return operator.ge
            case CmpOp.LE: return operator.le

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

    def get_op(self):
        match self:
            case ArithOp.ADD: return operator.add
            case ArithOp.SUB: return operator.sub
            case ArithOp.MUL: return operator.mul
            case ArithOp.DIV: return operator.truediv



# Base Expressions
class BooleanExpr(BaseModel, Genetic, SMTConvertible):
    model_config = ConfigDict(frozen=False)
    def mutate(self):   raise NotImplementedError()

    @classmethod
    def random(_, depth=2): return Cmp.random(depth) if depth <= 0 else random.choice([And, Or, Not, Cmp]).random(depth - 1)

    def __len__(self):      return 1 + sum(len(child) for child in self)
    def eval(self, symtable):   raise NotImplementedError

class ArithExpr(BaseModel, Genetic, SMTConvertible):
    model_config = ConfigDict(frozen=False)
    def mutate(self):       raise NotImplementedError()

    @classmethod
    def random(_, depth=1):
        return Symbol.random() if depth <= 0 else random.choice([Binary, Symbol]).random(depth-1)

    def __len__(self):      return 1 + sum(len(child) for child in self)
    def eval(self, sample): raise NotImplementedError







# Boolean Expressions
class And(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __init__(self, l: BooleanExpr, r: BooleanExpr):
        super().__init__(left=l, right=r)

    def __str__(self):      return f"{self.left} ∧ {self.right}"
    def __iter__(self):     return iter((self.left, self.right))
    def mutate(self):       return Or(self.left, self.right)
    def to_z3(self):        return z3.And(self.left.to_z3(), self.right.to_z3())
    def eval(self, sample): return self.left.eval(sample) and self.right.eval(sample)

    @classmethod
    def random(_, depth=2):     return And(BooleanExpr.random(depth-1), BooleanExpr.random(depth-1))


class Or(BooleanExpr):
    left: BooleanExpr
    right: BooleanExpr
    def __init__(self, l: BooleanExpr, r: BooleanExpr):  super().__init__(left=l, right=r)

    def __str__(self):      return f"{self.left} ∨ {self.right}"
    def __iter__(self):     return iter((self.left, self.right))
    def mutate(self):       return And(self.left, self.right)
    def to_z3(self):        return z3.Or(self.left.to_z3(), self.right.to_z3())
    def eval(self, sample): return self.left.eval(sample) or self.right.eval(sample)

    @classmethod
    def random(_, depth=2):
        return Or(BooleanExpr.random(depth-1), BooleanExpr.random(depth-1))


class Not(BooleanExpr):
    inner: BooleanExpr

    def __init__(self, i: BooleanExpr):  super().__init__(inner=i)
    def __str__(self):      return f"¬ ({self.inner})"
    def __iter__(self):     return iter((self.inner,))
    def mutate(self):       return (self.inner)
    def to_z3(self):        return z3.Not(self.inner.to_z3())
    def eval(self, sample): return not (self.inner.eval(sample))

    @classmethod
    def random(_, depth=2):
        return Not(BooleanExpr.random(depth-1))


class Cmp(BooleanExpr):
    left: ArithExpr
    op: CmpOp
    right: ArithExpr

    def __init__(self, l: ArithExpr, o: CmpOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)

    def __str__(self):      return f"{self.left} {self.op.value} {self.right}"
    def __iter__(self):     return iter((self.left, self.right))
    def mutate(self):       return Cmp(self.left, random.choice(list(CmpOp)), self.right)
    def to_z3(self):        return self.op.to_z3(self.left.to_z3(), self.right.to_z3())
    def eval(self, sample): return self.op.get_op()(self.left.eval(sample), self.right.eval(sample))

    @classmethod
    def random(_, depth=0):
        return Cmp(ArithExpr.random(1), random.choice(list(CmpOp)), ArithExpr.random(1))





# Arithmetic Expressions
class Binary(ArithExpr):
    left: ArithExpr
    op: ArithOp
    right: ArithExpr
    def __str__(self):      return f"{self.left} {self.op.value} {self.right}"
    def __init__(self,  l: ArithExpr, o: ArithOp, r: ArithExpr):  super().__init__(left=l, op=o, right=r)
    def __iter__(self):     return iter((self.left, self.right))
    def mutate(self):       return Binary(self.left, random.choice(list(ArithOp)), self.right)
    def to_z3(self):        return self.op.to_z3(self.left.to_z3(), self.right.to_z3())
    def eval(self, sample): return self.op.get_op()(self.left.eval(sample), self.right.eval(sample))

    @classmethod
    def random(_, depth=1):
        return Binary(ArithExpr.random(depth-1), random.choice(list(ArithOp)), ArithExpr.random(depth-1))

class Number(ArithExpr):
    value: float
    def __init__(self,  n: float):  super().__init__(value=n)
    def __str__(self):      return str(self.value)
    def __iter__(self):     return iter(())
    def mutate(self):       return Number(self.value + random.randrange(-50, 50) / 100)
    def to_z3(self):        return z3.RealVal(self.value)
    def eval(self, sample): return self.value

    @classmethod
    def random(_, depth=0):     return random.choice(SYMBOLS)

class Symbol(ArithExpr):
    iden: str
    def __init__(self,  i: str):  super().__init__(iden=i)
    def __str__(self):      return self.iden
    def __iter__(self):     return iter(())
    def mutate(self):       return random.choice(SYMBOLS)
    def to_z3(self):        return z3.Real(self.iden)
    def eval(self, sample): return sample[self.iden]

    @classmethod
    def random(_, depth=0):     return random.choice(SYMBOLS)



def set_symbol_universe(names):
    global SYMBOLS
    SYMBOLS = [Symbol(n) for n in names]

