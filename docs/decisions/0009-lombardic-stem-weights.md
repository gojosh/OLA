# 0009 — Two stem weights in Pugin Lombardic

- **Status:** accepted
- **Date:** 2026-10-28
- **Decided by:** Josh Goforth

## Context
The Lombardic letters are fitted to Pugin's together, sharing measured parts so that his hand-to-hand variation settles into one regular value (decision 0008). With seven letters built, fitting each alone showed that his stems are not one width plus noise but two groups. Measured at the straight, in plate pixels:
- I 79.6 and L 80.3. These letters are mostly stem.
- F 70.8, H 73.2, K 72.9 and T 74.8. These letters carry arms, a shoulder or a wide bar.

The pattern reads as optical compensation: a lighter stem where the letter already has more black elsewhere. A single shared stem (76.1 px) split the difference, making I and L lighter than Pugin drew them and the others heavier. The question was put to Josh with the measurements ([log](../log/2026-10-28-lombardic-h-k.md)).

## Decision
Josh: "Give the two groups their own stem: one for the letters that are mostly stem (I, L), one for those that carry arms, shoulders or wide bars (F, H, K, T)."

The Lombardic family has two stem measurements, each fitted across all the letters in its group:
- `stem_plain`, for letters that are mostly stem;
- `stem_armed`, for letters that carry arms, a shoulder or a wide bar.

## Consequences
- Each new letter with a stem is assigned to one of the two groups when its construction is written. Most will be `stem_armed`; a letter that is essentially a bare stem joins `stem_plain`.
- The fit keeps the regularity decision 0008 asks for (one value per group, not per letter) while keeping Pugin's evident intent.
- Round letters have no stem in this sense; their bowl weights are a separate measurement.
