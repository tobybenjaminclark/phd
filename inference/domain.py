import z3
from enum import Enum


class Type(Enum):
    Integer =   lambda x: z3.Int(x)
    Real =      lambda x: z3.Real(x)


class Domain():
    functional_attributes = list[(str, Type)]
    variables             = list[(str, Type)]


class RSPDomain(Domain):

    def __init__(self):
        self.functional_attributes = [
            ("CTOT_START", Type.Real),
            ("CTOT_END", Type.Real),
            ("TIME_WINDOW_START", Type.Real),
            ("TIME_WINDOW_END", Type.Real),
            ("B", Type.Real),
            ("C", Type.Real),
            ("δ", Type.Real),
        ]

