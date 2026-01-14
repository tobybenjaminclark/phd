
= SMT
Runway Sequencing consists of integer and real arithmetic, piecewise-linear constraints, max operators, polynomial functions, and finite sets of symbolic aircraft; consequently, verification of pruning rules sits in quantifier-free non-linear real arithmetic (QF_NRA). Currently, each pruning rule has been proved using pen-and-paper, which is difficult to reliably construct and impossible to automate, @de2018pruning.

Pruning rules in @de2018pruning are expressed as universally quantified statements over all combinations of sequences of aircraft, subject to some precondition. Even if all parameters are artificially restricted to finite ranges, a brute-force enumeration to verify a rule still suffers from combinatorial explosion; the number of possible instances and orderings increases super-exponentially with the number of aircraft. This makes exhaustive verification computationally infeasible beyond very small toy problems, therefore unsuitable to verify in real-world cases.

Given the high-impact, safety critical problem domain, establishing formal correctness is necessary; holding statistical confidence that a rule holds simply isn’t enough. As a result, sampling-based simulation/fuzz testing is inadequate for the verification of pruning rules, since such methodologies only prove the presence of counterexamples, not their absence @dijkstra2022reliability.

Establishing this formal correctness necessitates the symbolic quantification over both ℝ and ℤ; thus any approach utilizing integer programming techniques can not faithfully encode the problem. However, integer programming techniques could be utilized for the operational validation of pruning rules, but are unsuitable for universal, mathematical proof in the general case.

Recreating the problem and pruning rules in a higher-order logic or dependently typed programing language and proving interactively could guarantee formal correctness and produce a set of extremely strong, foundational proofs. However, similar to pen-and-paper, this requires strong user-guidance and singular proofs are often hundreds of lines. There are limited methodologies in the automated synthesis of proofs under this methodology.

On the other hand, SMT supports symbolic parameters over ℤ and ℝ, reasons exactly over max, conditional logic and piecewise-linear penalties. It can provably negate the existence of a counterexample, or provide (useful) concrete counterexamples if one exists. Moreover, the methodology runs automatically, without the need for weeks of specialist, theorem-prover development. One could place it as a Goldilocks methodology, sitting between operational verification in IP and the full, mathematical rigour of a theorem proving system such as HOL or Lean4.

However, there are limitations: proofs in SMT are large, difficult to inspect and not directly interpretable by humans. Thus, the trust chain depends on the correctness of the solver, correctness of the theory solver, and absence of internal bugs. The methodology should be combined with independent solver cross-checks, or even certificate verification in a stronger logic such as HOL in some cases (not non-linear real arithmetic).

== Is it proof?
Some would argue that Mathematics requires transparent deductive reasoning; whereas SMT provides opaque algorithmic answers.

#pagebreak()