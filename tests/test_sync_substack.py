"""Tests for fail-closed, append-only Substack catalog reconciliation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_substack as sync


def item(n, date, url_suffix=None, title=None):
    return {
        "date": date,
        "datetime_utc": date + "T16:00:00Z",
        "title": title or f"Test source article {n}",
        "subtitle": "View this post on the web at https://theminusoneguarantee.substack.com/p/test-" + str(n),
        "url": "https://theminusoneguarantee.substack.com/p/" + (url_suffix or f"test-{n}"),
    }


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.base = {
            "publication": "The -1 Guarantee",
            "snapshot_date": "2026-11-10",
            "last_recorded_publication_date": "2026-11-10",
            "count": 1,
            "records": [{"id": "SUB-001", "date": "2026-11-10", "title": "Editorial map verified title", "subtitle": "Verified original subtitle", "url": item(1, "2026-11-10")["url"]}],
        }
        self.source = [item(1, "2026-11-10")]

    def test_noop_does_not_touch_existing(self):
        result, added = sync.reconcile(self.base, self.source)
        self.assertEqual(added, 0)
        self.assertIs(result, self.base)

    def test_append_and_preserve_verified_metadata(self):
        source = self.source + [item(2, "2026-11-11")]
        original = json.dumps(self.base, sort_keys=True)
        result, added = sync.reconcile(self.base, source, today="2026-11-11")
        self.assertEqual((added, result["count"]), (1, 2))
        self.assertEqual(result["records"][0]["title"], "Editorial map verified title")
        self.assertEqual(result["records"][0]["subtitle"], "Verified original subtitle")
        self.assertEqual(result["records"][1]["id"], "SUB-002")
        self.assertEqual(result["records"][1]["subtitle"], "")
        self.assertIn("provvisorio", result["records"][1]["metadata_status"])
        self.assertEqual(json.dumps(self.base, sort_keys=True), original)
        md = sync.render_markdown(result)
        self.assertIn("**2 articoli**", md)
        self.assertIn("SUB-002", md)

    def test_reject_upstream_missing_existing(self):
        with self.assertRaisesRegex(sync.SyncError, "non contiene"):
            sync.reconcile(self.base, [item(2, "2026-11-11")])

    def test_reject_new_historical_post(self):
        with self.assertRaisesRegex(sync.SyncError, "storico"):
            sync.reconcile(self.base, self.source + [item(2, "2026-10-19")])

    def test_reject_existing_date_same_day(self):
        with self.assertRaisesRegex(sync.SyncError, "stesso giorno"):
            sync.reconcile(self.base, self.source + [item(2, "2026-11-10")])

    def test_reject_duplicate_urls(self):
        with self.assertRaisesRegex(sync.SyncError, "duplicato"):
            sync.reconcile(self.base, self.source + self.source)

    def test_reject_noncanonical_urls(self):
        altered = item(2, "2026-11-11")
        altered["url"] += "?utm_source=email"
        with self.assertRaisesRegex(sync.SyncError, "canonico"):
            sync.reconcile(self.base, self.source + [altered])

    def test_multiple_new_rows_ordered_and_ids(self):
        source = self.source + [item(3, "2026-11-13"), item(2, "2026-11-12")]
        updated, added = sync.reconcile(self.base, source, today="2026-11-13")
        self.assertEqual(added, 2)
        self.assertEqual([r["id"] for r in updated["records"]], ["SUB-001", "SUB-002", "SUB-003"])
        self.assertEqual(updated["last_recorded_publication_date"], "2026-11-13")

    def test_warn_truncated_title_and_escape_markdown(self):
        shortened = item(2, "2026-11-11", title="Truncated title…")
        shortened["title"] = "Research | Action…"
        updated, _ = sync.reconcile(self.base, self.source + [shortened])
        self.assertTrue(updated["records"][-1]["title_may_be_truncated"])
        markdown = sync.render_markdown(updated)
        self.assertIn("Research \\| Action… *(titolo da verificare)*", markdown)

    def test_actual_file_write_and_idempotency(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "fonti").mkdir()
            (root / sync.JSON_FILE).write_text(json.dumps(self.base), encoding="utf-8")
            (root / sync.MARKDOWN_FILE).write_text("OLD MARKDOWN", encoding="utf-8")
            source = root / "source.json"
            source.write_text(json.dumps(self.source + [item(2, "2026-11-11")]), encoding="utf-8")
            self.assertEqual(sync.sync(source, root), 1)
            self.assertEqual(sync.sync(source, root), 0)
            self.assertIn("SUB-002", (root / sync.MARKDOWN_FILE).read_text(encoding="utf-8"))
            self.assertEqual(json.loads((root / sync.JSON_FILE).read_text(encoding="utf-8"))["count"], 2)


if __name__ == "__main__":
    unittest.main()
