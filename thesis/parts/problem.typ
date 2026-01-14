= Problem Description

Formally defined in @problem-description, the Runway Sequencing Problem is to determine a feasible take-off sequence for a set of aircraft, subject to time-slot and wake constraints. In the model from @de2018pruning, the objective is to get all aircraft into the air as quickly as possible, while respecting their CTOT slots and avoiding disproportionate delay to any individual aircraft.

$
cal(P) = (
  S, space
  delta, space
  chevron.l e c, l c chevron.r, space
  chevron.l e t, l t chevron.r, space
  b, space
  c
)
$ <problem-description>

- $S$ denotes the set of all aircraft in the problem.
- $delta$ denotes a domain-complete function returning the minimum wake separation between 2 aircraft. 
- $chevron.l e c, space l c chevron.r$ denote the CTOT slot of an aircraft, i.e. $e c_i$ denotes the earliest CTOT time of aircraft $i$
- $chevron.l e t, space l t chevron.r$ denote the hard time window of an aircraft, i.e. $e t_i$ denotes the start of the time window for aircraft $i$
- $b$ denotes base-time, $b_i$ is the earliest time that aircraft $i$ can join the queue of aircraft waiting at the runway.
- $c$ denotes the minimum time to reach the start of the queue and line up with the runway. 

Assuming each aircraft will takeoff as early as possible (a valid assumption at busy airports), take-off time, denoted in @takeoff-time, is the latest of the release time or minimum wake separation takeoff (for all aircraft scheduled before $i$). Release time, @release-time, denotes the earliest (possible) time an aircraft can be sequenced. 

$
r_i = max ( 
  b_i + c_i, space
  e t_i, space
  e c_i
)
$ <release-time>

$
t_i = max (
  r_i, space
  max_(x in s_i) (t_x + delta_(x i))
)
$ <takeoff-time>

Orderings are ranked are using the multi-objective function in @objective-function. Firstly, we want to minimise _makespan_, that is the take-off time of the final aircraft in the sequence or total time to sequence all aircraft in $S$. In the second part, we consider the total delay, meaning the time-difference between an aircraft's base time and it's scheduled takeoff in the sequence, with a nonlinear scalar to promote equity. Here, we also consider costs relating to CTOT (calculated time-of-takeoff) violations, described straightforwardly in the definition of $C$.

$
F(s) = (
  max_(i in s) t_i,
  sum_(i in s)(
    W_1 (t_i - b_i)^alpha + W_2 C(t_i, l c_i)
  )
)
$ <objective-function>

$
C(t_i, l c_i) = cases(
  (0,                   t_i <= l c_i),
  (omega_1 (t_i - l c_i) + omega_2,  l c_i < t_i <= l c_i + 300),
  (omega_3 (t_i - l c_i) + omega_4,  t_i > l c_i + 300),
)
$ <ctot-function>

Additionally, @objective-function and @ctot-function include weightings which operators can tune to prioritise different parts of the objective function.  Several variables in the problem formulation reference points in time, or a period of time; formally, these are constrained as non-negative in @foundational-nonnegativity. That is, base times, queue times, CTOT-slots, time windows and wake separations are explicitly constrained to be $gt.eq 0$.

$
b_i, space
c_i, space
e t_i, space
l t_i, space
e c_i, space
e t_i
gt.eq 0, space forall i in S
quad quad
delta_(i j) gt.eq 0, space forall (i, j) in S times S
$ <foundational-nonnegativity>

#pagebreak()
= Optimal Runway Sequencing

== Bruh Momento

#pagebreak()