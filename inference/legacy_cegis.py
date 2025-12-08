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






# --- Helpers for CEGIS -----------------------------------------------------


def _build_delay_terms(form: CompleteOrderForm):
    """Rebuild D1, D2 as in CompleteOrderForm.verify_rule, but reusable."""
    seq1 = ["σ1", "i", "σ2", "j", "σ3"]
    seq2 = ["σ1", "j", "σ2", "i", "σ3"]
    T1 = form.compute_T(seq1)
    T2 = form.compute_T(seq2)
    D1 = form.delay_cost(T1)
    D2 = form.delay_cost(T2)
    return D1, D2


def universal_check(form: CompleteOrderForm, rule_ast: BooleanExpr):
    """
    Universal check of a rule with vacuity detection and counterexample extraction.
    Returns (is_valid, counterexample_model_or_None).
    """
    rule = rule_ast.to_z3()
    D1, D2 = _build_delay_terms(form)

    # 1. Vacuity check: ensure there exists a model where rule holds and D1 <= D2
    solver_vacuous = z3.Solver()
    for c in form.constraints:
        solver_vacuous.add(c())
    solver_vacuous.add(rule)
    solver_vacuous.add(D1 <= D2)

    if solver_vacuous.check() != z3.sat:
        # Vacuous: rule never applies in a way that gives a meaningful proof.
        return False, None

    # 2. Proof check: look for a model where rule holds and D1 > D2 (a real counterexample)
    solver_cex = z3.Solver()
    for c in form.constraints:
        solver_cex.add(c())
    solver_cex.add(rule)
    solver_cex.add(D1 > D2)

    if solver_cex.check() == z3.sat:
        model = solver_cex.model()
        return False, model

    # No counterexample and non-vacuous ⇒ universally valid
    return True, None


def satisfies_examples(rule_ast: BooleanExpr, examples, form: CompleteOrderForm) -> bool:
    """
    Check that the rule is 'good' on all stored counterexamples.
    Each counterexample model is one where constraints and D1 > D2 hold.
    For such a model m, we need rule(m) to be False so that (rule ⇒ D1 <= D2) holds.
    """
    z3_rule = rule_ast.to_z3()
    for m in examples:
        val = m.eval(z3_rule, model_completion=True)
        if z3.is_true(val):
            # Rule still fires on a known bad assignment ⇒ candidate is not acceptable.
            return False
    return True


def synthesise_for_examples(
    examples,
    seed: BooleanExpr,
    form: CompleteOrderForm,
    max_iters: int = 2000,
    reset_prob: float = 0.01,
):
    """
    Inner synthesis loop: mutate until we find a rule that

      (a) is 'good' on all stored counterexamples (satisfies_examples),
      (b) is not outright contradictory under the form constraints
          (rule_satisfiable).

    NOTE: We intentionally do *not* auto-accept the seed to avoid getting
    stuck on candidates that trivially satisfy examples (e.g. always-false
    rules such as X > X).
    """
    expr = seed

    for i in range(max_iters):
        # Random restart: start from a fresh random Boolean expression,
        # not from the (possibly bad) seed.
        if random.random() < reset_prob:
            expr = BooleanExpr.random()
        else:
            try:
                expr = mutate_one(expr)
            except Exception:
                # If mutation fails for some weird reason, skip this step.
                continue

        # Must be consistent with stored counterexamples
        if not satisfies_examples(expr, examples, form):
            continue

        # Filter out contradictory/vacuous rules like X > X
        if not rule_satisfiable(form, expr):
            continue

        # Candidate is acceptable w.r.t. examples and not obviously contradictory
        return expr

    return None

def print_counterexample_table(form: CompleteOrderForm, examples, rule_ast: BooleanExpr):
    """
    Print a detailed table of counterexamples:

      ✓ = rule is FALSE on that counterexample (good)
      ✗ = rule is TRUE  on that counterexample (bad)
    """
    if not examples:
        print("[CEGIS] No counterexamples stored yet.")
        return

    rule = rule_ast.to_z3()
    D1, D2 = _build_delay_terms(form)

    print("[CEGIS] Counterexamples (✓ = rule false, ✗ = rule true):")
    print(" idx | rule |   D1   |   D2   | D1>D2 | Values")
    print("-----+------+--------+--------+-------+--------")

    for idx, m in enumerate(examples):
        # Evaluate expressions under model
        r_val  = m.eval(rule, model_completion=True)
        d1_val = m.eval(D1,   model_completion=True)
        d2_val = m.eval(D2,   model_completion=True)
        gt_val = m.eval(D1 > D2, model_completion=True)

        # ✓/✗ mark = rule MUST be false (good)
        ok   = not z3.is_true(r_val)
        mark = "✓" if ok else "✗"

        # Stringify
        r_str  = "T" if z3.is_true(r_val) else ("F" if z3.is_false(r_val) else str(r_val))
        d1_str = str(d1_val)
        d2_str = str(d2_val)
        gt_str = "T" if z3.is_true(gt_val) else ("F" if z3.is_false(gt_val) else str(gt_val))

        # Extract complete assignments to all symbols
        vals = []
        for name in form.symbol_set():   # just the symbols in the universe
            try:
                v = m.eval(z3.Real(name) if name.startswith(("R_","B_","C_","LT_","ET_","LC_","EC_","δ")) else z3.Int(name),
                           model_completion=True)
            except:
                # fallback generic eval
                try:
                    v = m.eval(z3.Real(name), model_completion=True)
                except:
                    v = "?"
            vals.append(f"{name}={v}")

        # Print row
        print(f"{idx:4d} |  {mark}  | {d1_str:6s} | {d2_str:6s} |  {gt_str:3s}  | " + ", ".join(vals))




def rule_satisfiable(form: CompleteOrderForm, rule_ast: BooleanExpr) -> bool:
    """
    Quick check: is 'constraints ∧ rule' satisfiable at all?
    This filters out obviously contradictory rules such as X > X.
    """
    s = z3.Solver()
    for c in form.constraints:
        s.add(c())
    s.add(rule_ast.to_z3())
    return s.check() == z3.sat

# --- CEGIS loop ------------------------------------------------------------


def cegis(
    initial: BooleanExpr,
    max_rounds: int = 10,
    max_inner_iters: int = 2000,
    reset_prob: float = 0.01,
):
    """
    Counterexample-Guided Inductive Synthesis loop.

    1. Maintain a growing set of counterexamples (models).
    2. Synthesis phase: search (by mutation) for a rule that is false on all counterexamples.
    3. Verification phase: universally check the candidate.
       - If vacuous → reject and keep searching.
       - If a counterexample model exists → add it to the example set and loop.
       - If no counterexample and non-vacuous → success.
    """
    examples = []
    current = initial

    for round_idx in range(max_rounds):
        print(f"\n[CEGIS] Round {round_idx}, {len(examples)} counterexamples stored.")

        # 1. Synthesis over current example set
        candidate = synthesise_for_examples(
            examples, current, FORM, max_iters=max_inner_iters, reset_prob=reset_prob
        )

        if candidate is None:
            print("[CEGIS] Failed to find a candidate consistent with all examples.")
            return None

        print(f"[CEGIS] Candidate after synthesis: {candidate}")

        # >>> NEW: show table of counterexamples vs current candidate
        #print_counterexample_table(FORM, examples, candidate)

        # 2. Universal verification
        is_valid, cex_model = universal_check(FORM, candidate)

        if is_valid:
            print("\n[CEGIS] Universally valid, non-vacuous rule found:")
            print(candidate)
            print("\n[CEGIS] Simplified Z3 formula:")
            print(z3.simplify(candidate.to_z3()))
            return candidate

        # Not valid: vacuous or a real counterexample.
        if cex_model is None:
            # Vacuous: rule never applies meaningfully; reject and continue.
            print("[CEGIS] Candidate was vacuous; continuing search.")
            current = candidate
            continue

        # Real counterexample: store and continue.
        print("[CEGIS] Counterexample found; adding to example set and continuing.")
        examples.append(cex_model)
        current = candidate

    print("[CEGIS] No valid rule found within bounds.")
    return None



seed = Cmp(Symbol("R_i"), CmpOp.LE, Symbol("R_j"))
found = cegis(seed, max_rounds=15000, max_inner_iters=25000, reset_prob=0.01)