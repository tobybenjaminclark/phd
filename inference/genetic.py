from pr_ast import *

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
    B = z3.Real("B")

    # 1. Check that the rule is satisfiable at all (not vacuous)
    sat_solver = z3.Solver()
    sat_solver.add(rule_expr.to_z3())
    if sat_solver.check() != z3.sat:
        return False   # rule is contradictory → reject

    # 2. Check implication validity:
    #    R ∧ ¬(A > 10) is UNSAT
    imp_solver = z3.Solver()
    imp_solver.add(rule_expr.to_z3())
    imp_solver.add(A <= B)

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
