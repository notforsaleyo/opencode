"""Failure-preservation checks and opt-in live API transfer round trip."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import uuid


spec = importlib.util.spec_from_file_location(
    "handoff", Path(__file__).resolve().parents[1] / "scripts" / "handoff.py"
)
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir="/tmp/opencode")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = {
            "info": {"id": "ses_test", "title": "테스트", "location": {"directory": str(self.root)}, "time": {"created": 1, "updated": 1}},
            "messages": [{"id": "msg_test", "type": "user", "text": "보존할 내용", "time": {"created": 1}}],
        }
        with patch.object(handoff, "api", side_effect=[{"data": self.data}, {"version": "2.0.18"}]):
            self.saved = handoff.export(self.root, "ses_test")
        self.entry = self.root / "handoff" / self.saved["id"]

    def expire(self):
        path = self.entry / "metadata.json"
        metadata = json.loads(path.read_text())
        metadata["expiresAt"] = "2000-01-01T00:00:00Z"
        path.write_text(json.dumps(metadata))

    def test_modified_transcript_is_neither_restored_nor_removed(self):
        (self.entry / "session.json").write_text('{"info":{},"messages":[]}')
        with patch.object(handoff, "import_session") as importer:
            with self.assertRaises(handoff.HandoffError):
                handoff.restore(self.root, self.saved["id"], str(self.root))
            importer.assert_not_called()
        with self.assertRaises(handoff.HandoffError):
            handoff.remove(self.root, self.saved["id"])
        self.assertTrue((self.entry / "session.json").exists())

    def test_export_has_no_expiry(self):
        self.assertIsNone(self.saved["expiresAt"])
        self.assertEqual(handoff.read_entry(self.root, self.saved["id"])[1], self.data)

    def test_cleanup_keeps_legacy_expired_backups(self):
        self.assertEqual(handoff.cleanup(self.root)["removed"], [])
        self.expire()
        self.assertEqual(handoff.cleanup(self.root, [self.saved["id"]])["removed"], [])
        self.assertEqual(handoff.cleanup(self.root)["removed"], [])
        self.assertTrue(self.entry.exists())
        self.assertEqual(handoff.read_entry(self.root, self.saved["id"])[1], self.data)
        self.assertFalse(handoff.entries(self.root)[0]["expired"])
        self.assertIsNone(handoff.entries(self.root)[0]["expiresAt"])

    def test_backup_without_expiry_field_can_be_read(self):
        path = self.entry / "metadata.json"
        metadata = json.loads(path.read_text())
        metadata.pop("expiresAt")
        path.write_text(json.dumps(metadata))
        self.assertEqual(handoff.read_entry(self.root, self.saved["id"])[1], self.data)
        self.assertEqual(handoff.cleanup(self.root)["removed"], [])

    def test_unknown_files_prevent_cleanup(self):
        self.expire()
        (self.entry / "user-notes.md").write_text("사용자 작업")
        with self.assertRaises(handoff.HandoffError):
            handoff.cleanup(self.root)
        self.assertTrue((self.entry / "user-notes.md").exists())

    def test_import_failure_keeps_backup(self):
        with patch.object(handoff, "api", side_effect=handoff.APIError("SessionNotFoundError")):
            with patch.object(handoff, "import_session", side_effect=handoff.HandoffError("unavailable")):
                with self.assertRaises(handoff.HandoffError):
                    handoff.restore(self.root, self.saved["id"], str(self.root))
        self.assertEqual(handoff.read_entry(self.root, self.saved["id"])[1], self.data)

    def test_existing_unrelated_session_is_not_overwritten(self):
        with patch.object(handoff, "api", return_value={"data": {"metadata": {}}}):
            with patch.object(handoff, "import_session") as importer:
                with self.assertRaises(handoff.HandoffError):
                    handoff.restore(self.root, self.saved["id"], str(self.root))
                importer.assert_not_called()
        self.assertTrue(self.entry.exists())

    def test_paths_and_symlinks_cannot_escape_store(self):
        with self.assertRaises(handoff.HandoffError):
            handoff.remove(self.root, "../../other")
        session = self.entry / "session.json"
        original = session.read_bytes()
        session.unlink()
        outside = self.root / "outside.json"
        outside.write_bytes(original)
        session.symlink_to(outside)
        with self.assertRaises(handoff.HandoffError):
            handoff.remove(self.root, self.saved["id"])
        self.assertEqual(outside.read_bytes(), original)


@unittest.skipUnless(os.environ.get("HANDOFF_LIVE_TEST") == "1", "opt-in local service test")
class LiveTransferTests(unittest.TestCase):
    def test_large_compacted_child_session_round_trip(self):
        # No prompts are submitted and no model is invoked by this test.
        with tempfile.TemporaryDirectory(prefix="handoff-test-", dir="/tmp/opencode") as temporary:
            root = Path(temporary)
            source_dir = root / "source"
            target_dir = root / "target"
            source_dir.mkdir()
            target_dir.mkdir()
            ids = []
            try:
                request = {"title": "handoff-test-parent", "location": {"directory": str(source_dir)}}
                process = subprocess.run(
                    ["opencode", "api", "post", "/api/session", "--data", json.dumps(request)],
                    check=True, capture_output=True, text=True,
                )
                parent = json.loads(process.stdout)["data"]
                ids.append(parent["id"])
                info = json.loads(json.dumps(parent))
                info["id"] = "ses_handoff_test_" + uuid.uuid4().hex
                ids.append(info["id"])
                info["parentID"] = parent["id"]
                info["title"] = "handoff-test-" + uuid.uuid4().hex
                info["time"]["archived"] = info["time"]["created"]
                messages = [
                    {"id": "msg_" + uuid.uuid4().hex, "type": "user", "text": "긴 대화 검증\n" * 30000, "time": {"created": 1}},
                    {"id": "msg_" + uuid.uuid4().hex, "type": "assistant", "agent": "build", "model": {"providerID": "openai", "id": "test"}, "time": {"created": 2, "completed": 3}, "content": [{"type": "text", "text": "보존되어야 하는 답변"}]},
                    {"id": "msg_" + uuid.uuid4().hex, "type": "compaction", "status": "completed", "reason": "manual", "time": {"created": 4}, "summary": "압축된 대화 요약 보존", "recent": ""},
                ]
                handoff.import_session({"info": info, "messages": messages, "location": {"directory": str(source_dir)}})
                saved = handoff.export(root, info["id"])
                target_id = "ses_handoff_" + handoff.digest(saved["id"].encode())[:32]
                ids.append(target_id)
                result = handoff.restore(root, saved["id"], str(target_dir))
                self.assertTrue(result["verified"])
                self.assertEqual(result["status"], "restored")
                exported = handoff.api("get", f"/api/experimental/session/{target_id}/export?sanitize=false")["data"]
                self.assertEqual(
                    [{k: v for k, v in message.items() if k != "id"} for message in exported["messages"]],
                    [{k: v for k, v in message.items() if k != "id"} for message in messages],
                )
                self.assertTrue(set(m["id"] for m in messages).isdisjoint(m["id"] for m in exported["messages"]))
                self.assertNotIn("parentID", exported["info"])
                self.assertNotIn("archived", exported["info"]["time"])
                self.assertEqual(exported["info"]["location"]["directory"], str(target_dir))
                self.assertEqual(handoff.restore(root, saved["id"], str(target_dir))["status"], "already_restored")
                with self.assertRaises(handoff.HandoffError):
                    handoff.restore(root, saved["id"], str(source_dir))
                handoff.remove(root, saved["id"])
                self.assertEqual(handoff.entries(root), [])
                # Consuming a backup does not delete either actual session.
                self.assertEqual(handoff.api("get", "/api/session/" + target_id)["data"]["id"], target_id)
                self.assertEqual(handoff.api("get", "/api/session/" + info["id"])["data"]["id"], info["id"])
            finally:
                for session_id in reversed(ids):
                    try:
                        handoff.api("delete", "/api/session/" + session_id)
                    except handoff.APIError as exc:
                        if exc.tag != "SessionNotFoundError":
                            raise


if __name__ == "__main__":
    unittest.main()
