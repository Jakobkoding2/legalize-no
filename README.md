# legalize-no

Norsk lovgivning som et Git-repo — hver lov er en Markdown-fil, hver endring er en commit.

**781 lover** fra 1687 til i dag.

Inspirert av [legalize-es](https://github.com/legalize-dev/legalize-es).

---

## Struktur

```
no/
  LOV-1814-05-17.md       ← Grunnloven
  LOV-2005-06-17-62.md    ← Arbeidsmiljøloven
  LOV-1902-05-22-10.md    ← Straffeloven (1902)
  ...
```

Hvert filnavn følger Lovdatas identifikator: `LOV-ÅÅÅÅ-MM-DD-NR`.

## Filformat

Hver lov er en Markdown-fil med YAML-frontmatter:

```markdown
---
title: "Kongeriket Norges Grunnlov"
short_title: "Grunnloven – Grl."
identifier: "LOV-1814-05-17"
country: "no"
rank: "lov"
lang: "nb"
publication_date: "1814-05-17"
last_change_in_force: "2024-05-21"
status: "gjeldende"
source: "https://lovdata.no/dokument/NL/lov/1814-05-17"
department: ["Justis- og beredskapsdepartementet"]
subjects: ["Grunnloven", "Stortinget"]
---
# Kongeriket Norges Grunnlov
...
```

## Kilde og lisens

Lovtekstene er hentet fra [Lovdata](https://lovdata.no/) sitt åpne API og er lisensiert under [NLOD 2.0](https://data.norge.no/nlod/en/2.0).

Data hentes fra:
- Lover: `https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2`

## Bygge lokalt

Krev Python 3.10+ og BeautifulSoup4:

```bash
pip install beautifulsoup4
```

Last ned og pakk ut kildedataene:

```bash
curl -L https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2 -o lover.tar.bz2
tar xf lover.tar.bz2
# Plasser innholdet i nl/
python build.py
```

## Relaterte prosjekter

- [legalize-es](https://github.com/legalize-dev/legalize-es) — Spansk lovgivning som Git-repo
- [legalize](https://github.com/legalize-dev/legalize) — Paraplyprosjekt
