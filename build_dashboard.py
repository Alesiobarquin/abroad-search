#!/usr/bin/env python3
"""Build the static review map from reviewed data. Does not fetch or contact anyone."""
import json
import math
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent


def validate(data):
    listings = data['listings']
    assert len({p['id'] for p in listings}) == len(listings), 'Duplicate listing IDs'
    assert len({p['review_id'] for p in listings}) == len(listings), 'Duplicate review IDs'
    assert len({p['url'] for p in listings}) == len(listings), 'Duplicate primary URLs'
    assert data['merge_counts']['distinct_records'] == len(listings)
    assert data['merge_counts']['earlier_records'] + data['merge_counts']['map_repo_records'] - data['merge_counts']['overlapping_records'] == len(listings)
    for p in listings:
        assert p['status'] in {'prospect', 'lead', 'excluded', 'benchmark'}
        readiness = p['move_in_readiness']
        assert readiness['status'] in {'unverified', 'confirmed'}
        if readiness['status'] == 'confirmed':
            assert all(readiness[k] is True for k in ['bed_linen', 'pillows_and_duvets', 'towels', 'kitchenware']), 'Arrival essentials need explicit confirmation'
        # shortcut: all records remain unqualified; revise this gate after full dated verification.
        assert p['calendar_verified'] is False and p['value_score'] is None
        for url in [p['url'], *p['alternate_urls'], *p['source_urls']]:
            parsed = urlparse(url)
            assert parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password
        loc = p['location']
        if loc:
            assert loc['precision'] in {'building', 'approximate', 'proxy'}
            assert math.isfinite(loc['lat']) and math.isfinite(loc['lon'])
            assert 41.3 <= loc['lat'] <= 41.5 and 2.0 <= loc['lon'] <= 2.3
            assert loc['precision'] == 'building' or loc['radius_m'] > 0
        cost = p['cost']
        assert cost['unknown'], 'Incomplete quotes must name the outstanding costs'
        amounts = [x['amount_eur'] for x in cost['items']]
        assert all(math.isfinite(x) and x >= 0 for x in amounts)
        if amounts:
            assert abs(sum(amounts) - cost['subtotal_eur']) < .005, 'Cost subtotal mismatch'
        else:
            assert cost['subtotal_eur'] is None
    assert data['merge_counts']['fully_verified'] == 0


def build(data):
    validate(data)
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    # Listing text cannot terminate the application/json script element.
    encoded = encoded.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'dashboard_template.html').read_text()
    assert template.count('{{DATA_JSON}}') == 1
    return template.replace('{{DATA_JSON}}', encoded)


if __name__ == '__main__':
    data = json.loads((ROOT / 'upf_housing_candidates.json').read_text())
    html = build(data)
    for name in ['index.html', 'housing_dashboard.html']:
        (ROOT / name).write_text(html)
    print(f"Built {len(data['listings'])} reviewed findings; no live availability claims.")
