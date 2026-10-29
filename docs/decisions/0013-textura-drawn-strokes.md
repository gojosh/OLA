# 0013 — The textura's s drawn by hand, point by point, with the pen's angle and pressure

- **Status:** accepted
- **Date:** 2026-10-29
- **Decided by:** Josh Goforth

## Context
The s was rebuilt as one stroke of a pen that turns and presses as it goes, fitted to Pugin's letter and then to Josh's own drawing of its main stroke ([log](../log/2026-10-29-textura-s.md)). Each change of model needed a fit of many minutes, and the ends never took the shape Josh drew. Josh: "18 minutes is not reasonable." Then: "We need to take a drawing approach to the s outline, not our usual stroke representing a textura line." And: "Actually can create for me an editor, where I can define, at any point I create, the position, angle, and pressure? I'm pretty sure I can draw it myself." ([brief](../brief/2026-10-29-textura-s-drawn.md))

## Decision
Josh: "can create for me an editor, where I can define, at any point I create, the position, angle, and pressure? I'm pretty sure I can draw it myself."

- **What a drawn stroke is.** Points along the pen's path, each with where the pen is, the nib's angle and how hard it's pressed, and whether the path turns sharply there (a corner). The path runs smoothly through the points (`textura_letters.through`); the nib's angle and pressure change smoothly between them, by the length of the path. The same simulated pen as every other letter draws it (`nib.ramped_region`).
- **Where.** The proof page's pen editor (`tools/type/textura_pen.js`), on letters that can be drawn (`textura_letters.PENNABLE`; the s for now): **Draw the stroke**. Drag a point; drag the end of its nib to turn it; set any value in the list; double-click the path to add a point; Delete, C for a corner, arrows, [ ] and − = from the keyboard; undo. The letter is drawn again as the points move, over Pugin's letter and Josh's drawing, with how far the drawing lies from it.
- **How it is kept.** Save writes the points into the letter's recipe (`drawn`). Wherever a recipe has a drawing, the build, the fit and the editors draw the letter from it, not from its construction's measurements, and nothing of it is fitted. Before a drawing is saved, the editor starts from the construction: a point every 10 px along its path, and a corner where it turns sharply.

## Since
Josh, 2026-10-29: "Ok - that ended up not being useful for the s. I drew it myself, and dropped it as an SVG in the references folder." The s is now his outline (decision 0014). The pen editor stays in the code and offers no letter (`PENNABLE` is empty).

## Consequences
- The s's shape is Josh's to draw, with the pen's own idiom (the nib's width, angle and pressure) and nothing fitted. The construction and its fit stay in the code, for letters not drawn and as the starting point of a drawing.
- A drawn letter has no measurements, so its stroke editor (decision 0012) offers nothing for it; **Edit strokes** is hidden once it is drawn.
- Other letters can be made drawable by adding them to `PENNABLE` and letting their construction use their drawing, as the s's does.
- Its stems and pips are off while its shape is drawn (`PIPS`). How they are drawn when they come back, by hand or fitted to the drawn stroke, is for later.
