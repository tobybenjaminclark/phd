from pr_ast import *
from form import *
from z3 import Model
import random
import copy
import numpy as np
import functools







import time
TIMINGS = {}

def timed(name, fn):
    start = time.perf_counter()
    out = fn()
    TIMINGS[name] = TIMINGS.get(name, 0) + (time.perf_counter() - start)
    return out






def breed(a: BooleanExpr, b: BooleanExpr) -> BooleanExpr:
    def collect_nodes(expr, classes):
        nodes = []

        def _walk(node):
            if isinstance(node, classes):
                nodes.append(node)
            for child in node:
                _walk(child)

        _walk(expr)
        return nodes

    def replace_subtree(root, target, replacement):
        if root is target:
            return replacement

        for field_name, field_value in root.__dict__.items():
            if field_value is target:
                setattr(root, field_name, copy.deepcopy(replacement))
                return root

            if isinstance(field_value, (BooleanExpr, ArithExpr)):
                replaced = replace_subtree(field_value, target, replacement)
                if replaced is not field_value:
                    setattr(root, field_name, replaced)
                    return root

        return root

    # Copy to avoid mutating both parents
    a_copy = copy.deepcopy(a)
    b_copy = copy.deepcopy(b)

    # Collect ALL possible crossover nodes
    a_nodes = collect_nodes(a_copy, (BooleanExpr, ArithExpr))
    b_nodes = collect_nodes(b_copy, (BooleanExpr, ArithExpr))

    # Pick random subtree from A
    subtree_a = random.choice(a_nodes)

    # Find matching candidates in B
    same_type = [n for n in b_nodes if isinstance(n, type(subtree_a))]
    same_family = [
        n for n in b_nodes
        if isinstance(n, BooleanExpr) and isinstance(subtree_a, BooleanExpr) or
           isinstance(n, ArithExpr) and isinstance(subtree_a, ArithExpr)
    ]

    candidates = same_type or same_family or b_nodes
    subtree_b = random.choice(candidates)

    # Perform crossover
    replace_subtree(a_copy, subtree_a, subtree_b)
    return a_copy






def mutate_one(expr):
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




form = CompleteOrderForm()

@functools.lru_cache(None)
def monte_carlo(rule, n = 50_000, low = 0, high = 1_000):
    """ Monte-Carlo approximation to calculate the activation percentage of a pruning condition """
    syms = list(form.symbol_set())
    env = {s: np.random.uniform(low, high, n) for s in syms}
    return np.mean(rule.eval_np(env))



def gen_initial(number: int) -> [BooleanExpr]:
    return [BooleanExpr.random(random.choice([1, 2, 3, 4])) for _ in range(number)]



def _fitness(β: BooleanExpr, Σ, βmax: int) -> [float]:
    β_z3 = β.to_z3()

    # weights
    ω1, ω2, ω3 = 1.5, 1.0, 1.0

    # --- term 1: labelled examples accuracy ---
    if Σ:
        correct = 0
        for (model, expected) in Σ:
            val = z3.is_true(model.eval(β_z3, model_completion=True))
            correct += (val == expected)
        t1 = correct / len(Σ)
    else:
        t1 = 0.5

    # --- term 2: size penalty ---
    t2 = 1 - (len(β) / βmax)

    # --- term 3: Monte Carlo activation ---
    p = monte_carlo(β)
    eps = 1e-9
    t3 = -(p * np.log(p + eps) + (1 - p) * np.log((1 - p) + eps))

    score = (ω1*t1 + ω2*t2 + ω3*t3) / (ω1 + ω2 + ω3)
    return score, t1, t2, t3



def fitness(population: [BooleanExpr], Σ):
    βmax = len(max(population, key=lambda β: len(β)))
    return [(β, *_fitness(β, Σ, βmax)) for β in population]






# The top 25% make it through
def selection(fitpop: [(BooleanExpr, float)]) -> [BooleanExpr]:
    ranked =        sorted(fitpop, key=lambda x: x[1], reverse=True)
    survivors =     [expr for expr, *_ in ranked[:len(ranked)//4]]
    return          [None]*(len(fitpop)-len(survivors)) + survivors



def crossover(population: [BooleanExpr]) -> [BooleanExpr]:
    fertile =           list(filter(lambda v: v is not None, population))

    for idx, _ in filter(lambda idx_v: idx_v[1] is None, enumerate(population)):
        population[idx] = breed(*random.sample(fertile, 2))

    return population



def mutation(population: [BooleanExpr]) -> [BooleanExpr]:
    return list(map(
        lambda β: mutate_one(β) if (random.random() < 0.5) else β,
        population
    ))













def genetic_algorithm(starting=10, generations=1000, elite=2, Σ=None):
    if Σ is None:
        Σ = []

    population = gen_initial(starting)

    for gen_num in range(generations):
        fitpop = timed("fitness", lambda: fitness(population, Σ))

        print(f"Generation {gen_num}")
        for rank, (expr, score, t1, t2, t3) in enumerate(fitpop, 1):
            expr_str = str(expr)
            print(f"[{rank:^4}] {expr_str:<50} (Score of {score:.4f} \t Σ:{t1:.3f}, \t βmax: {t2:.3f}, \t #: {t3:.3f})")

        elites = [expr for expr, *rest in sorted(fitpop, key=lambda x: x[1], reverse=True)[:elite]]


        surpop = timed("selection", lambda: selection(fitpop))
        sexpop = timed("crossover", lambda: crossover(surpop))
        mutpop = timed("mutation", lambda: mutation(sexpop))

        # protect elites
        mutpop[:elite] = elites
        population = mutpop

        print("\n  Time profile so far:")
        for k, v in TIMINGS.items():
            print(f"    {k:<10}: {v:.6f}s")
        print()

    # return best from final generation
    final_fit = fitness(population, Σ)
    best, *rest = max(final_fit, key=lambda x: x[1])
    return best, rest[0]

