  
#set text(size: 9pt)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")
#show link: underline

#show heading.where(level: 1): it => [
  #set text(size: 12pt, weight: 700)
  #smallcaps(it)
  #v(-0.3cm)
  #line(length: 100%, stroke: 0.5pt + black)
]

#show heading.where(level: 2): it => [
  #set text(size: 9pt, weight: 700)
  #smallcaps(it)
] 

#grid(
  columns: (50%, 50%),
  [
    #text(size: 9pt)[
      _PhD Notes on Runway Sequencing_
    ]
  ],
  [
    #align(right)[
      #text(size: 9pt)[
        *Toby Benjamin Clark* #linebreak()
        psytc9\@nottingham.ac.uk
      ]
    ]
  ]
)
#v(-0.3cm)
#align(center)[
  #text(size: 18pt, weight: 500)[#smallcaps[Pruning Rules For Runway Sequencing]]
]
#v(-0.3cm)

Simply put, the Runway Scheduling Problem is to find an optimal, ordered sequence of landings and take-offs for a collection of aircraft. This is constrained by maintaining asymmetric minimum separations between aircraft (due to wake turbulence), hard time windows and minimising CTOT violations. Solving this effectively is paramount to the economic and environmental efficiency of real-world airports. It is traditionally NP-hard, making a fast optimal algorithm for the general formulation likely unattainable.

Heathrow is a particularly challenging instance of this problem, with limited runway availability and intricate ground movement dynamics contributing to increased complexity. Currently, the TSAT/DMAN system deploys a branch-and-bound approach, supplemented by a set of powerful, manually inferred pruning rules that leverage
structural features to considerably reduce the search space. Whereas heuristic approaches introduce complexity by adding meta-search layers atop the problem, pruning rules exploit key domain characteristics to simplify the problem without changing it, constituting a fundamentally new paradigm of optimization.

#include "parts/problem.typ"

#include "parts/contractors.typ"

#include "parts/why_smt.typ"

#include "parts/prunlang.typ"

#include "parts/synthesis.typ"

#bibliography("references.bib") 