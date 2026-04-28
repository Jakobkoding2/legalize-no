# legalize-no

Norwegian legislation as a Git repository — every law is a Markdown file, every amendment is a commit.

**781 laws** spanning from 1687 to the present day.

Inspired by [legalize-es](https://github.com/legalize-dev/legalize-es).

---

## Why

Norwegian law is publicly available via Lovdata's open API, but it's not version-controlled or easy to diff. This project makes the full body of Norwegian legislation:

- **Searchable** with standard text tools (`grep`, `fzf`, `ripgrep`)
- **Diffable** — track exactly what changed between amendments
- **Programmable** — structured YAML frontmatter on every file for easy parsing
- **Offline** — clone once, search forever

Useful for legal tech, NLP training data, academic research, and anyone who wants to `git log` the history of Norwegian law.

---

## Structure

```
no/
  LOV-1814-05-17.md       ← Grunnloven (Constitution)
  LOV-2005-06-17-62.md    ← Arbeidsmiljøloven (Working Environment Act)
  LOV-1902-05-22-10.md    ← Straffeloven 1902 (Penal Code)
  ...
```

Filenames follow Lovdata's identifier format: `LOV-YYYY-MM-DD-NR`.

## File format

Each law is a Markdown file with YAML frontmatter:

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

## Source and license

Legal texts are fetched from [Lovdata](https://lovdata.no/)'s open API and licensed under [NLOD 2.0](https://data.norge.no/nlod/en/2.0).

Data source: `https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2`

## Build locally

Requires Python 3.10+ and BeautifulSoup4.

Install dependencies, download the source data, and run the build script:

```
pip install beautifulsoup4
python build.py
```

## Related projects

- [legalize-es](https://github.com/legalize-dev/legalize-es) — Spanish legislation as a Git repo
- [legalize](https://github.com/legalize-dev/legalize) — Umbrella project
