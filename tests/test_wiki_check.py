import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import wiki_check


class WikiCheckTests(unittest.TestCase):
    def paths_for(self, root: Path):
        knowledge = root / "knowledge"
        return {
            "ROOT": root,
            "KNOWLEDGE": knowledge,
            "INDEX": knowledge / "index.md",
            "LOG": knowledge / "log.md",
            "WIKI": knowledge / "wiki",
            "SOURCES": knowledge / "sources",
        }

    def make_fixture(
        self,
        root: Path,
        *,
        page: str = "---\ntype: concept\nstatus: current\nupdated: 2026-09-25\nsources:\n---\n# Page\n",
        index: str = "# index\n",
        log: str = "## [2026-09-25] lint | test\n",
        page_name: str = "page.md",
    ) -> None:
        knowledge = root / "knowledge"
        (knowledge / "wiki").mkdir(parents=True)
        (knowledge / "sources").mkdir(parents=True)
        (knowledge / "index.md").write_text(index, encoding="utf-8")
        (knowledge / "README.md").write_text("# readme\n", encoding="utf-8")
        (knowledge / "log.md").write_text(log, encoding="utf-8")
        (knowledge / "wiki" / page_name).write_text(page, encoding="utf-8")

    def run_fixture(self, root: Path) -> int:
        with mock.patch.multiple(wiki_check, **self.paths_for(root)):
            return wiki_check.run()

    def test_repository_wiki_is_structurally_healthy(self):
        self.assertEqual(wiki_check.run(), 0)

    def test_missing_required_knowledge_path_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(root)
            (root / "knowledge" / "sources").rmdir()
            self.assertEqual(self.run_fixture(root), 1)

    def test_missing_frontmatter_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(root, page="# Page\n")
            self.assertEqual(self.run_fixture(root), 1)

    def test_unterminated_frontmatter_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(root, page="---\ntype: concept\nstatus: current\n")
            self.assertEqual(self.run_fixture(root), 1)

    def test_missing_required_frontmatter_key_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(
                root,
                page="---\ntype: concept\nstatus: current\nupdated: 2026-09-25\n---\n# Page\n",
            )
            self.assertEqual(self.run_fixture(root), 1)

    def test_unsupported_type_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(
                root,
                page="---\ntype: unsupported\nstatus: current\nupdated: 2026-09-25\nsources:\n---\n# Page\n",
            )
            self.assertEqual(self.run_fixture(root), 1)

    def test_unsupported_status_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(
                root,
                page="---\ntype: concept\nstatus: unknown\nupdated: 2026-09-25\nsources:\n---\n# Page\n",
            )
            self.assertEqual(self.run_fixture(root), 1)

    def test_broken_relative_link_from_wiki_page_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(
                root,
                page="---\ntype: concept\nstatus: current\nupdated: 2026-09-25\nsources:\n---\n[missing](nope.md)\n",
            )
            self.assertEqual(self.run_fixture(root), 1)

    def test_broken_index_link_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(root, index="[missing](nope.md)\n")
            self.assertEqual(self.run_fixture(root), 1)

    def test_malformed_dated_log_entry_is_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_fixture(root, log="## 2026-09-25 malformed\n")
            self.assertEqual(self.run_fixture(root), 1)


if __name__ == "__main__":
    unittest.main()
