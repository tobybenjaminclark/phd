from pr_ast import *
from form import *





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


FORM = CompleteOrderForm()

set_symbol_universe(FORM.symbol_set())


def implies(rule_ast):
    z3_rule = rule_ast.to_z3()
    return FORM.verify_rule(z3_rule)


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

        if i % 50 == 0 and i != 0:
            print(f"[{i}] still searching… (maybe resetting) \t \t \t Current-Expr = {expr}")

    print("No rule found")
    return None





found = search_for_implication(Cmp(Symbol("R_i"), CmpOp.GT, Symbol("R_j")), max_iters=5000)
