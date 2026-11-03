import copy
import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_dashboard import build, validate


class HousingReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'upf_housing_candidates.json').read_text())

    def test_merge_counts_and_existing_review_labels(self):
        validate(self.data)
        rows = self.data['listings']
        self.assertEqual(len(rows), 71)
        self.assertEqual(self.data['merge_counts']['additional_research_records'], 10)
        self.assertEqual(sum(p['status'] in ['prospect', 'lead'] for p in rows), 31)
        self.assertEqual(sum(p['status'] == 'excluded' for p in rows), 36)
        self.assertEqual(sum(p['status'] == 'benchmark' for p in rows), 4)
        self.assertTrue(set('ABCDEFGHIJKLMNO').issubset({p['review_id'] for p in rows}))

    def test_material_conflicts_and_costs(self):
        rows = {p['id']: p for p in self.data['listings']}
        for id in ['spotahome_201508', 'spotahome_1426235', 'spotahome_1403718', 'spotahome_932678']:
            self.assertEqual(rows[id]['status'], 'excluded')
            self.assertTrue({'Earlier review', 'Map repo'}.issubset(rows[id]['research_tracks']))
            self.assertTrue(rows[id]['conflicts'])
        self.assertEqual(rows['habitatgejove_2489']['cost']['subtotal_eur'], 6767)
        self.assertEqual(rows['idealista_112946294']['cost']['subtotal_eur'], 5469.63)
        self.assertEqual(rows['spotahome_324761']['cost']['subtotal_eur'], 7370)
        self.assertGreater(rows['housinganywhere_ut1732758']['cost']['subtotal_eur'], 11040)
        self.assertIsNone(rows['lupo_poblenou_search']['location'])

    def test_all_original_findings_are_preserved(self):
        original_map = json.loads((ROOT / 'research/map_agent_findings.json').read_text())
        original_earlier = json.loads((ROOT / 'research/earlier_agent_findings.json').read_text())
        embedded_map = [p['original_map_findings'] for p in self.data['listings'] if 'original_map_findings' in p]
        embedded_earlier = [p['earlier_agent_findings'] for p in self.data['listings'] if 'earlier_agent_findings' in p]
        self.assertEqual(len(original_map), 21)
        self.assertEqual({p['id']: p for p in embedded_map}, {p['id']: p for p in original_map})
        expected = [p for key in ['conditional_candidates', 'unverified_leads', 'rejected_screenings', 'residence_benchmarks'] for p in original_earlier[key]]
        self.assertEqual(len(expected), 49)
        self.assertEqual({p['id']: p for p in embedded_earlier}, {p['id']: p for p in expected})

    def test_rejects_invalid_money_and_links(self):
        invalid = copy.deepcopy(self.data)
        invalid['listings'][0]['cost']['subtotal_eur'] += 1
        with self.assertRaises(AssertionError):
            validate(invalid)
        invalid = copy.deepcopy(self.data)
        invalid['listings'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(AssertionError):
            validate(invalid)

    def test_furniture_does_not_establish_arrival_readiness(self):
        row = next(p for p in self.data['listings'] if p['review_id'] == 'A')
        self.assertTrue(row['details']['property']['furnished'])
        self.assertEqual(row['move_in_readiness']['status'], 'unverified')
        self.assertIsNone(row['move_in_readiness']['bed_linen'])
        self.assertIsNone(row['move_in_readiness']['towels'])
        invalid = copy.deepcopy(self.data)
        next(p for p in invalid['listings'] if p['review_id'] == 'A')['move_in_readiness']['status'] = 'confirmed'
        with self.assertRaises(AssertionError):
            validate(invalid)

    def test_exclusion_recheck_distinguishes_duration_from_purpose(self):
        from datetime import date
        rows = {p['review_id']: p for p in self.data['listings']}
        parcel = rows['R05']
        self.assertEqual((date(2027, 3, 31) - date(2027, 1, 1)).days, 89)
        self.assertTrue(parcel['duration_check']['duration_fits_in_principle'])
        self.assertEqual(parcel['status'], 'excluded')
        self.assertFalse(parcel['move_in_readiness']['bed_linen'])
        self.assertFalse(parcel['move_in_readiness']['towels'])
        self.assertEqual(parcel['cost']['subtotal_eur'], 9109.5)
        reopened = {'R09', 'R20', 'R21', 'R23', 'R24', 'R30'}
        self.assertEqual(set(self.data['exclusion_recheck']['reopened_review_ids']), reopened)
        self.assertTrue(all(rows[k]['status'] == 'lead' and not rows[k]['calendar_verified'] for k in reopened))
        self.assertEqual(sum('exclusion_audit' in p for p in rows.values()), 31)

    def test_embedded_data_cannot_close_script(self):
        data = copy.deepcopy(self.data)
        data['listings'][0]['title'] = '</script><script>alert("x")</script>'
        html = build(data)
        embedded = html.split('<script id="housing-data" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertNotIn('</script>', embedded)
        self.assertEqual(json.loads(embedded)['listings'][0]['title'], data['listings'][0]['title'])

    def test_close_walk_search_dates_costs_and_deduplication(self):
        rows = {p['review_id']: p for p in self.data['listings']}
        for key in ['P', 'Y', 'J', 'V', 'AI', 'AJ']:
            self.assertEqual(rows[key]['status'], 'excluded')
        self.assertIn('https://www.uniplaces.com/accommodation/barcelona/767287', rows['R05']['alternate_urls'])
        self.assertEqual(rows['R05']['commute']['origin_precision'], 'building')
        self.assertLess(rows['R05']['commute']['walking_minutes_estimate'], 10)
        self.assertGreater(rows['T']['commute']['walking_minutes_estimate'], 15)
        self.assertGreater(rows['AE']['commute']['walking_minutes_estimate'], 15)
        self.assertEqual(rows['AH']['cost']['subtotal_eur'], 11700)
        self.assertGreater(rows['AH']['cost']['subtotal_eur'], self.data['budget']['three_month_total_eur'])
        self.assertEqual(rows['AG']['cost']['subtotal_eur'], 13150)
        self.assertEqual(rows['AG']['deposit_eur'], 2400)
        self.assertAlmostEqual(rows['BM4']['cost']['subtotal_eur'], 10859.2)
        self.assertEqual(rows['BM4']['deposit_eur'], 3200)
        self.assertFalse(rows['BM4']['move_in_readiness']['kitchenware'])
        self.assertEqual(rows['BM4']['cost']['basis'], 'published_rate_scenario')
        invalid = copy.deepcopy(self.data)
        invalid['merge_counts']['additional_research_records'] -= 1
        with self.assertRaises(AssertionError):
            validate(invalid)

    def test_generated_files_match_and_have_no_private_paths(self):
        expected = build(self.data)
        for name in ['index.html', 'housing_dashboard.html']:
            self.assertEqual((ROOT / name).read_text(), expected)
        serialized = json.dumps(self.data)
        for private in ['/Users/', 'file://', '__SOYUZ_CONTEXT__', 'pk_live_', '_su_rec', 'send_user_message']:
            self.assertNotIn(private, serialized)


if __name__ == '__main__':
    unittest.main()
