import time
from form import CompleteOrderForm
from pr_ast import *
from genetic import ProgramSearch

form = CompleteOrderForm()
set_symbol_universe(form.symbol_set())
_MC_CACHE = {}


def find_counterexamples(candidate: BooleanExpr,
                         spec: z3.ExprRef,
                         max_cex: int = 5) -> list[z3.Model]:
    """
    Find up to `max_cex` models where candidate != spec.
    Returns a list of z3.Models.
    """
    s = z3.Solver()
    cand = candidate.to_z3()

    # Candidate should match spec; counterexamples are where they differ.
    s.add(z3.Xor(cand, spec))

    cexs = []

    while len(cexs) < max_cex and s.check() == z3.sat:
        m = s.model()
        cexs.append(m)

        # block this model so we can look for another one
        blocking_literals = []
        for d in m.decls():
            v = m[d]
            # Only block on interpreted values (reals/bools etc.)
            if isinstance(v, (z3.ArithRef, z3.BoolRef)):
                blocking_literals.append(d() != v)

        if not blocking_literals:
            break

        s.add(z3.Or(blocking_literals))

    return cexs

def cegis(form: CompleteOrderForm,
          max_rounds: int = 50,
          starting: int = 30,
          generations: int = 50,
          elite: int = 4,
          target_solutions: int = 5):
    """
    Continues evolving until `target_solutions` sound and non-vacuous rules
    have been found (or max_rounds reached).
    """
    Σ: list[tuple[z3.Model, bool]] = []
    verified_rules = []

    for outer in range(max_rounds):
        print(f"\n=== CEGIS round {outer} (|Σ|={len(Σ)}) | Verified={len(verified_rules)} ===")

        best, best_score = ProgramSearch.genetic_algorithm(
            start=starting,
            gens=generations,
            elite=elite,
            Σ=Σ
        )
        print(f"CEGIS candidate: {best} (score={best_score:.4f})")

        # reject unsatisfiable (vacuous) rules
        if not form.is_rule_satisfiable(best):
            print("[CEGIS] Rule UNSAT under constraints -> discarding.")
            # Optional: Force rule True to get a positive training point
            s = z3.Solver()
            for c in form.constraints: s.add(c())
            s.add(best.to_z3())
            if s.check() == z3.sat:
                Σ.append((s.model(), True))
            continue

        # Check for counterexamples (unsoundness)
        cex = form.find_unsound_counterexample(best)
        if cex is None:
            print("[CEGIS] Rule appears SOUND & non-vacuous. Recording.")
            verified_rules.append(best)

            if len(verified_rules) >= target_solutions:
                print("\n=== Found enough verified rules ===\n")
                return verified_rules

            # Don't add a negative sample — it passed. Just continue evolving.
            continue

        # add counterexample as negative example
        print("[CEGIS] Unsoundness counterexample found -> adding to Σ (False).")
        Σ.append((cex, False))

    print("\n=== Max CEGIS rounds reached ===")
    return verified_rules




if __name__ == "__main__":
    form = CompleteOrderForm()
    set_symbol_universe(form.symbol_set())

    rule = cegis(
        form,
        max_rounds=100,
        starting=30,
        generations=5,
        elite=4
    )
    print("Final CEGIS result:", rule)
