
#pagebreak()
= Synthetising Pruning Conditions
Having defined the rule language and its semantic obligations, we now turn to the problem of automatically synthesising pruning conditions that satisfy these constraints. Here, we treat pruning conditions as objects of program synthesis whose soundness must hold for every instantiation of their rule-form. 

However, even under the restrictive language, the space of boolean-expressions over symbol sets is exponential in the number of symbols, depth of terms and combination of operators. Most randomly-constructed rules are semantically meaningless, vacuously unsatisfiable, or incompatiable with form constraints, making a naïve enumeration hopeless.

Moreover, valid pruning conditions must satisfy a universally quantified correctness obligation, which makes each verification query expensive and necessitates a synthesis approach that minimises such queries while still exploring a large, highly non-convex, disconnected search space.

== Counter-Example Guided Inductive Synthesis (CEGIS)
Evolutionary search depends on a graded notion of correctness; candidate programs must be rewarded for satisfying portions of their specification so that mutation has a meaningful search direction. However, universal proof is binary, and therefore intrinsically non-graded -- collapsing the fitness landscape and making incremental progression non-trivial.

CEGIS avoids this by replacing the necessity for universal proof with a growing set of finite examples extracted from the SMT-solver at each generation, @program_synthesis. Intuitively, this relies on the assumption that programs that work for $n$ examples have a higher-probability of working for $n+1$ examples, since they have likely internalised some of the specification structure.

As more counterexamples are discovered, the hypothesis space shrinks, and once no counterexample exists - the candidate program becomes universally sound, by virtue of the SMT verification. This process transforms universal constraint into a sequence of tractable problems with smoother fitness landscapes.

=== Vacuous Satisfaction & Activation Region
In the context of counterexample-driven pruning-condition synthesis, counterexamples are instances in which activation would lead to pruning the better off solution. Given this, any system implementing this alone would punish unsound activations but never reward those that are sound; by extension, the optimal behavior of a condition becomes to never activate at all.

Such rules trivially avoid penalty, but offer little in the way of pruning power. In order to combat this downwards pressure in the preorder (_towards $bot$_), the fitness function must reward those rules with a large activation region, or conditions that hold true much of the time.  It is possible to estimate the activation percentage of a pruning rule using _model counting_ - that is calculating the number of total states where some condition $beta$ holds under $Phi_F$, divided by the total number of states where $Phi_F$ holds.

Unfortunately, accurate _model counting_ is of exponential time complexity, but it is possible to quickly generate an approximation through Monte-Carlo sampling over the possible state space. This provides _upwards pressure_ (_towards_ $top$), rewarding pruning conditions that are more applicable, and promoting the ingestion of the problem structure.



== Objective Function
Candidate pruning rules are assigned a multi-objective fitness through the following function, $F(beta)$
$
F(beta) =
frac(|Sigma^*(beta)|, |Sigma^*|) +
(1 - frac(|beta|, max_(i in P) |beta_i|)) +
H(frac( cal(M) (beta), |cal(M)|))
$

$
H(p) = -p log p - (1 - p) log (1 - p)
$

In this defintion,
- $Sigma^*$ denotes the set of counterexamples, with $Sigma^*(beta) subset.eq Sigma^*$ denoting the subset where $beta$ is activated.
- $|beta|$ denotes the syntactic size of $beta$, normalised by the largest rule in the current population $P$.
- $cal(M)$ is a Monte-Carlo sample of feasible configurations, and $cal(M)(beta) subset.eq cal(M)$ the samples where $beta$ activates.

== Generalisation vs. Refinement on Mutations
- Sound pruning conditions should be able to mutate _up_ (become more general)
- Unsound pruning conditions should only be able to mutate _down_ (become more refined)

#pagebreak()
== Candidate Equivalence
Duplicate candidates within genetic populations are detrimental to search efficiency, as they reduce effective diversity without contributing new behavior. In addition to syntactically equivalent candidates, semantically equivalent candidates arise frequently, owing to the domain’s rich algebraic structure. Establishing semantic distinctness among candidates via symbolic methods is computationally expensive.

Mitigating this cost, Monte Carlo and $Sigma^*$ (counterexample set) activation signatures are used to induce an over-approximation of semantic equivalence classes: candidates assigned to different classes are guaranteed to be semantically distinct, while candidates within the same class are subjected to exact verification. Semantic equivalence is established by querying an SMT solver for a counterexample to bi-implication between candidates.