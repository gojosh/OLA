# Open questions

Questions that need Josh, the parish, or research. Agents: add questions here instead of guessing.

- Each question has a **permanent ID** (`Q1`, `Q2`, …). Never renumber; new questions take the next free number. Refer to them by ID elsewhere.
- When a question is answered, move it to **Answered** with the answer, who answered, and the date.

## Open

### Scope and people
- **Q2. Who decides and who approves?** Pastor, staff, parish council? Who reviews theological and liturgical content?
- **Q3. Who will maintain content after launch,** and how comfortable are they with technology? *(Drives the CMS and content-model choices.)*
- **Q4. Language:** is there a Spanish-speaking (or other) community the site should serve?
- **Q5. Timeline and budget constraints,** if any.

### Existing systems and content
- **Q8. Photography:** is there a photo archive of the church, liturgy, and people (with consent)? Is commissioning new photography possible?
- **Q9. Brand assets:** does OLA have a logo, seal, coat of arms, or established marks?
- **Q20. Analytics access:** the current site runs Google Analytics. Can we get read access? Real usage data (top pages, devices, search terms) would ground the IA.
- **Q21. On Fire Media:** what is the parish's arrangement with the current vendor? Who controls the domain and DNS, and can we get a full content export?
- **Q22. ParishSOFT:** the site links to ParishSOFT Giving for choir fees, religious-ed registration, and some ministry donations. Is ParishSOFT also the parish's records/management system? Why two giving tools (Tithely and ParishSOFT)?
- **Q23. After-hours emergencies:** the Emergency Pastoral Care page says "contact parish office," and the office is open weekdays only. Is there an after-hours route (a priest's on-call number, or an answering service)? The site can only be as good as the process behind it.

### Aesthetic
- **Q11. AI-image concepts:** does the diagnosis in `03-aesthetic.md` §1 match your sense of why they miss?
- **Q13. Place:** how much should Texas and San Antonio show in the aesthetic?
- **Q14. Eric Gill:** are his typefaces acceptable to use, given his history?
- **Q15. Generated imagery:** should "no AI-generated imagery presented as real" become a formal decision?
- **Q16. The church interior:** `explorations/interior-inspired` says its palette came from the interior (blue star-diapered ceiling, green frieze, burgundy walls, oak). Is that accurate? Photographs of the interior would be a primary source for color.

### Information architecture
- **Q17. "Gallery" in the primary nav:** what good was it meant to serve?

### Repository
- **Q18. Large files:** the Pugin plates (~258 MB) are in Git history and already on GitHub. Options: leave as is; move future large binaries to Git LFS; or migrate history to LFS (rewrites history and needs a force-push).
- **Q19. Pugin plates provenance:** they look like photographs of a physical copy. Whose copy, which edition, and are there any rights or attribution to respect?

## Answered

- **Q1. The Atonement Academy.** *Josh, 2026-10-27:* "The academy is no longer. Valor is a charter school on site, but not associated with the church." → School families are out of scope as an audience.
- **Q6. Current site.** *Josh, 2026-10-27:* https://ourladyoftheatonement.org/. Platform, vendor, and analytics found by audit: see [`research/current-site-audit.md`](research/current-site-audit.md). Analytics access is now Q20.
- **Q7. Systems in use.** *Josh, 2026-10-27:* "Tithely for giving, you can audit for anything else." The audit's findings are in [`research/current-site-audit.md`](research/current-site-audit.md) §2. Vendor arrangement is now Q21.
- **Q12. The parish name.** *From the parish's own history page (`/about-us`), 2026-10-27:* the title "originated in the Episcopal Church in the 19th century, and… was brought into the Catholic Church by the Graymoor Friars and Sisters of The Atonement in 1909." The Knights of Columbus council is named for Fr. Paul of Graymoor. → Yes.
- **Q10. `liturgical-system`.** *Josh, 2026-10-27:* "Probably just having the seasons integrated, and clean typography, and use of color."
