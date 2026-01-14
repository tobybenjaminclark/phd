#import "@preview/simplebnf:0.1.1": *

= Ruleforms
Let $FF$ denote the set of _rule-forms_, which act as as syntactic templates describing the structure in which a pruning rule operates. Forms define the activation environment in which conditions to prune search branches can arise, the symbols a pruning condition of that form can reference/include (detailed later in @symbol-sets) and some post-condition function $cal(A)$.
$
F := chevron.l
  cal(X), space
  Phi_F (sigma), space
  cal(A) (sigma)
  chevron.r
  quad
  forall F in FF
$
- $cal(X)$ denotes the set of variable bundles, where each element $sigma in cal(X)$ contains a full valuation of all variables.
- $Phi_F (sigma)$ denotes the _dependent conjunction of all feasibility constraints_ on some state $sigma in cal(X)$.
- $cal(A)(sigma)$ denotes the _acceptance function_, for some pruning condition $beta: cal(X) arrow BB$. 

One example is the _complete order form_, which states that under some precondition $R$, sequencing aircraft $i$ before $j$ in an arbitary sequence can never yield a higher objective cost than the swapped ordering $j prec i$. Explicitly, _complete order form_ defines two arbitrary sequences ($S, S'$) where $i prec j$ and $j prec i$, with a post-condition necessitating: $F(S) lt.eq F(S')$. Inside of this form, any _sound pruning condition_, would necessitate that $F(S) lt.eq F(S prime)$.

= Pruning Condition Syntax
Pruning conditions are expressed in the language defined in @pruning-language.
Syntactic typing is enforced by an ordered, multi-sorted grammar, ensuring that every well-formed rule denotes a Boolean expression: true when the rule holds and false otherwise. @pruning-language describes pruning conditions in their canonical form, without syntactic-sugaring.

#figure(
  kind: "Grammar",
  supplement: "Grammar",
  caption: [Correct by Construction Language for Pruning Rules],
  bnf(
    Prod(
      $beta$,
      annot: [Boolean Term],
      {
        Or[$beta and beta$][_Conjunction_]
        Or[$beta or beta$][_Disjunction_]
        Or[$not beta$][_Negation_]
        Or[$alpha space rho space alpha$][_Comparison_ #v(8pt)]
      },
    ),

    Prod(
      $alpha$,
      annot: [Arithmetic Expression],
      {
        Or[$alpha plus.o alpha_t$][_Additive Expression_]
        Or[$alpha_t$][_Arithmetic Term_ #v(8pt)]
      }
    ),
    
    Prod(
      $alpha_t$,
      annot: [Arithmetic Term],
      {
        Or[$alpha_t times.o alpha_f$][_Multiplicative Expression_]
        Or[$alpha_f$][_Arithmetic Factor_ #v(8pt)]
      }
    ),

    Prod(
      $alpha_f$,
      annot: [Arithmetic Factor],
      {
        Or[$ZZ$][_Numerical_]
        Or[$SS(F)$][_Symbol_]
        Or[$( alpha )$][_Arithmetic Expression_ #v(8pt)]
      }
    ),

    Prod(
      $rho$,
      annot: [Comparison Operator],
      {
        Or[$gt$][_Greater Than_]
        Or[$lt$][_Less Than_]
        Or[$eq$][_Equality_]
        Or[$gt.eq$][_Greater Than or Equal To_]
        Or[$lt.eq$][_Less Than or Equal To_ #v(8pt)]
      },
    ),

    Prod(
      $plus.o$,
      annot: [Additive Expression],
      {
        Or[$plus$][_Addition_]
        Or[$minus$][_Subtraction_ #v(8pt)]
      },
    ),

    Prod(
      $times.o$,
      annot: [Multiplicative Expression],
      {
        Or[$times$][_Multiplication_]
        Or[$div$][_Division_ #v(8pt)]
      },
    ),
  )
)<pruning-language>

== Symbol Sets <symbol-sets>
Introduced in @pruning-language, is a symbol-set operator $SS$, which assigns to each _rule form_ $F in FF$ a set of admissible symbols. Rules may reference only symbols contained in their symbol-sets; references to symbols outside $SS(F)$ are ill-formed. The collection $SS(F)$ is therefore an indexed family of symbol-sets (over index $FF$), or $F in FF, space F tack SS(F)$. The symbol set for a given form, or $SS(F)$, is defined as the least set of symbols satisfying the following closures#footnote[We assume that $sans("AC"): FF arrow S$ is a function extracting the set of aircraft placeholders appearing syntactically in a given rule-form, that is for every $F in FF$, $sans("AC")(F) = { a divides a "is an individual aircraft variable bound in form" F}$.]:

- All _functional attributes_ lifted over _all aircraft_, or $f_p in SS(F), space forall f in {r,c,b,e t, l t, e c, l c, t, t'}, space forall_p in sans("AC")(F)$
- All _wake separation_ pairings over _all aircraft_, or $delta_(i j) space forall chevron.l i, j chevron.r in sans("AC")(F) times sans("AC")(F)$

Intuitively, these rules enforce that a pruning rule may only reference relevant symbols in its form definition. Aircraft variables themselves are explicitly excluded from symbol sets $a in.not SS(F), space forall a in sans("AC")(F)$, since these denote arbitary, unique identifiers with no semantic relevance beyond indexing functional attributes (such as _release times_).

#pagebreak()

= Pruning Condition Semantics & Validity
We formally specify the semantic obligations (_sound_ and _applicable_) that a _condition_, _rule-form_ pair must meet to be considered _valid_ within the restrictive pruning framework. These conditions are provided under the context of an SMT-based verification methodology.

== Condition Soundness
Some pruning rule $beta$ is _sound_ for form $F$ if whenever the rule is triggered in a feasible configuration, the dominance relation (post-condition) necessitated by the form always holds. That is, for every configuration $sigma in cal(X)$, that is feasible under the form constraints $Phi_F (sigma)$ and satisfies the pruning condition $beta(sigma)$, the dominance post-condition required by the form must hold; equivalently the acceptance predicate $cal(A)(sigma)$ must hold true, @eq:pruning-condition-soundness.

$
forall sigma in cal(X),
(Phi_F (sigma) and beta(sigma) arrow.double.long cal(A) (sigma))
$ <eq:pruning-condition-soundness>

== Vacuously Unsatisfiable / Min-Applicability
Consider $delta_(i j) eq.not delta_(i j)$ as a candidate condition, it is syntactically well-formed, and reduces to a boolean yet semantically it is vacuously false. However, under a naïve SMT-interpretation of pruning rule validity-- to be _unsatisfiable_ is to be _verified_, yet this is not; consequently we must additionally rule out vacuous predicates whose truth set is empty.

This is relevant, because if the sole priority is the context-blind pursuit of unsatisfiability, it's far easier to construct a vacuously false case than an effective pruning rule. To eliminate these common cases, we must obtain a witness of applicability, that is an example that the rule can hold true in a feasible scenario. That is, we must verify the _domain_ of the pruning condition to be non-empty within the form constraints, @eq:pruning-condition-vacuously-unsatisfiable.

$
exists sigma in cal(X),
(Phi_F (sigma) and beta(sigma))
$ <eq:pruning-condition-vacuously-unsatisfiable>

== Condition Completeness (Non-Requisite)
Pruning conditions are _complete_ within their form if they trigger for all feasible configurations in which the dominance post-condition is true, thereby capturing the full domain where pruning would be correct, @eq:pruning-condition-complete. However, for a _pruning rule_ to be valid, it is not necessary to be _complete_, as the objective is merely to discard some dominated configurations, as opposed to characterising the entire dominance region within the search space.

$
forall sigma in cal(X), space
(Phi_F (sigma) and cal(A)(sigma) arrow.double.long beta(sigma))
$ <eq:pruning-condition-complete>

== Condition Non-Redundancy
Pruning conditions can be considered _non-redundant_ if they are not logically implied by existing problem constraints or pre-defined pruning rules; that is, there exists a feasible configuration $sigma$, where candidate rule $beta prime$ holds at least one existing rule $beta$ does not. _Non-redundancy_ is desirable for efficacy but not necessary for a rule to be valid.

$
forall beta in beta^*, space
exists sigma in cal(X), space 
(Phi_F (sigma) and beta prime (sigma) and not beta (sigma))
$<eq:pruning-non-redundancy>

== Condition Applicability (Exact and Approximate)
Condition applicability quantifies how often a pruning condition $beta$ activates over feasible configurations within its rule form $F$. Computing this fraction exactly (see $p_F$) requires model counting, which is computationally intractable in general and may be undefined when the state space is infinite/enumerable.

We approximate applicability using Monte Carlo sampling, drawing configurations independently from a uniform product distribution over bounded variable domains. Specifically, $hat(p)_F^((n))$ is defined as a Monte Carlo proxy of $p_F$ obtained by evaluating $beta$ on sample configurations of $cal(X)$ and computing the empirical activations as a fraction of the feasible samples.

$
p_F (beta) = frac(
  sum_(sigma in cal(X)) 1[Phi_F (sigma) and beta(sigma)],
  sum_(sigma in cal(X)) 1[Phi_F (sigma)] 
)

quad quad quad quad

hat(p)_F^((n))(beta) = frac(
  sum^n_(k=1) 1[Phi_F (sigma_k) and beta(sigma_k)],
  sum^n_(k=1) 1[Phi_F (sigma_k)] 
), quad sigma_1 dots sigma_n tilde cal(X)
$<eq:pruning-applicability>

Applicability induces an extensional preorder over pruning conditions under form $F$, ordered by frequency of activation, with $top$ denoting conditions that apply on all feasible configurations and $bot$ denoting conditions that never activate. Formally, this preorder can be logically defined as: $beta_1 prec.eq_p_F beta_2 arrow.double.l.r.long_("def") p_F (beta_1) lt.eq p_F (beta_2)$.


== Condition Equivalence and Form-Equivalence
Logical equivalence between two pruning conditions can be established by proving their bi-implication, however; two conditions $beta$, $beta prime$ can be considered equivalent under their _form_ $F$, if for all feasible configurations in $cal(X)$, their bi-implication holds, i.e. they only differ semantically outside of the feasible region. Whilst weaker than traditional equivalence, form-equivalence ignores irrelevant distinctions outside the form constraints. 

$
beta =_F beta prime quad arrow.long.double.l.r^("def") quad forall sigma in cal(X), space (Phi_F (sigma) arrow.long.double (beta(sigma) arrow.long.double.l.r beta prime (sigma)))
$<eq:pruining-equivalence>

#pagebreak()

= Algebraic Structure of Pruning Conditions
Having defined the syntax and semantic validity of pruning conditions, we now characterise the algebraic structure they induce under semantic implication. This structure formalises notions of strengthening and weakening, and explains the monotonic propagation of soundness as well as its role in guiding automated pruning-condition synthesis.

== Strengthening and Weakening
Let $beta, beta prime : cal(X) arrow BB$ be pruning conditions of rule-form $F$. It is said that $beta$ _strengthens_ (or _refines_) $beta prime$, if for all feasible configurations, $sigma$, in $cal(X)$, it holds that $beta(sigma) arrow.double beta prime(sigma)$. Dually, $beta prime$ _weakens_ (or _generalizes_) $beta $ if for all feasible configurations, $sigma$, $beta prime(sigma) arrow.double beta (sigma)$. Intuitively, if some pruning condition $beta$ is stronger than another condition, $beta prime$, then $beta$ applies/activates over less configurations in $cal(X)$ and vice versa. 

$
beta space & italic("strengthens") & space & beta prime & space quad & "iff" &  space quad forall sigma in cal(X), space (Phi_F (sigma) arrow.double.long (beta(sigma) arrow.long.double beta prime (sigma))) \
beta space & italic("weakens") & space & beta prime&  space & "iff" & space quad forall sigma in cal(X), space (Phi_F (sigma) arrow.double.long (beta prime(sigma) arrow.long.double beta (sigma)))
$

Strengthening induces a preorder over valid pruning conditions, since logical implication is reflexive and transitive but antisymmetry holds only up to semantic equivalence. We introduce this structure here primarily to reason about dominance; its fuller algorithmic significance becomes apparent when the preorder is later lifted to a lattice.

Within this preorder, soundness properties propagate monotonically. Importantly, _unsoundness_ is monotone in respect to weakening, if a pruning condition $beta$ is _unsound_, then any weakening of $beta$ is also unsound, since it applies to a superset of configurations. Dually, _soundness_ is monotone to strengthening, if $beta$ is sound, then any strengthening of $beta$ is also sound, since it applies within a subset of sound configurations.

== Lindenbaum-Tarski Algebra & Quotienting
Whilst _strengthening/weakening_ alone induces a preorder defined by semantic implication, it is not antisymmetric: syntactically distinct pruning conditions may be semantically equivalent. To obtain a genuine partial order - and to reason algebraically about the space of pruning conditions rather than individual syntactic representations, the set of pruning conditions is quotiented by semantic equivalence/bi-implication.

The resulting quotient structure is the Lindenbaum-Tarski algebra; its elements are equivalence classes of pruning conditions, ordered by entailment, with conjunction and disjunction inducing meet and join operations. This algebraic view makes the search regions eliminated by unsoundness-weakening monotonicity precise as upward and downward closures in the induced lattice #footnote[Partially ordered sets are termed _lattices_ when every pair of elements admits both a greatest lower bound (meet) and a least upper bound (join), which in the present setting correspond to conjunction, $and$, and disjunction, $or$, respectively.]. Formally, $[beta] lt.eq [beta prime] "iff" beta prime tack.double beta$ for all feasible $sigma$ in $cal(X)$.

@lindenbaum-tarski-lattice depicts a finite sublattice of the infinite Lindenbaum-Tarski lattice, where $[beta]$ nodes denote equivalence classes of pruning conditions ordered by semantic entailment; vertical position corresponds to weakening/strengthening, while horizontal placement is purely for layout. Here, subscript indicies denote relative lattice depth with respect to reference element $[beta_0]$; primes distinguish incomparable elements at the same lattice level, but convey no semantic meaning.

#figure(caption: [Lindenbaum-Tarski Lattice of Pruning Conditions])[
#image("../assets/lindenbaum-tarski-lattice.png", width: 8.3cm)
]<lindenbaum-tarski-lattice>

== Monotonicity of Soundness
@lindenbaum-tarski-unsound depicts the monotonic propagation of unsoundness under weakening; if an equivalence class of pruning conditions $[beta_0]$ is proven unsound, then any weakening $[beta_0^(arrow.b)]$ is also unsound. The shaded region therefore denotes the upward closure of $[beta_0]$, which can be discarded from consideration once a single feasible counterexample is identified.

Dually, @lindenbaum-tarski-sound illustrates that soundness is monotone under strengthening: if $[beta_0]$ is sound, then every $[beta_n] lt.eq [beta_0]$ is sound. The shaded region denotes the downward closure of $[beta_0]$, certifying all refinements $[beta_0^arrow.t]$ without additional proof. Once a pruning condition is proven sound, further _strengthening_ does not increase correctness, only restricts applicability.

#grid(
  columns: 2,
  gutter: 1em,
  [
    #figure(
        caption: [Unsoundness Monotonicity Closure],
      )[
      #image("../assets/lindenbaum-tarski-unsound.png", width: 95%)
    ]<lindenbaum-tarski-unsound>],
  [
    #figure(
        caption: [Soundness Monotonicity Closure],
      )[
      #image("../assets/lindenbaum-tarski-sound.png", width: 95%)
    ]<lindenbaum-tarski-sound>],
)

Under a naïve synthesis procedure, a singular counterexample refutes a singular candidate condition; however, under the lattice interpretation, all weakenings of the condition are refuted, since they apply to a superset of configurations that include the violating instance. Consequently, synthesis methodologies are able to prune the entire upward closure of that condition in the lattice, which typically contains an exponentially large family of syntactically distinct candidates.

Operationally, synthesis seeks pruning conditions of maximal applicability subject to soundness. Accordingly, once a condition is established as sound, it is natural to consider its successive weakenings, generalising until a fixed point is reached beyond which soundness no longer holds, containing the maximal sound element in that subregion.