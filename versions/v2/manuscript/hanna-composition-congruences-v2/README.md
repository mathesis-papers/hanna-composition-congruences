# Hanna's OEIS A389474 formula (4) and linked composition identities

This note proves Paul D. Hanna's conjecture in OEIS A389474 formula (4), its
modulo-nine companion (3), and OEIS A389475 formulas (4.a) and (4.b). It includes
integral existence and rational uniqueness, the inverse-series identities and
the Catalan comparison from the posing entries. Revision 2 also proves
odd-parameter, signed and prime-degree extensions, the reversion and iteration
identities in A273095, A273320 and A274396, and prime-power congruences.
The linked prime-degree and signed integrality results are special cases of
Salerno and Silverman (2017), Theorem 4; the note credits that theorem and
gives alternative coefficient proofs. The two odd-parameter families couple
composition with the independent variable.
The prime-power congruence is a standard consequence of Pomerat and Straub
(2024), Lemma 2.1 and equation (7), with the elementary proof included.
The modulus is sharp, and a cubic coefficient of `7/2` obstructs extending
prime-degree integrality to degree four.
For a positive exponent `k`, the prime-power modulus is `p^(r+v_p(k))`.
The coverage table distinguishes these formal-series statements from numerical
real evaluations and A273095's asymptotic formula.

## Contents and building

The PDF is supplied separately; the source archive contains the LaTeX,
metadata, checking program, coefficient tables and expected checking output.

- `note.tex`: complete mathematical arguments and references.
- `note.pdf`: typeset note.
- `metadata.json`: title, creators, license, covered problems and formal source.
- `verify.py`: exact finite coefficient checks using Python 3's standard library.
- `A389474-first96.tsv`, `A389475-first96.tsv`: the first 96 terms of Hanna's
  respective OEIS tables, with their public source URLs.
- `A273095-first30.tsv`, `A273320-first30.tsv`, `A274396-first30.tsv`:
  30 terms from each linked OEIS entry, with its public source URL.
- `checker-output.json`: expected finite-check output.

Build with **Tectonic 0.17.0**:

```sh
tectonic note.tex
```

Alternatively run `pdflatex note.tex` twice. The bibliography is contained in
the source, so BibTeX and additional bibliography files are unnecessary.

Run the coefficient checks:

```sh
python3 verify.py > computed.json
diff -u checker-output.json computed.json
```

## Coverage

The proof establishes all-degree statements. The computation compares both
series with 96 OEIS coefficients, checks defining equations through degree 97,
and checks congruences through degree 96, including every nonzero power that
can occur in that degree range. Inverse identities are checked through degree
32 and the Catalan comparison through degree 96.
The extension checks compare 90 linked-entry coefficients and test both
odd-parameter families for seven parameters through degree 30, the signed
family for both signs, and the prime family for primes 2, 3, 5 and 7.
Their reversion and iteration identities are checked through degree 30.
Prime-power congruences are checked for these four primes, heights 1 to 3,
and all exponents with a nonzero contribution through degree 30, for five
series (9,610 coefficient pairs).

The pinned formal-source declarations corresponding to the two A389474
congruences are `HannaCompositionSquareModNine.FormulaFour.resultFour` and
`HannaCompositionSquareModNine.result`. The two A389475 declarations are
`HannaTripleSquareFrobeniusModThree.result` and
`HannaTripleSquareFrobeniusModThree.FormulaFourB.resultFourB`.
Their shared namespace prefix is `D5.S1.Recurrence.Invariants.`
The PDF and metadata link the exact `.lean` sources at revision
`074df09ddbbef1843ddb383577bfaa827f753e36`.
The four declarations cover the four original congruences, with normalized
rational-solution existence. The integrality and uniqueness constructions,
inverse identities, Catalan comparison and extensions have written proofs
in `note.tex`; the Python comparisons have the finite scope stated above.

## Creators and license

Haobo Ma (ChronoAI Pte Ltd, Singapore), followed by Wenlin Zhang (National
University of Singapore; ChronoAI Pte Ltd, Singapore).

CC BY 4.0, Creative Commons Attribution 4.0 International.
https://creativecommons.org/licenses/by/4.0/
