from pr_ast import *
from form import *
import random, copy, numpy as np, functools, time

def timed(name, fn):
    start = time.perf_counter()
    out = fn()
    TIMINGS[name] = TIMINGS.get(name, 0) + (time.perf_counter() - start)
    return out


TIMINGS = {}
FORM = CompleteOrderForm()





@functools.lru_cache(None)
def monte_carlo(rule, n=50_000, low=0, high=1_000):
    syms = list(FORM.symbol_set())
    env = {s: np.random.uniform(low, high, n) for s in syms}
    return np.mean(rule.eval_np(env))

def entropy(p, eps=1e-9):
    return -(p*np.log(p+eps) + (1-p)*np.log(1-p+eps))





class ProgramSearch:


    @staticmethod
    def _collect(expr, kinds):
        return [n for n in expr.walk() if isinstance(n, kinds)]


    @staticmethod
    def find_parent(expr, target):
        return next(((p, k) for p in expr.walk() for k, v in p.__dict__.items() if v is target), (None, None))


    @staticmethod
    def breed(a: BooleanExpr, b: BooleanExpr) -> BooleanExpr:
        """Cross two trees at compatible AST nodes."""
        a = copy.deepcopy(a)
        nodes_a = ProgramSearch._collect(a, (BooleanExpr, ArithExpr))
        nodes_b = ProgramSearch._collect(copy.deepcopy(b), (BooleanExpr, ArithExpr))

        cut_a = random.choice(nodes_a)

        same_type = [n for n in nodes_b if isinstance(n, type(cut_a))]
        same_kind = [n for n in nodes_b if isinstance(n, BooleanExpr) == isinstance(cut_a, BooleanExpr)]
        cut_b = random.choice(same_type or same_kind or nodes_b)

        return replace_subtree(a, cut_a, cut_b)


    @staticmethod
    def mutate_one(expr):
        """Mutate an expression."""

        node = random.choice(ProgramSearch._collect(expr, (BooleanExpr, ArithExpr)))
        parent, field = ProgramSearch.find_parent(expr, node)

        # 30%: full replacement
        if random.random() < 0.3:
            repl = node.__class__.random()
            return repl if parent is None else (setattr(parent, field, repl) or expr)

        # 70%: local mutate()
        new = node.mutate()
        if not new or new is node:
            return expr
        return new if parent is None else (setattr(parent, field, new) or expr)


    @staticmethod
    def gen_initial(n: int):
        """ Generate an initial population of `n` boolean expressions."""
        return [BooleanExpr.random(random.choice([1, 2, 3, 4])) for _ in range(n)]


    @staticmethod
    def selection(fitpop):
        """ Keep top 25% by fitness; others replaced with None for breeding. """
        ranked = sorted(fitpop, key=lambda x: x[1], reverse=True)
        return [expr for expr, *_ in ranked[:len(ranked) // 4]] + [None] * (len(ranked) - len(ranked) // 4)


    @staticmethod
    def crossover(pop):
        """ Perform crossover on a population of expressions, replaces 'None' members with children """
        return [v or ProgramSearch.breed(*random.sample([p for p in pop if p], 2)) for v in pop]


    @staticmethod
    def mutation(pop, chance=0.5):
        """ Mutate a population of expressions """
        return [ProgramSearch.mutate_one(p) if random.random() < chance else p for p in pop]


    @staticmethod
    def _fitness(β: BooleanExpr, Σ: [z3.Model], βmax: int) -> (float, float, float):
        """ Compute fitness for a singular boolean expression. """
        βz = β.to_z3()
        return (
            (sum(z3.is_true(m.eval(βz, model_completion=True)) == e for m, e in Σ) / len(Σ)) if Σ else 0.5,
            1 - len(β) / βmax,
            entropy(monte_carlo(β))
        )


    @staticmethod
    def fitness(pop: [BooleanExpr], Σ) -> [float]:
        """ Compute weighted fitness for a generation of boolean expressions. """
        βmax = len(max(pop, key=len))
        ω = (2.5, 1.0, 1.0)
        return [
            (β, (ω[0] * t1 + ω[1] * t2 + ω[2] * t3) / sum(ω), t1, t2, t3)
            for β in pop
            for (t1, t2, t3) in (ProgramSearch._fitness(β, Σ, βmax),)
        ]


    @staticmethod
    def run_generation(pop, Σ, elite=2):
        """Run one generation step and return the next population."""

        fitpop = timed("fitness", lambda: ProgramSearch.fitness(pop, Σ))

        elites = [e for e, *_ in sorted(fitpop, key=lambda x: x[1], reverse=True)[:elite]]

        surpop = ProgramSearch.selection(fitpop)
        sexpop = timed("crossover", lambda: ProgramSearch.crossover(surpop))
        mutpop = timed("mutation", lambda: ProgramSearch.mutation(sexpop))

        mutpop[:elite] = elites
        return mutpop, fitpop


    @staticmethod
    def search(start=10, gens=1000, elite=2, Σ=None, pop=None):

        Σ = Σ or []
        pop = pop or ProgramSearch.gen_initial(start)

        for g in range(gens):
            pop, fitpop = ProgramSearch.run_generation(pop, Σ, elite)

            """
            print(f"Generation {g}")
            for i, (expr, sc, t1, t2, t3) in enumerate(fitpop, 1):
                print(f"[{i:^3}] {expr!s:<45} (score {sc:.4f} Σ:{t1:.3f} β:{t2:.3f} H:{t3:.3f})")

            print("\nTime profile:")
            for k, v in TIMINGS.items():
                print(f"  {k:<10} {v:.6f}s")
            print()
            """

        best = max(ProgramSearch.fitness(pop, Σ), key=lambda x: x[1])
        return best[0], best[1], pop
