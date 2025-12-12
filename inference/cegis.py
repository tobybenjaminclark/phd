import time
from form import CompleteOrderForm
from pr_ast import *
from genetic import ProgramSearch

form = CompleteOrderForm()
set_symbol_universe(form.symbol_set())
_MC_CACHE = {}





class CEGIS():
    round_number = 0

    def round(self):

        self.round_number += 1

        print(f"\n=== CEGIS round {self.round_number} (|Σ|={len(self.Σ)}) | Verified={len(self.verified_rules)} ===")

        best, best_score, pop = ProgramSearch.search(
            start = self.starting,
            gens = self.generations,
            elite = self.elite,
            Σ = self.Σ,
            pop = self.pop
        )

        print(f"CEGIS candidate: {best} (score={best_score:.4f})")

        if not form.is_rule_satisfiable(best):
            print("[CEGIS] Rule UNSAT under constraints -> discarding.")
            # Optional: Force rule True to get a positive training point
            s = z3.Solver()
            for c in form.constraints: s.add(c())
            s.add(best.to_z3())
            if s.check() == z3.sat:
                self.Σ.append((s.model(), True))
            return

        # Check for counterexamples (unsoundness)
        cex = form.find_unsound_counterexample(best)
        if cex is None:
            print("[CEGIS] Rule appears SOUND & non-vacuous. Recording.")
            self.verified_rules.append(best)
            return

        # add counterexample as negative example
        print("[CEGIS] Unsoundness counterexample found -> adding to Σ (False).")
        self.Σ.append((cex, False))

    def __init__(self, form: CompleteOrderForm, *, max_rounds: int = 50, starting: int = 30, generations: int = 50, elite: int = 4, target_solutions: int = 5):
        self.form = form
        self.max_rounds = max_rounds
        self.starting = starting
        self.generations = generations
        self.elite = elite
        self.target_solutions = target_solutions

        self.Σ: list[tuple[z3.Model, bool]] =   []
        self.verified_rules: [BooleanExpr] =    []
        self.pop: [BooleanExpr] =               None

    def synthesise(self) -> [BooleanExpr]:
        for outer in range(self.max_rounds):
            self.round()
            if len(self.verified_rules) >= self.target_solutions:
                print("[CEGIS] Found all rules")
        print("\n=== Max CEGIS rounds reached ===")
        return self.verified_rules





if __name__ == "__main__":
    form = CompleteOrderForm()
    set_symbol_universe(form.symbol_set())

    cegis = CEGIS(
        form,
        max_rounds=250,
        starting=10,
        generations=25,
        elite=4
    )
    rule = cegis.synthesise()
    print("Final CEGIS result:")
    for r in rule:
        print(f"- {r}")
