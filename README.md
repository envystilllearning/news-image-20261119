# The World in One Day — Thursday 19 November 2026

A single 1024×1024 newspaper poster summing up the world's news of
Thursday 19 November 2026. Every story on the page happened, or was first
reported, on that day, in any time zone. The poster is rendered by
`generate.py` (Python + PIL, standard library plus Pillow) and shipped as
`entry.png`; `main.ts` copies it to the harness output directory.

## Layout

The poster follows one visual family: a light paper background, a serif
masthead with the date in large red type, a region strip and a field strip,
a "day in numbers" strip, three illustrated feature panels, ten mini-viz
cards, a numbered-pin world map, an "ALSO" list of 26 more briefs, a DATE
CHECK box, and a sources footer.

- **Masthead** — "THE WORLD IN ONE DAY" over "THURSDAY 19 NOVEMBER 2026",
  with the promise that everything on the page is from that day.
- **BY REGION** — ASIA 18 · N. AMERICA 10 · EUROPE 6 · WORLD 3 · OCEANIA 2.
- **BY FIELD** — Politics 10 · Markets 15 · Tech 3 · World 6 · Sport 3 ·
  Culture 2.
- **THE DAY IN NUMBERS** — Dow −561 (−1.11%), Brent $88.73 (−4.73%), gold
  $3,738, Nikkei 59,024 (+0.3%), GTA VI $79.99 (16m+ pre-orders), Voyager 1
  25.9bn km (one light-day).
- **DATE CHECK** — eight items that were reported on 17–18 November, not
  today, are named and excluded: the Pew Islam report, Jeffries nominated,
  Glastonbury 2027, the Brazil fiscal package, the Gaza offensive, the EU
  €45bn loan, the Nvidia H200 halt, and the Carney–Xi thaw.

## The three features

1. **GTA VI IS HERE** — the biggest launch of the year. Rolling midnight
   launch worldwide on PS5 and Xbox Series X|S, $79.99 standard. New
   Zealand plays first; 16m+ pre-orders.
2. **TRUMP, XI AND PUTIN MEET THREE-WAY** — a first. First-ever trilateral
   on the APEC sidelines; Iran and nuclear arms on the agenda, Ukraine off
   it.
3. **WORLD COURT RULES ON MYANMAR** — The Hague. Judgment day in The
   Gambia v. Myanmar; 730,000+ displaced in 2017; a first verdict possible.

## The ten cards

4. **ANTHROPIC DEBUTS AT $83** — priced above range at $83; $81.34bn
   offering; $26bn placement.
5. **VOYAGER 1: ONE LIGHT-DAY OUT** — NASA confirms the milestone at 5:16
   a.m. EST, 49 years after launch.
6. **CYCLONE AKVAN BEARS DOWN** — landfall due noon Friday; winds 90–100
   km/h, red alerts in Odisha.
7. **MODI MEETS THE ROYALS** — the Prince and Princess of Wales in New
   Delhi, boosting UK–India ties.
8. **INDIA AND JAPAN TALK DEFENCE** — 2+2 dialogue in Tokyo; Singh and
   Jaishankar review defence ties.
9. **INDIGO HALTS FOUR SAUDI ROUTES** — flights to Jeddah, Madinah, Riyadh
   and Dammam cancelled to 30 Nov.
10. **THE COALITION MEETS IN BERLIN** — Merz hosts five leaders plus NATO's
    Rutte; drone package for Kyiv.
11. **COP31'S FINAL STRETCH** — Antalya talks seek fossil-fuel phase-out;
    $120bn a year by 2035.
12. **ALIBABA REPORTS TODAY** — September-quarter results before the US
    open; Qwen4-Max out Monday.
13. **ISRAEL'S E1 DECISION DUE** — caretaker government to rule on E1;
    Australia, Britain imposed sanctions.

## The 26 briefs (ALSO list)

14. Dow drops 561 (−1.11%) to 50,198 · 15. S&P falls a fifth day; Nasdaq
    +0.42% · 16. Brent slides to $88.73 (−4.73%) · 17. Gold extends slide to
    $3,738 · 18. Nikkei closes up 0.3% at 59,024 · 19. Nikkei opens higher;
    SoftBank +1.2% · 20. FTSE 100 falls 1.3% to 10,551 · 21. US 10-year yield
    holds above 5% · 22. Seoul delays open an hour for exam · 23.
    UnitedHealth sinks 10% on clawback · 24. Hong Kong stocks set to open
    lower · 25. Kospi jumps 2% to 5,067 on chips · 26. Nvidia gives back
    bounce, down 2.9% · 27. Colts at Texans, Thursday night NFL ·
    28. Bangladesh trail by 99 runs, day four · 29. Sri Lanka–Pakistan Test,
    day two · 30. Britain and EU haggle over summit text · 31. APEC leaders
    wrap up in Shenzhen · 32. Saudi Arabia braces for long Houthi fight ·
    33. Canadian judge orders firms to disclose · 34. Pakistan minister to
    attend SCO talks · 35. India reviews rail readiness for Akvan ·
    36. Telangana braces for rain to Saturday · 37. KFC Australia's fake
    funeral for GTA · 39. Logitech declares GTA "Game Day" off ·
    40. New Zealand first to play GTA VI.

The world map pins 1–13 (the features and cards) and dots the briefs
14–40. Number 38 is deliberately absent: the ENISA cybersecurity report
brief was removed after verification showed it was published on
10 November, not 19 November.

## How to build and run

Render the poster (deterministic — two runs produce the same file):

```sh
python3 generate.py   # writes entry.png (1024x1024, under 1 MiB)
```

Run the entrypoint, which copies the poster to the output directory:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` refuses to ship an image over the 1 MiB cap and verifies the copy
by size and sha256. The poster was checked story by story against the
sources named in the footer (Rockstar Support, PlayStation Blog, Reuters,
AP, NASA, The Hindu, Le Monde, TradingView, MarketWatch, Inc.com,
cricbuzz, Times of India, and others); market briefs use 18 Nov closes as
reported on the morning of 19 Nov.
