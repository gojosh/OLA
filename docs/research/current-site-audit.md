---
title: Current site audit — ourladyoftheatonement.org
status: draft
updated: 2026-10-27
---

# Current site audit: ourladyoftheatonement.org

Audited 2026-10-27 by an agent: a polite crawl (robots.txt respected, 10 s between requests) of the sitemap plus every same-site link found, and a look at the live pages in a browser. Facts quoted below are **as published on the current site on that date**. They may be stale; ⚑ verify with the parish before reusing any of them.

A full-text snapshot was deliberately **not** committed: many pages carry volunteer names and contact details (AGENTS.md §4.8). Re-fetch a page if you need its full text.

## 1. Summary

1. **The platform is end-of-life.** The site runs on On Fire Media's hosted Drupal 7 platform; Drupal 7 stopped receiving community security support in January 2025.
2. **Some content is stale in ways that matter.**
   - The home page FAQ says the parish is "in union with Pope Francis." Pope Leo XIV was elected in May 2025.
   - The footer "Holidays" link goes to a **2025** closures PDF.
   - A banner says parts of the site are "Under construction."
   - A booster-club page for the Academy is still live, though the school closed in June 2024.
3. **The most urgent page is the weakest.** Emergency Pastoral Care says "contact parish office," and gives no after-hours route; the office is open weekdays only ⚑ verify whether the office line forwards after hours.
4. **The main visitor page is empty.** "Join Us" has about 10 words. The good inquirer content (the home page FAQ, *The Ordinariate*, *Becoming Catholic*, *Coming Back to the Church*) exists but is scattered.
5. **Some public links lead to a login page.** The footer's Parishioner Business Directory isn't members-only; it's an **unpublished** page, still linked from every page's footer and the About menu. An old, unpublished Becoming Catholic page does the same.
6. **The real menu is about 70 links,** not 19. Ministries alone account for 28.
7. **Content governance is the underlying problem.** Of 83 unique pages, 22 aren't linked from the menus or the home page, 12 are nearly empty, and 45 haven't been updated since before 2024. Schedules are retyped on several pages and already disagree in small ways.
8. **The parish already uses a stack of outside services:** Tithely, ParishSOFT, Flocknote, LPi, Universalis, Formed, Google Forms, YouTube, Vimeo. The new site should hand off to these well rather than replace them.
9. **There's a good base to build on.** A real history page, an Ordinariate explainer, a Universalis feed already set to the Ordinariate calendar, a motto ("Worship the LORD in the beauty of holiness"), and ministries with English patron saints (St. Cuthbert, St. George, St. Stephen).

## 2. Platform and systems

| System | Role | Evidence | Notes |
|---|---|---|---|
| **On Fire Media** (hosted Drupal 7 platform) | The website: CMS, hosting, theme | `generator` meta tag; `/profiles/hosted/`, `/sites/atonement/`, Bootstrap 3 theme | **Drupal 7 reached end of life in January 2025.** The platform no longer gets community security updates, which is a strong practical reason for the rebuild. Vendor arrangement and content export: Q21. |
| **Cloudflare** | CDN / proxy in front of the site | `/cdn-cgi/` scripts, email obfuscation | Who controls the Cloudflare account and DNS: Q21. |
| **Tithely** | Online giving | `give.tithe.ly` form embedded on `/donations-gifts` | Confirmed by Josh. |
| **ParishSOFT** (Giving) | Program fees and registrations; some ministry donations | `giving.parishsoft.com` links on Choirs (choir fee), Children's Religious Education (registration form), God's Comfort in Loss (donate) | A second giving tool alongside Tithely. ParishSOFT is also a parish-management suite. **Is it the parish's records system?** Q22. |
| **Google Forms / Docs** | Interest forms, schedules | Young Adults interest form; miscarriage-ministry care-box request; altar server schedule (Google Doc) | Ad hoc. Candidates for proper forms or the remembered state. |
| **Flocknote** | Email/text updates to parishioners | Sign-up form on home page and bulletin page (`app.flocknote.com`) | Likely the parish's main broadcast channel. |
| **LPi / Parishes Online** | Weekly bulletin publishing | `parishesonline.com` bulletin widget on `/about-us/sunday-bulletin` | LPi bulletins are typically ad-supported ⚑ verify. A data source the new site can embed or link. |
| **Universalis** | Daily Mass readings, Ordinariate calendar | Home page "Today's Mass Readings" block (`Universalis_*` element IDs) | Showed "Tuesday after the Twenty-first Sunday after Trinity." See `foundations/04-technology.md` §4. |
| **Formed** | Catholic formation streaming (Augustine Institute) | Utility-nav link to formed.org | External subscription; link out. |
| **Google Analytics 4** | Usage analytics | Tag `G-TNJJSDCJLW` | Access requested: Q20. |
| **YouTube** | Video channel; Mass recordings | Social link; Holy Mass page: "Watch Recordings of Holy Mass on YouTube" | Livestream vs. recordings only ⚑ verify. |
| **Vimeo** | Background video on home page | Embedded player | |
| **Facebook** | Social page | `facebook.com/OLAtonement` | |

Not found on the site: online event registration, a livestream page, calendar feeds (ICS), or structured data for Mass times. Events are listed by Drupal's own calendar.

## 3. Navigation as built

Josh's count of 19 covered the top level. Counting every link in the menus, the site has **about 70 navigation links**:

- **Utility bar (7):** Home · Emergency Pastoral Care · Sunday Bulletin · Formed · Donations & Gifts · Join Us · Events
- **Main menu (8 top-level, ~54 beneath):**
  - **Liturgy:** Holy Mass · Confessions · Daily Office
  - **Sacraments:** Baptism · Confirmation · First Holy Communion · Confession · Holy Matrimony · Anointing of the Sick
  - **Ministries**
    - *Liturgical (9):* Altar Guild · Altar Servers & Ushers · Greeters & Ushers · Altar Server Resources · Music · Choirs · Music Series · Organs · Sacraments for the Homebound
    - *Outreach (19):* Adoration · Atonement Young Adult Group · Bereavement · CYO · Culture of Life · God's Comfort Miscarriage Ministry · Home Visitation (St. Cuthbert) · Knights of Columbus (Fr. Paul of Graymoor Council 16730) · Men's Prayer Group (St. Joseph the Worker) · Moms Group · Newcomers · Pastoral Council · Prayer Ministry · Rosary Guild · Troops of St. George (Troop 815) · Women of Grace · St. Vincent de Paul · Women at the Well · Youth Group
  - **Education:** Adult Catechism Course · Children's Religious Education · Adult Education Resources
  - **Why Catholic:** Why Catholic · What is Salvation? · Who is Jesus? · Coming Back to the Church
  - **About Us:** Calendar · Careers · Emergency Pastoral Care · Join Us · Our Staff · Parish Business Directory · Parish History · Photo Album · Sunday Bulletin · Safe Environment
  - **Giving**
  - **Becoming Catholic**
- **Footer:** Holidays (a PDF) · Sunday Bulletin · Parishioner Business Directory; address, phone, office hours; social links.

**Structural problems in the current menus:**
- The **Sacraments** top-level link points to the home page.
- **Confession** appears twice (under Liturgy and under Sacraments) with different URLs; **Emergency Pastoral Care** and **Join Us** also appear twice.
- **Adoration** (a devotion) and **Pastoral Council** (governance) are filed under *Outreach Ministries*.
- "Altar Servers & Ushers" links to a page about altar servers *and greeters*, alongside a separate "Greeters & Ushers" page.
- The home page "Mass Times" heading links to `/sacraments/sacrament-eucharist`, a page that isn't in the menus at all.

## 4. Content inventory

83 unique pages (login, search, calendar-date variants, and off-site redirects excluded). "Updated" is the sitemap's last-modified date. "Not in nav" means not linked from the menus or the home page (they may still be linked from other pages).

| Section | Page | Path | Updated | Words | Notes |
|---|---|---|---|---:|---|
| (home) | Worship the LORD in the beauty of holiness | `/` |  | 369 | FAQ says "in union with Pope Francis" |
| about-us | About Us | `/about-us` | 2026-10-19 | 636 |  |
| about-us | Calendar | `/about-us/calendar` | 2022-11-02 | 77 | dynamic event listing; duplicate of `calendar-0`; not in nav; not updated since 2022 |
| about-us | Calendar | `/about-us/calendar-0` | 2022-11-02 | 77 | dynamic event listing; not updated since 2022 |
| about-us | Careers | `/about-us/careers` | 2024-09-05 | 28 | thin |
| about-us | Emergency Pastoral Care | `/about-us/emergency-pastoral-care` | 2025-11-02 | 71 | no after-hours number given |
| about-us | Join Us | `/about-us/join-us` | 2026-10-06 | 10 | the main visitor page, nearly empty; thin |
| about-us | Sunday Bulletin | `/about-us/sunday-bulletin` | 2022-12-19 | 16 | LPi bulletin widget (bulletin itself is current); thin; not updated since 2022 |
| adoration | Adoration of the Most Blessed Sacrament | `/adoration` | 2024-12-03 | 934 |  |
| altar-server-training | Altar Server Training | `/altar-server-training` | 2021-07-28 | 102 | not in nav; not updated since 2021 |
| becoming-catholic | Becoming Catholic | `/becoming-catholic` | 2026-05-23 | 211 |  |
| calendar | Liturgy | `/calendar/categories/liturgy` |  | 98 | not in nav |
| donations-gifts | Donations & Gifts | `/donations-gifts` | 2026-04-11 | 0 | Tithely embed only; thin |
| education | Adult Catechism Course | `/education/adult-catechism-course` | 2026-05-23 | 272 |  |
| education | Adult Education Resources | `/education/adult-education-resources` | 2023-02-17 | 393 | not updated since 2023 |
| education | Children's Religious Education | `/education/childrens-religious-education` | 2025-09-04 | 30 | thin |
| education | Educating on Nature & Dignity of Women (ENDOW) | `/education/educating-nature-dignity-women-endow` | 2023-02-17 | 196 | not in nav; not updated since 2023 |
| education | Our Lady's Lambies | `/education/our-ladys-lambies` | 2024-03-07 | 20 | not in nav; thin |
| education | Who is Jesus? | `/education/why-catholic/who-jesus` | 2023-02-17 | 433 | not updated since 2023 |
| events | Upcoming Events | `/events` | 2023-08-11 | 78 | dynamic event listing; not updated since 2023 |
| formation | Formation | `/formation` | 2023-07-11 | 104 | not updated since 2023 |
| home | Clergy & Staff | `/home/clergy-staff` | 2026-09-09 | 69 |  |
| home | The Ordinariate | `/home/ordinariate` | 2021-06-05 | 1296 | home page FAQ links here; not updated since 2021 |
| home | Photo Album | `/home/photo-album` | 2021-05-06 | 15 | thin; not updated since 2021 |
| learn | The Sacrament of the Anointing of the Sick | `/learn/why-catholic/7-sacraments/sacrament-anointing-sick` | 2022-01-05 | 1858 | catechetical twin of `/sacraments/anointing-sick`; not in nav; not updated since 2022 |
| learn | The Seven Sacraments: Sources of Divine Life! | `/learn/why-catholic/seven-sacraments-sources-divine-life` | 2022-01-05 | 128 | not in nav; not updated since 2022 |
| liturgical-outreach-ministries | Liturgical & Outreach Ministries | `/liturgical-outreach-ministries` | 2022-11-01 | 178 | not updated since 2022 |
| liturgy | Confessions | `/liturgy/confessions` | 2026-10-19 | 40 |  |
| liturgy-devotions | Daily Office | `/liturgy-devotions/daily-office` | 2022-11-02 | 19 | thin; not updated since 2022 |
| liturgy-devotions | Holy Mass | `/liturgy-devotions/holy-mass-0` | 2024-08-23 | 91 |  |
| liturgy-devotions | Parish Devotion Hours | `/liturgy-devotions/parish-devotion-hours` | 2024-08-23 | 57 | not in nav |
| ministries | Altar Guild | `/ministries/liturgical-ministries/altar-guild` | 2026-01-28 | 56 |  |
| ministries | Altar Server Resources | `/ministries/liturgical-ministries/altar-servers-ushers/altar-server-resources` | 2022-10-10 | 171 | not updated since 2022 |
| ministries | Altar Server Schedule | `/ministries/liturgical-ministries/altar-servers-ushers/altar-server-schedule` | 2022-10-10 | 5 | not in nav; thin; not updated since 2022 |
| ministries | Greeters & Ushers | `/ministries/liturgical-ministries/altar-servers-ushers/greeters-ushers` | 2022-10-26 | 342 | not updated since 2022 |
| ministries | Music | `/ministries/liturgical-ministries/music` | 2025-01-24 | 113 |  |
| ministries | Choirs | `/ministries/liturgical-ministries/music/choirs` | 2025-02-20 | 487 |  |
| ministries | Music Series | `/ministries/liturgical-ministries/music/music-series` | 2023-11-21 | 42 | not updated since 2023 |
| ministries | Sacraments for the Homebound | `/ministries/liturgical-ministries/sacraments-homebound` | 2026-05-22 | 178 |  |
| ministries | St. Stephens Guild for Altar Servers and Greeters | `/ministries/liturgical-ministries/st-stephens-guild-altar-servers-and-greeters` | 2022-10-14 | 87 | not updated since 2022 |
| ministries | American Heritage Girls TX0814 | `/ministries/outreach-ministries-organizations/american-heritage-girls-tx0814` | 2022-09-22 | 128 | not in nav; not updated since 2022 |
| ministries | The Atonement Catholic Academy Booster Club | `/ministries/outreach-ministries-organizations/atonement-catholic-academy-booster-club` | 2022-10-19 | 139 | school closed June 2024; not in nav; not updated since 2022 |
| ministries | Bereavement | `/ministries/outreach-ministries-organizations/bereavement` | 2022-10-13 | 147 | not updated since 2022 |
| ministries | Catholic Youth Organization (CYO) | `/ministries/outreach-ministries-organizations/catholic-youth-organization-cyo` | 2024-08-23 | 1044 |  |
| ministries | Culture of Life | `/ministries/outreach-ministries-organizations/culture-life` | 2022-10-19 | 455 | not updated since 2022 |
| ministries | Fr. Paul of Graymoor Knights of Columbus, Council #16730 | `/ministries/outreach-ministries-organizations/fr-paul-graymoor-knights-columbus-council-16730` | 2022-10-26 | 272 | not updated since 2022 |
| ministries | God's Comfort in Loss Miscarriage Ministry | `/ministries/outreach-ministries-organizations/gods-comfort-loss-miscarriage-ministry` | 2025-03-13 | 1057 |  |
| ministries | Pastoral Council | `/ministries/outreach-ministries-organizations/pastoral-council` | 2022-10-19 | 82 | not updated since 2022 |
| ministries | Prayer Ministry | `/ministries/outreach-ministries-organizations/prayer-ministry` | 2025-03-13 | 160 |  |
| ministries | Rosary Guild | `/ministries/outreach-ministries-organizations/rosary-guild` | 2024-07-16 | 524 |  |
| ministries | Security & Safety Committee | `/ministries/outreach-ministries-organizations/security-safety-committee` | 2022-10-19 | 128 | not in nav; not updated since 2022 |
| ministries | St. Cuthbert Home Visitation Ministry | `/ministries/outreach-ministries-organizations/st-cuthbert-home-visitation-ministry` | 2022-10-26 | 571 | not updated since 2022 |
| ministries | St. Joseph the Worker Men's Prayer Group | `/ministries/outreach-ministries-organizations/st-joseph-worker-mens-prayer-group` | 2024-08-23 | 92 |  |
| ministries | The Troops of St. George - Troop 815 | `/ministries/outreach-ministries-organizations/troops-st-george-troop-815` | 2022-10-26 | 379 | not updated since 2022 |
| ministries | Weekend Adoration Ministry | `/ministries/outreach-ministries-organizations/weekend-adoration-ministry` | 2022-09-22 | 409 | not in nav; not updated since 2022 |
| ministries | Women of Grace | `/ministries/outreach-ministries-organizations/women-grace` | 2023-09-04 | 167 | not updated since 2023 |
| ministries | Women at the Well Ministry | `/ministries/outreach-ministries-organizations/women-well-ministry` | 2023-09-06 | 151 | not updated since 2023 |
| ministries | Youth Group | `/ministries/outreach-ministries-organizations/youth-group` | 2023-08-01 | 48 | not updated since 2023 |
| ministries | Atonement Young Adult Group | `/ministries/outreach-ministries/atonement-young-adult-group` | 2026-09-17 | 260 |  |
| ministries | Moms Group | `/ministries/outreach-ministries/moms-group` | 2026-10-20 | 301 |  |
| ministries | Newcomers Ministry | `/ministries/outreach-ministries/newcomers-ministry` | 2026-10-20 | 341 |  |
| ministries | St. Vincent de Paul | `/ministries/outreach-ministries/st-vincent-de-paul` | 2026-10-13 | 921 |  |
| ministries-organizations | St. Cuthbert Home Visitation Ministry | `/ministries-organizations/st-cuthbert-home-visitation-ministry` | 2021-03-02 | 5 | stub duplicate; not in nav; thin; not updated since 2021 |
| news | News | `/news` | 2019-07-13 | 1 | empty; not in nav; thin; not updated since 2019 |
| nonnatus | Meal Train for New Moms | `/nonnatus` | 2021-06-25 | 88 | not in nav; not updated since 2021 |
| our-lady-atonement-bereavement-committee | Our Lady of the Atonement Bereavement Committee | `/our-lady-atonement-bereavement-committee` | 2022-09-22 | 147 | duplicate of Bereavement page; not in nav; not updated since 2022 |
| pray | Organs | `/pray/music/organs` | 2021-05-06 | 197 | not updated since 2021 |
| sacraments | Anointing of the Sick | `/sacraments/anointing-sick` | 2026-01-30 | 310 |  |
| sacraments | Baptism | `/sacraments/baptism` | 2026-05-23 | 315 |  |
| sacraments | Confirmation | `/sacraments/confirmation` | 2026-06-24 | 560 |  |
| sacraments | First Holy Communion | `/sacraments/first-holy-communion` | 2026-06-24 | 510 |  |
| sacraments | Holy Matrimony | `/sacraments/holy-matrimony` | 2026-08-21 | 762 |  |
| sacraments | The Sacrament of Baptism | `/sacraments/sacrament-baptism` | 2023-02-17 | 856 | catechetical twin of `/sacraments/baptism`; not in nav; not updated since 2023 |
| sacraments | The Sacrament of Confession | `/sacraments/sacrament-confession` | 2026-10-19 | 3010 |  |
| sacraments | The Sacrament of the Eucharist | `/sacraments/sacrament-eucharist` | 2022-11-15 | 1350 | home page 'Mass Times' heading links here; not updated since 2022 |
| sacraments | The Sacrament of Holy Matrimony | `/sacraments/sacrament-holy-matrimony` | 2022-11-15 | 2307 | catechetical twin of `/sacraments/holy-matrimony`; not in nav; not updated since 2022 |
| safe-environment | Safe Environment | `/safe-environment` | 2026-03-25 | 93 |  |
| test | Test | `/test` | 2022-04-10 | 5 | test page, publicly live; not in nav; thin; not updated since 2022 |
| why-catholic | Why "Catholic"? | `/why-catholic` |  | 155 |  |
| why-catholic | The Sacrament of Confirmation | `/why-catholic/7-sacraments/sacrament-confirmation` | 2019-07-13 | 964 | catechetical twin of `/sacraments/confirmation`; not in nav; not updated since 2019 |
| why-catholic | The Sacrament of Holy Orders | `/why-catholic/7-sacraments/sacrament-holy-orders` | 2019-07-13 | 1179 | only page on Holy Orders; not in nav; not updated since 2019 |
| why-catholic | Coming Back to the Church | `/why-catholic/coming-back-church` |  | 542 |  |
| why-catholic | What is Salvation? | `/why-catholic/what-salvation` | 2019-07-13 | 1143 | not updated since 2019 |

## 5. Content health

| Problem | Examples |
|---|---|
| **Stale facts** | "in union with Pope Francis" (home); 2025 holiday PDF; Academy booster club; "Under construction" banner |
| **Duplicates** | Two calendars (`/about-us/calendar`, `/about-us/calendar-0`); two Bereavement pages; two St. Cuthbert pages |
| **Two parallel sacrament sets** | Practical pages (`/sacraments/baptism`: how to arrange it at OLA, mostly updated 2026) and older catechetical pages (`/sacraments/sacrament-baptism`: what the sacrament is, 2019–2023). Most catechetical pages aren't in the nav. Holy Orders exists only in the catechetical set. |
| **Schedules retyped on several pages** | Mass times on the home page and the Holy Mass page (the holy-day Mass appears only on the home page); devotions on the home page and the Parish Devotion Hours page differ (an "Adoration Hour 6:30–7:30 PM" has no day; the "Right to Life Mass" appears only on the home page) |
| **Login walls on public links** | Parishioner Business Directory (unpublished, but linked in the footer and About menu); `/education/why-catholic/becoming-catholic` (unpublished duplicate) |
| **Orphans and stubs** | `/test`, `/news` (empty), `/nonnatus` (Meal Train, 2021), Security & Safety Committee, American Heritage Girls, ENDOW, Our Lady's Lambies, Weekend Adoration Ministry |
| **Content in embeds and documents** | Altar server schedule in a Google Doc; interest forms in Google Forms; giving through Tithely (embedded) and ParishSOFT (links out); bulletin in an LPi widget |

## 6. Parish facts as published (2026-10-27)

Copied from the current site for reference so agents don't have to invent placeholders. **⚑ Verify with the parish before reuse; some are already inconsistent across pages (§5).**

**Identity and history** (from `/about-us`)
- Our Lady of the Atonement Catholic Church, "A Parish of the Personal Ordinariate of the Chair of St. Peter."
- Founded by Fr. Christopher G. Phillips with the permission of Archbishop Patrick Flores; Decree of Erection effective **15 August 1983**.
- Founded as a Personal Parish under the Pastoral Provision, for the "Anglican Common Identity usage." The site says it was "the first parish ever to be established for this purpose."
- The title Our Lady of the Atonement "originated in the Episcopal Church in the 19th century, and… was brought into the Catholic Church by the Graymoor Friars and Sisters of The Atonement in 1909."
- First Masses were at the Church of San Francesco di Paola, downtown San Antonio; 18 founding members.
- The Atonement Academy opened in 1994 (eventually PreK3–12, 500+ students) and **closed in June 2024**.
- The church was expanded in 2006. A new building across from the church and school is under construction (offices, meeting rooms, multipurpose hall).
- Incorporated into the Ordinariate of the Chair of St. Peter in **2017** (Bishop Steven J. Lopes).
- Home page motto: *"Worship the LORD in the beauty of holiness."* Meta description: *"Fully Catholic. Fully Alive."*

**Schedule** (from the home page)
- **Mass:** Sat 5:00 PM anticipatory (Said) · Sun 7:00 AM (Said), 9:00 AM (Sung), 11:00 AM (Sung), 5:00 PM (Said) · Mon–Sat 7:00 AM (Said) · Holy Days of Obligation 6:30 PM
- **Confessions:** Sun 7:50–8:50 AM · Wed 3:30–4:30 PM · Fri 7:50–8:50 AM · Sat 3:30–4:30 PM
- **Daily Office:** Morning and Evening Prayer, daily, 6:30 AM and 4:30 PM
- **Devotions:** Adoration in the Sacred Heart Chapel, Fri 7:45 AM – Sun 6:15 AM · Benediction, first Saturday after 7:00 AM Mass · Parish Rosary, Saturdays after 7:00 AM Mass · Right to Life Mass, first Saturday 7:00 AM

**Contact**
- 15415 Red Robin Road, San Antonio, TX 78255 · (210) 695-2944
- Office hours: Mon–Thu 8 AM–4 PM (closed 12–1), Fri 8 AM–12 PM

## 7. Implications for the IA session

1. **Ministries need a directory, not a menu.** 28+ groups of very different kinds (liturgical service, devotion, fellowship, youth, charity, governance). Something browsable and filterable, each with an owner and a "last confirmed" date.
2. **Decide what to do with the two sacrament layers.** "How to arrange it at OLA" (people at a threshold) and "what this sacrament is" (inquirers) are both valuable. Options: one page per sacrament with both layers, or two sections cross-linked.
3. **Schedules must be data, entered once.** Every place a time appears should draw from one source. That is also what feeds structured data, calendar feeds, and the liturgical "Day's Prayer."
4. **Give inquirers a real front door.** The ingredients exist (FAQ, Ordinariate explainer, Becoming Catholic, Coming Back) but need one clear path, especially for Anglican/Protestant seekers.
5. **Emergency care needs a real after-hours route,** reachable in one tap from anywhere. This is a parish process question before it's a design question.
6. **Build content governance into the model:** owners, review dates, and expiry for time-bound content, so the new site doesn't drift the way this one has.
7. **Mass intentions.** An unpublished "Mass Intention" page (2022) suggests a common parish task (requesting a Mass for someone) with no current home ⚑ Josh: how are intentions requested today?

## 8. From the Drupal admin (2026-10-27)

Read-only look, with Josh logged in.

**No traffic data.** Drupal's Reports section has only error logs (recent messages, top 403s, top 404s). Real usage data exists only in Google Analytics (Q20).

**The error logs cover about 3.7 days** (Oct 24 03:33 to Oct 27 20:53, roughly 10,000 entries) and are dominated by bots:
- **404s:** almost entirely vulnerability scanners probing `/api`, `/graphql`, `/login`, `/.env`, and similar. One real fault: 76 hits on `<nolink>`, a broken entry in the site's own sitemap.
- **403s:** `node/208` (the unpublished Parishioner Business Directory) leads with 746, about 200 a day. It's linked in every page's footer, so this is mostly crawlers, and it can't be read as human demand. Smaller numbers hit other unpublished pages that outside links or search indexes still point to: old Becoming Catholic (44), Documents and Forms (42), old Holy Mass (9), old St. Vincent de Paul (6), COVID-19 (3), "New Here?" (2).

**Content (`/admin/content`):**
- 95 pages: 84 published, 11 unpublished; 62 in the main menu, 33 not.
- Unpublished: Becoming Catholic (old), Documents and Forms, Parishioner Business Directory, Test Page, Adult Inquiry, Society of St. Vincent De Paul (old), Holy Mass (old), Read the Sunday Bulletin, Join the Parish, **Mass Intention**, COVID-19.
- Last updated, by year: 2016: 1 · 2019: 6 · 2020: 1 · 2021: 6 · 2022: 28 · 2023: 11 · 2024: 9 · 2025: 9 · 2026: 24.
- **Editors:** five accounts have edited pages since 2025, and two of them made most of the edits (13 and 11). The parish does have people actively maintaining the site (relevant to Q3).
