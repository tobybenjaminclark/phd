
= Intervals & Contractors

== Inference Rules for Intervals

#show smallcaps: set text(font: "linux libertine", weight: "bold")

$
frac(
  x in [a, b]
  quad
  y in [c, d],
  x plus y in [a plus c, b plus d]
) #smallcaps("[Add-Forward]")

quad quad quad

frac(
x in [a, b]
  quad
  y in [c, d],
  x - y in [a - d, b - c]
) #smallcaps("[Sub-Forward]")
$

$
frac(
  x in [a, b]
  quad
  y in [c, d],
  x times y in [min(a c, a d, b c, b d), max(a c, a d, b c, b d)]
) #smallcaps("[Mult-Forward]")
$

$
frac(
x in [a, b]
  quad
  y in [c, d]
  quad
  0 in.not [c, d],
  frac(x, y) in [a, b] times [frac(1, d), frac(1, c)]
) #smallcaps("[Div-Forward]")
$

#pagebreak()