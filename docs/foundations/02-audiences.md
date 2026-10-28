---
title: Audiences
status: draft
updated: 2026-10-27
---

# Audiences

## What Josh has said

- **Catholic inquirers**: "is this a Parish I would like to visit or join?"
- **Inquirers** (non-Catholic and non-Christian): "what is this place?"
- **Parishioners**: "this is an important resource for my parish life"
  - **Church ministries / leadership**: "this is where we record things and organize"
- A possible **"remembered" state** that "recognizes returning parishioners, and tailors their experience for members."
- Josh asked for advice on this breakdown and for groups he may not be thinking about.

Source: [`docs/brief/2026-10-27-kickoff.md`](../brief/2026-10-27-kickoff.md)

---

## Working proposals

### A. Assessment of the breakdown

Organizing by **relationship to the parish** (stranger → inquirer → member → servant) is right, and it maps naturally onto a "remembered" state. Two refinements:

1. **Also segment by mode, not only by identity.** The same person changes mode. A parishioner arranging a parent's funeral is not browsing parish life; they're in a high-stakes, task-driven moment. A curious inquirer and a traveler who needs Mass in two hours are both "outsiders," but they need opposite things. So there are two axes:
   - **Relationship:** how close the person is to the parish.
   - **Mode:** *discerning* (exploring, unhurried, open to beauty and depth) or *tasking* (needs one fact or action, now, often on a phone).
2. **Use audiences to test the IA, not to label the navigation.** Most real needs cut across audiences (everyone needs Mass times). The navigation should be built around needs; audiences are the lenses we use to check that every group can find its way.

### B. Groups to add

In rough order of importance:

| Group | Why they matter | Key question |
|---|---|---|
| **Christian seekers drawn to the Ordinariate:** Anglicans, Episcopalians, other Protestants | The reason the Ordinariate exists. They're Christian, often liturgically literate, often know the Prayer Book. They're neither "Catholic inquirers" nor "what is this place?" inquirers. This may be OLA's most distinctive audience. | "Can I come into full communion and bring my patrimony with me?" |
| **People at a threshold:** baptism, marriage, funeral, anointing/emergency, OCIA | The highest-stakes visits, often emotionally loaded, and frequently from people who are *not* parishioners. In the medieval English parish these things began *at the church porch*. | "What do I do, who do I call, what will it be like?" |
| **Travelers and one-time visitors** | Probably the most common single task on any parish site: Mass today, address, parking. Mobile and urgent. | "When is the next Mass, and how do I get there?" |
| **Returning Catholics** | Differ from inquirers: they carry history, sometimes hurt. Confession times and an honest welcome matter more than an explanation of the faith. | "Would I be welcome back?" |
| **Pilgrims and admirers (the wider Church)** | OLA's liturgy, music, and Ordinariate story draw interest far beyond San Antonio ⚑ verify. These people watch, share, visit once, sometimes give. They help the parish's mission even though they'll never register. | "What is the liturgy like there, and can I see it?" |
| **The people who run the site:** clergy and staff as editors | If updating Mass times needs a developer, the site rots, and then it fails every other audience. Their workflow is a design requirement, not an afterthought. | "Can I change this in two minutes, correctly?" |
| **Machines:** search engines, maps, AI assistants, Mass-time directories, calendar apps, screen readers | More and more, people find Mass times by asking Google, Apple Maps, or an AI assistant, which read structured data and never see the design. Screen readers depend on the same structure. | (Needs: accurate structured data, feeds, clean semantics) |
| **School families:** The Atonement Academy ⚑ verify scope | If the Academy is part of the parish's web presence, current and prospective school families are a large audience in their own right, and many may not be parishioners. | ⚑ Josh: is the Academy in scope? |

**Cross-cutting needs** (not audiences, but constraints on every audience): older eyes and low tech confidence; mobile first; slow connections; possibly language ⚑ Josh (is there a Spanish-speaking community to serve?).

### C. A spatial model: from the churchyard to the altar

The medieval English parish church already arranged people by relationship to the community. That layout gives a native, Gothic logic for how deep each audience goes, and for what a "remembered" state unlocks:

| Place | Who | What the site offers there |
|---|---|---|
| **Churchyard and lychgate** | Everyone, including machines | Where, when, what: the public facts, perfectly structured |
| **Porch** | Inquirers, seekers, people at a threshold | Welcome, explanation, first contact. In medieval England baptism began and marriages were made "at the church door." The porch is where thresholds happen. |
| **Nave** | Parishioners | Parish life: bulletin, events, formation, giving |
| **Chancel and choir** (beyond the rood screen) | Those who serve | Tools for organizing: schedules, rosters, coordination |
| **Sanctuary** | — | The liturgy itself: at the center of everything, and **visible to all** |

The point of the rood screen was that it was **pierced**: everyone in the nave could see the altar. The same should hold here. Remembering someone changes how deep their tools go, never their access to the heart of the place. The Mass, the day's feast, and the life of prayer are public and central for every audience.

### D. The "remembered" state: recommendation

Split it into three tiers, because they carry very different costs and risks:

1. **Device memory, no login (recommended).** "I'm a parishioner" (opt-in), my usual Mass, ministries I follow, text size, maybe language. Stored on the device only. The site reorders itself: my Mass first, this week's bulletin, my ministry's next date. Low risk, high value, and it works on day one.
2. **Light identity (maybe).** Sign-ups, RSVPs, volunteer slots, subscriptions. Often better delegated to a tool the parish already uses ⚑ Josh (which systems exist today?).
3. **Authenticated member and ministry area (only with a clear case).** Rosters, records, directories. This means real security, data-protection obligations, safe-environment rules wherever minors are involved, and ongoing staff burden. The parish almost certainly has, or should have, a parish-management system for records. The website should **integrate** with it, not rebuild it.

**Rules for any remembered state:**
- Personalization **reorders and shortcuts; it never hides.** The public site is complete on its own.
- It is visible and reversible ("You're seeing the parishioner view · change").
- It is honest. No dark patterns, no tracking beyond what serves the person.
- Directory-style content about parishioners (e.g. the business directory) needs explicit consent from those listed.

### E. Draft: top needs by audience

Starting material for the IA session. To be validated with real people.

| Audience | Mode | Top needs |
|---|---|---|
| Curious non-Christian | Discerning | What is this place? What happens inside? Can I just come and look? What would I see? |
| Christian seeker (Ordinariate) | Discerning | What is the Ordinariate? What's kept from the Anglican tradition? How does reception work? Who do I talk to? |
| Catholic considering OLA | Discerning | What's the liturgy like? Is there community for people like me (families, young adults)? How do I register? |
| Returning Catholic | Discerning → task | Confession times. Would I be welcome? Who can I talk to quietly? |
| Traveler | Task | Next Mass, address, parking, what to expect (it's Divine Worship, not the usual Roman Missal) |
| Person at a threshold | Task, high stakes | Emergency contact. Funeral, wedding, baptism: steps, people, timelines |
| Pilgrim / admirer | Discerning | Livestream, music, the building, the story, how to support |
| Parishioner | Task, recurring | This week: Masses, bulletin, events, changes. Giving. Formation. |
| Those who serve | Task, recurring | Schedules, rosters, communication, resources |
| Editors (clergy, staff) | Task, recurring | Update times, post the bulletin, add events, publish notices: fast and safely |
| Machines | — | Structured data (schema.org), calendar feeds (ICS), accurate titles, clean semantics |
