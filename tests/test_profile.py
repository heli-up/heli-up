import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('profile', Path(__file__).resolve().parents[1] / 'scripts/update_profile.py')
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)
NOW = profile.stamp('2026-11-02T06:00:00Z')


class ProfileTests(unittest.TestCase):
    def event(self, **kwargs):
        return {'type': 'PushEvent', 'created_at': '2026-11-02T06:00:00Z', 'actor': {'login': 'heli-up'}, 'repo': {'name': 'heli-up/QuantAgent'}, **kwargs}

    def test_svg_all_time_and_theme_combinations(self):
        for month in (1, 4, 7, 10):
            for hour in (6, 12, 18, 23):
                for dark in (False, True):
                    now = NOW.replace(month=month, hour=hour)
                    documents = [profile.header(now, dark), profile.footer(now, [], NOW.isoformat(), dark)]
                    documents += [profile.card(key, dark) for key in profile.PROJECTS]
                    documents += [profile.mobile_header(now, dark)]
                    documents += [profile.mobile_card(key, dark) for key in profile.PROJECTS]
                    for text in documents:
                        root = ET.fromstring(text)
                        self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
                        self.assertNotIn('<script', text)
                        self.assertNotIn('foreignObject', text)
                        self.assertIn('prefers-reduced-motion', text)
                        self.assertLess(len(text.encode()), 14000)

    def test_scene_follows_shanghai_time(self):
        self.assertEqual(profile.environment(profile.stamp('2026-11-02T16:00:00Z'))[:2], ('NIGHT', 'AUTUMN'))
        self.assertEqual(profile.environment(profile.stamp('2026-12-02T04:00:00Z'))[:2], ('DAY', 'WINTER'))

    def test_count_boundaries_use_local_dates(self):
        events = [self.event(created_at='2026-11-01T16:01:00Z'), self.event(created_at='2026-10-19T15:59:00Z'), self.event(created_at='2026-11-03T00:00:00Z')]
        counts = profile.activity_counts(events, NOW)
        self.assertEqual(sum(counts), 1)
        self.assertEqual(counts[-1], 1)
        self.assertIsNone(profile.activity_counts(None, NOW))

    def test_feed_uses_first_party_development_events(self):
        events = [self.event(type='WatchEvent'), self.event(actor={'login': 'other'}), self.event(repo={'name': 'heli-up/heli-up'}), self.event(repo={'name': 'evil/](javascript:alert(1))'}), self.event(), self.event()]
        text = profile.activity_lines(events)
        self.assertEqual(text.count('推送代码'), 1)
        self.assertNotIn('javascript:', text)
        self.assertNotIn('other', text)

    def test_readme_survives_api_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = 'before\n' + profile.START + '\nkeep me\n' + profile.END + '\nafter'
            (root / 'README.md').write_text(text, encoding='utf-8')
            state = {'events': [self.event()], 'fetched_at': NOW.isoformat()}
            (root / '.github').mkdir()
            (root / '.github/profile-state.json').write_text(json.dumps(state), encoding='utf-8')
            def fail():
                raise OSError('simulated network outage')
            result = profile.refresh(root, NOW, loader=fail)
            self.assertFalse(result['fresh'])
            self.assertTrue(result['has_snapshot'])
            self.assertEqual((root / 'README.md').read_text(encoding='utf-8'), text)
            self.assertTrue((root / 'assets/header.svg').exists())
            self.assertEqual(json.loads((root / '.github/profile-state.json').read_text()), state)

    def test_no_cache_is_honest_and_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'README.md').write_text(profile.START + '\nexisting\n' + profile.END, encoding='utf-8')
            result = profile.refresh(root, NOW, offline=True)
            self.assertFalse(result['has_snapshot'])
            self.assertIn('UNAVAILABLE', (root / 'assets/footer.svg').read_text(encoding='utf-8'))

    def test_fresh_feed_replaces_only_marked_region(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'README.md').write_text('prefix\n' + profile.START + '\nold\n' + profile.END + '\nsuffix', encoding='utf-8')
            profile.refresh(root, NOW, loader=lambda: [self.event()])
            text = (root / 'README.md').read_text(encoding='utf-8')
            self.assertTrue(text.startswith('prefix\n'))
            self.assertTrue(text.endswith('\nsuffix'))
            self.assertIn('QuantAgent', text)

    def test_broken_markers_prevent_partial_updates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'README.md').write_text('no markers', encoding='utf-8')
            with self.assertRaises(ValueError):
                profile.refresh(root, NOW, offline=True)
            self.assertFalse((root / 'assets').exists())


if __name__ == '__main__':
    unittest.main()
