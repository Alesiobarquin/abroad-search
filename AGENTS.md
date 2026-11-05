# AGENTS.md — Contributor & Agent Guide for abroad-search

> **Context**: This repository hosts an interactive housing research review and live map for 4 university students attending **Universitat Pompeu Fabra (UPF) Ciutadella Campus** for Winter Term 2027 (January 1 / January 8 through March 31, 2027).
> 
> **Live Deployment**: [https://alesiobarquin.github.io/abroad-search/](https://alesiobarquin.github.io/abroad-search/)
> 
> **For Incoming AI Agents & Automated Assistants**: Read this file first. Adhering to the conventions below will prevent breaking CI tests, committing disallowed paths, corrupting data structures, or burning unnecessary LLM context tokens on duplicate scraping.

---

## 1. Quick Orientation & Repository Architecture

This repository uses a **single source of truth** architecture. Do not edit HTML files directly without updating the build pipeline.

```
├── upf_housing_candidates.json    # Master dataset (71 reviewed listings)
├── dashboard_template.html        # HTML + Leaflet.js UI template
├── build_dashboard.py             # Build script: compiles JSON into static HTML
├── index.html                     # Deployed static frontend (GitHub Pages root)
├── housing_dashboard.html         # Mirror static frontend
├── tests/
│   └── test_build.py              # Strict regression tests executed on CI/push
├── upf_housing_daemon.py          # Background watchdog (price drop & listing monitor)
└── research/                      # Historical datasets, original agent logs, audit records
```

### The Standard Build Loop
Whenever modifying data or UI template:
```bash
# 1. Update data in upf_housing_candidates.json OR UI in dashboard_template.html
# 2. Recompile static files
python3 build_dashboard.py

# 3. Verify ALL regression tests pass
python3 -m unittest discover -s tests -v

# 4. Commit and push to deploy to GitHub Pages
git add dashboard_template.html housing_dashboard.html index.html upf_housing_candidates.json
git commit -m "Your concise change description"
git push origin main
```

---

## 2. Core Search Constraints & Ground Rules

All property assessments must adhere strictly to these project constraints:

| Parameter | Specification | Notes / Dealbreakers |
| :--- | :--- | :--- |
| **Anchor Point** | UPF Ciutadella Campus | `Carrer de Ramon Trias Fargas, 25-27, 08005 Barcelona` (`41.3894, 2.1915`). |
| **Occupants** | 4 adult students | Whole apartment required; no landlord/stranger co-living. |
| **Stay Window** | Jan 8 – Mar 31, 2027 *(or Jan 1 – Mar 31)* | Stays **must exceed 31 nights** (alquiler de temporada / seasonal lease). |
| **Hard Budget Cap** | **€3,680 / month total** ($4,000 USD) | **€920 / person / month** all-in. Anything higher is auto-disqualified. |
| **Target Value** | €2,400 to €3,200 / month total | €600 to €800 / person / month. |
| **Bedrooms** | Minimum 4 real bedrooms | Dedicated doors, exterior/ventilated windows. No living-room sofa beds (*zulos*). |
| **Bathrooms** | Minimum 1.5 bathrooms | 2 full bathrooms strongly preferred for 4 occupants. |
| **Amenities** | Heating, washer, high-speed Wi-Fi | Mandatory for winter months in Barcelona. |

---

## 3. Schema & Data Structure Rules (Common Pitfalls)

Incoming agents frequently introduce subtle breaking changes. Keep these in mind:

### A. Calendar Availability vs. Historical Status
* **`calendar_availability`**: Controls the live filter tab in the dashboard.
  * `"available"`: Verified open for Jan 8 – Mar 31, 2027 with zero conflicting blocks.
  * `"blocked"`: Disqualified due to existing booking, budget violation, or 11-month lease requirement.
  * `"unverified"`: Lead requiring agency phone call or manual inquiry.
  * `"benchmark"`: Dedicated student residence option (e.g. Resa, Livensa, Blau).
* **`status`**: Historical research classification (`"prospect"`, `"lead"`, `"excluded"`, `"benchmark"`).
  > ⚠️ **DO NOT randomly alter the historical `status` field** — `tests/test_build.py` enforces exact status assertions on historical records (e.g. `test_material_conflicts_and_costs`, `test_close_walk_search_dates_costs_and_deduplication`). Use `calendar_availability` for live state changes!

### B. Location & Map Pin Requirements
* Every pin on the map requires a valid `location` object:
  ```json
  "location": {
    "lat": 41.38181,
    "lon": 2.16963,
    "precision": "approximate",  // "building", "approximate", or "proxy"
    "label": "Spotahome map point (Carrer del Pintor Fortuny / El Raval)",
    "radius_m": 150,             // Must be > 0 if precision != "building"
    "source_url": "https://..."
  }
  ```
* **Coordinate Bounds**: `validate(data)` strictly asserts `41.3 <= lat <= 41.5` and `2.0 <= lon <= 2.3`.
* **Exception**: Review ID `N` (`lupo_poblenou_search`) **must have `location: null`** (asserted by unit tests).

### C. Commute Metrics
* Always provide:
  * `commute.walking_minutes_estimate`: (float, e.g. `7.0`)
  * `commute.walking_distance_m`: (float, e.g. `526.5`)
  * `commute.walking_route_summary`: (string, e.g. `"527 m · 7.0 min walk to UPF"`)
  * `commute.transit_alternative`: (string, e.g. `"5 min via Tram T4"`)
* To calculate walking distance fast without hallucinating, query OpenStreetMap OSRM:
  ```bash
  curl -s "https://routing.openstreetmap.de/routed-foot/route/v1/driving/{lon},{lat};2.1915,41.3894?overview=false"
  ```
  Divide `duration` by 60 for minutes, `distance` for meters.

### D. Security & Privacy Guardrails
* **No Private File Paths**: `tests/test_build.py` scans `upf_housing_candidates.json` for strings like `/Users/`, `file://`, `pk_live_`, `__SOYUZ_CONTEXT__`. The build test will reject the commit if found.
* **HTTPS Only**: All URLs must use valid `https://` schemas with non-empty network locations.

---

## 4. Token-Saving Cached Data & Utilities

Before burning tokens writing new scrapers or querying websites from scratch, use the existing local cached dumps:

| Data Source | Local File / Utility | Purpose |
| :--- | :--- | :--- |
| **Spotahome Data** | `spotahome_candidates.json`, `spotahome_batch2.json`, `all_4beds_spotahome.json` | Contains full JSON payloads with exact lat/lon, prices, and room details. |
| **HousingAnywhere** | `housinganywhere_4beds.json`, `ha_hydration.json` | Contains Hydration state with exclusion calendars. |
| **ShBarcelona** | `sh_10841.json` | Full seasonal rental payload. |
| **Research Notes** | `RESEARCH_NOTES.md` | In-depth rationale, previous agent conflicts, and landlord policies. |
| **Exclusion Audits** | `EXCLUSION_RECHECK.md` | Breakdown of why 39 listings were excluded. |

---

## 5. Adding or Updating Listings Checklist

1. [ ] Check that stay duration is $\ge 32$ days (between Jan 1 / Jan 8 and Mar 31).
2. [ ] Verify monthly all-in cost $\le €3,680$ total ($\le €920$/person).
3. [ ] Confirm 4 dedicated sleeping rooms with windows (no sofa-bed conversions).
4. [ ] Calculate walking distance to UPF Ciutadella (`41.3894, 2.1915`) using OSRM foot routing.
5. [ ] Ensure `location` object is present with valid Barcelona coordinates (`lat` $\approx 41.38$, `lon` $\approx 2.18$).
6. [ ] Run `python3 build_dashboard.py` to regenerate `index.html` and `housing_dashboard.html`.
7. [ ] Run `python3 -m unittest discover -s tests -v` — ensure **9/9 tests pass**.
8. [ ] Commit and push to `main` for instant deployment on GitHub Pages.
