# Barcelona housing for UPF · Winter 2027

A shared housing review for four students attending UPF Ciutadella in January–March 2027. It combines two AI-assisted research sets in an interactive map, with costs, room details, source links and unresolved questions.

**[Open the housing map](https://alesiobarquin.github.io/abroad-search/)** · [Research notes and all options](RESEARCH_NOTES.md) · [Download the data](upf_housing_candidates.json) · [Agent Guide](AGENTS.md)

## Use it with your roommates

1. Open the map. Search notes, statistics, the legend and archive links are inside **About this search**. It starts with all 71 findings. Use the status filter to focus on 31 prospects and preliminary leads.
2. Read **Details** before choosing a place. Dashed pins are approximate; some findings have no reliable location.
3. Use the budget slider, walk-time selector, bathroom and balcony filters as needed. Reported walk times include clearly labelled original agent estimates.
4. Click **Save** on places you like, then **Copy shortlist link**. The saved IDs travel in the link so roommates can review the same selection.
5. Use **Research status** to review the 36 excluded listings or 4 residence benchmarks. Discuss choices in GitHub Issues or share the shortlist link directly.

Saving a place does not contact anyone. Outreach remains on hold until the group chooses properties and authorizes inquiries. A shortlist is stored in the link, not a shared account or live voting database.

[November 3 exclusion recheck](EXCLUSION_RECHECK.md): all 31 original exclusions reviewed; 6 reopened for clarification. No property was promoted to a verified match.

[New 10–15-minute walking search](CLOSE_WALK_SEARCH.md): 10 additional records, two cross-platform duplicates merged, and four winter calendar corrections. The original 61 records remain. New findings include Pujades and a published-rate RESA La Ciutadella benchmark; several close flats fail dates, arrival inventory or budget.

## What the research establishes

As of **November 3, 2026**, the set contains **71 distinct records**: 5 developed conditional prospects, 26 preliminary leads/search routes, 36 exclusions and 4 residence benchmarks. **Zero are fully verified or booking-ready.** A generic provider search is labelled as such, rather than counted as a confirmed flat.

The earlier set had 49 records; the map repo had 21 summaries. Nine overlapped, giving 61 original combined records. Ten subsequent findings bring the total to 71. The merge retains the earlier A–O review labels and the other map’s unique leads as P–AA; newer records use AB–AJ and BM4. These labels are not value ranks.

The target is four separate sleeping rooms, at least 1.5 bathrooms, furnished accommodation with heating, installed internet, study space and a washer. Move-in readiness also requires sheets, pillows / winter bedding, towels and equipped kitchenware for all four; furniture alone is not enough. The group budget is **€3,680/month**, or **€11,040 for the three-month comparison**. January 1–March 31 is 89 nights; January 5–April 1 is 86 nights. The comparison uses three months and is not an exact invoice for either window.

Unknown fees are not zero. The map shows incomplete subtotals and estimates, with refundable deposits separate. Availability, academic-purpose leases, room ventilation and complete fees still need property-specific confirmation. Several previous “verified” rankings contradicted saved listing evidence; [the notes explain those corrections](RESEARCH_NOTES.md#where-the-research-differed).

## Run or update locally

The page is static HTML using Leaflet 1.9.4 and OpenStreetMap tiles. No build packages or account are required. Map assets need internet access; the embedded findings and filters work if the map library cannot load.

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. To update the reviewed JSON and regenerate both HTML entry points:

```sh
python3 build_dashboard.py
python3 -m unittest discover -s tests -v
```

The tests check merge counts, material exclusions, cost arithmetic, safe links, embedded-data escaping and generated-file consistency. The public repo contains the combined assessment, code and [both agents’ complete finding snapshots](research/README.md). Original prices, room descriptions, calendar claims and scores are preserved inside each card’s Details beside the current assessment. Raw page captures, account/session data, local logs, personal application documents and old scraping scripts stay local. The other agent’s unfilled application and lease notes are retained as labelled source notes. There is no active watchdog in this version.

The map layout and initial listing summaries came from the other agent’s workspace. The merged evidence, corrections and interface changes were produced with Codex assistance. Listing facts belong to the linked sources; location data and map tiles are © OpenStreetMap contributors, under their respective [data](https://www.openstreetmap.org/copyright) and [tile usage](https://operations.osmfoundation.org/policies/tiles/) terms.
