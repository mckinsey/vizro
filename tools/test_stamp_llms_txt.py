"""Unit tests for ``tools/stamp_llms_txt.py``.

Run with either::

    python tools/test_stamp_llms_txt.py
    python -m unittest tools/test_stamp_llms_txt.py

No third-party dependencies; pure ``unittest`` + ``tempfile`` so this
works in any minimal environment (including a fresh RTD build image).
"""

import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from stamp_llms_txt import compute_versioned_url, stamp_llms_txt


class ComputeVersionedURLTests(unittest.TestCase):
    """Cover the URL-rewriting helper used to stamp the build version."""

    def test_vizro_core_stable_to_tag(self):
        self.assertEqual(
            compute_versioned_url(
                "https://vizro.readthedocs.io/en/stable/",
                "0.1.58",
            ),
            "https://vizro.readthedocs.io/en/0.1.58/",
        )

    def test_subproject_latest_to_prefixed_tag(self):
        self.assertEqual(
            compute_versioned_url(
                "https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/",
                "vizro-mcp-0.1.4",
            ),
            "https://vizro.readthedocs.io/projects/vizro-mcp/en/vizro-mcp-0.1.4/",
        )

    def test_stable_to_stable_is_identity(self):
        # When the build version matches the placeholder slug, stamping
        # is a no-op and the result equals the input.
        placeholder = "https://vizro.readthedocs.io/en/stable/"
        self.assertEqual(compute_versioned_url(placeholder, "stable"), placeholder)

    def test_latest_to_latest_is_identity(self):
        placeholder = "https://vizro.readthedocs.io/projects/vizro-experimental/en/latest/"
        self.assertEqual(compute_versioned_url(placeholder, "latest"), placeholder)

    def test_handles_version_with_dots_and_dashes(self):
        # RTD slugs are derived from git tags so can contain dots and
        # dashes; ensure we don't munge them.
        self.assertEqual(
            compute_versioned_url(
                "https://vizro.readthedocs.io/projects/vizro-ai/en/latest/",
                "vizro-ai-0.4.0-rc1",
            ),
            "https://vizro.readthedocs.io/projects/vizro-ai/en/vizro-ai-0.4.0-rc1/",
        )


class StampLLMsTxtTests(unittest.TestCase):
    """Integration-style tests for the full ``stamp_llms_txt`` flow.

    Each test uses a TemporaryDirectory as the ``site_dir`` so nothing
    on disk is touched and tests are fully isolated.
    """

    PLACEHOLDER = "https://vizro.readthedocs.io/projects/vizro-mcp/en/latest/"
    SAMPLE_BODY = (
        "# Vizro-MCP\n\n"
        f"- [Tutorial]({PLACEHOLDER}pages/tutorials/first-dashboard-tutorial/): X\n"
        f"- [Guide]({PLACEHOLDER}pages/guides/use-data/): Y\n"
    )

    def _make_site(self, tmp: str, body: str | None = None) -> Path:
        site = Path(tmp)
        (site / "llms.txt").write_text(self.SAMPLE_BODY if body is None else body, encoding="utf-8")
        return site

    def test_no_op_when_readthedocs_version_unset(self):
        with TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {}, clear=True):
            site = self._make_site(tmp)
            original = (site / "llms.txt").read_text(encoding="utf-8")
            self.assertEqual(stamp_llms_txt(self.PLACEHOLDER, site), 0)
            self.assertEqual((site / "llms.txt").read_text(encoding="utf-8"), original)

    def test_no_op_when_version_matches_placeholder(self):
        # `latest` build of a project whose placeholder uses `/en/latest/`
        # leaves the file unchanged.
        with TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"READTHEDOCS_VERSION": "latest"}):
            site = self._make_site(tmp)
            original = (site / "llms.txt").read_text(encoding="utf-8")
            self.assertEqual(stamp_llms_txt(self.PLACEHOLDER, site), 0)
            self.assertEqual((site / "llms.txt").read_text(encoding="utf-8"), original)

    def test_stamps_tagged_version_url(self):
        with TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"READTHEDOCS_VERSION": "vizro-mcp-0.1.4"}):
            site = self._make_site(tmp)
            self.assertEqual(stamp_llms_txt(self.PLACEHOLDER, site), 0)
            stamped = (site / "llms.txt").read_text(encoding="utf-8")
            self.assertNotIn(self.PLACEHOLDER, stamped)
            self.assertIn(
                "https://vizro.readthedocs.io/projects/vizro-mcp/en/vizro-mcp-0.1.4/",
                stamped,
            )
            # All occurrences of the placeholder should be replaced (2 in
            # SAMPLE_BODY); count by recomputing on the stamped body.
            self.assertEqual(
                stamped.count("https://vizro.readthedocs.io/projects/vizro-mcp/en/vizro-mcp-0.1.4/"),
                2,
            )

    def test_no_op_when_placeholder_absent_from_file(self):
        # A file without any matching URL should be left untouched
        # without error.
        with TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"READTHEDOCS_VERSION": "vizro-mcp-0.1.4"}):
            body = "# Vizro-MCP\n\nNo placeholder URLs here.\n"
            site = self._make_site(tmp, body=body)
            self.assertEqual(stamp_llms_txt(self.PLACEHOLDER, site), 0)
            self.assertEqual((site / "llms.txt").read_text(encoding="utf-8"), body)

    def test_missing_site_llms_txt_is_an_error(self):
        with TemporaryDirectory() as tmp, mock.patch.dict(os.environ, {"READTHEDOCS_VERSION": "vizro-mcp-0.1.4"}):
            empty_site = Path(tmp)
            self.assertEqual(stamp_llms_txt(self.PLACEHOLDER, empty_site), 1)


if __name__ == "__main__":
    unittest.main()
