from form import CompleteOrderForm
from pr_ast import *
from genetic import ProgramSearch
from tqdm import tqdm
import math



form = CompleteOrderForm()
set_symbol_universe(form.symbol_set())
_MC_CACHE = {}



class CEGIS:
    def __init__(self, form: CompleteOrderForm, *, max_rounds=50, starting=30,
                 generations=50, elite=4, target_solutions=5):
        self.form = form
        self.max_rounds = max_rounds
        self.starting = starting
        self.generations = generations
        self.elite = elite
        self.target_solutions = target_solutions

        self.Σ = []
        self.verified_rules = []
        self.pop = None
        self.round_number = 0

    def round(self):
        self.round_number += 1

        tqdm.write(f"\n𝗖𝗼𝘂𝗻𝘁𝗲𝗿 𝗘𝘅𝗮𝗺𝗽𝗹𝗲 𝗚𝘂𝗶𝗱𝗲𝗱 𝗜𝗻𝗱𝘂𝗰𝘁𝗶𝘃𝗲 𝗦𝘆𝗻𝘁𝗵𝗲𝘀𝗶𝘀 | Round {self.round_number} of {self.max_rounds} | Solutions Found: {len(self.verified_rules)} of {self.target_solutions} | Σ* contains {len(self.Σ)} counterexamples")

        best, best_score, pop = ProgramSearch.search(
            start=self.starting,
            gens=self.generations,
            elite=self.elite,
            Σ=self.Σ,
            pop=self.pop,
        )

        self.pop = pop

        fitpop = ProgramSearch.fitness(pop, self.Σ)
        avg = sum(sc for (_, sc, *_) in fitpop) / len(fitpop)

        top3 = sorted(fitpop, key=lambda x: x[1], reverse=True)[:3]
        for i, (rule, *scores) in enumerate(top3, start=1):
            sigma, betamax, monte = scores[:3]
            tqdm.write(
                f" ► [{i}] {str(rule):<40} | "
                f"Σ: {sigma:7.4f} | "
                f"βmax: {betamax:7.4f} | "
                f"Monte: {monte:7.4f}"
            )

        # Check top-n candidates for counterexamples
        TOP_N = 3
        topn = sorted(fitpop, key=lambda x: x[1], reverse=True)[:TOP_N]

        for rank, (candidate, *_scores) in enumerate(topn, start=1):

            if not self.form.is_rule_satisfiable(candidate):
                tqdm.write(
                    f" ► [{rank}] candidate is 𝗩𝗔𝗖𝗨𝗢𝗨𝗦𝗟𝗬-𝗨𝗡𝗦𝗔𝗧𝗜𝗦𝗙𝗜𝗔𝗕𝗟𝗘 (removing from population)"
                )
                self.pop = [r for r in self.pop if str(r) != str(candidate)]
                continue

            cex = self.form.find_unsound_counterexample(candidate)

            if cex is None:
                tqdm.write(
                    f" ► [{rank}] candidate is 𝗦𝗢𝗨𝗡𝗗 (appending rule into verified-solutions)"
                )
                self.verified_rules.append(candidate)
                continue

            tqdm.write(
                f" ► [{rank}] candidate is 𝗨𝗡𝗦𝗢𝗨𝗡𝗗 (appending counter-example into Σ*)"
            )
            self.Σ.append((cex, False))
            return

    def synthesise(self) -> [BooleanExpr]:
        for outer in range(self.max_rounds):
            self.round()
            if len(self.verified_rules) >= self.target_solutions:
                break
        return self.verified_rules




if __name__ == "__main__":
    form = CompleteOrderForm()
    set_symbol_universe(form.symbol_set())

    cegis = CEGIS(
        form,
        max_rounds = 250,
        starting = 100,
        generations = 100,
        elite = 5,
        target_solutions=math.inf,
    )
    rule = cegis.synthesise()
    print("\nVerified Rules:")
    for r in rule:
        print(f"- {r}")
