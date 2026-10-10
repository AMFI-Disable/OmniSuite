"""Tests for the import engine.

Tests CSV/JSON import/export, URL import (mocked), and clipboard paste.
"""

import csv
import json
import os
from unittest.mock import MagicMock, patch

import pytest
from omnidebate.core.import_engine import (
    export_to_csv,
    export_to_json,
    import_from_clipboard,
    import_from_csv,
    import_from_json,
    import_from_url,
)

# ─── CSV ──────────────────────────────────────────────────────────────────────


class TestCSVImport:
    def test_import_basic_csv(self, tmp_path):
        csv_file = tmp_path / "cards.csv"
        csv_file.write_text(
            "tag,citation,text,side\n"
            "Economic growth,Smith 2023,Evidence text here,AFF\n"
            "Harms outweigh,Jones 2024,More evidence,NEG\n"
        )
        cards = import_from_csv(str(csv_file))
        assert len(cards) == 2
        assert cards[0]["tag"] == "Economic growth"
        assert cards[0]["side"] == "AFF"
        assert cards[1]["side"] == "NEG"

    def test_import_csv_with_optional_fields(self, tmp_path):
        csv_file = tmp_path / "cards.csv"
        csv_file.write_text("tag,text,side,language,tier\nTest tag,Text,AFF,EN,3\n")
        cards = import_from_csv(str(csv_file))
        assert len(cards) == 1
        assert cards[0].get("language") == "EN"

    def test_import_csv_missing_file(self):
        with pytest.raises((FileNotFoundError, Exception)):
            import_from_csv("/nonexistent/path/cards.csv")

    def test_import_csv_empty_file(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("tag,text,side\n")
        cards = import_from_csv(str(csv_file))
        assert cards == []


class TestCSVExport:
    def test_export_to_csv(self, tmp_path):
        cards = [
            {"tag": "Card 1", "citation": "Smith 2023", "text": "Evidence", "side": "AFF"},
            {"tag": "Card 2", "citation": "Jones 2024", "text": "More text", "side": "NEG"},
        ]
        out_path = str(tmp_path / "export.csv")
        export_to_csv(cards, out_path)
        assert os.path.exists(out_path)
        # Verify content
        with open(out_path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["tag"] == "Card 1"

    def test_export_empty_cards(self, tmp_path):
        out_path = str(tmp_path / "empty.csv")
        export_to_csv([], out_path)
        assert os.path.exists(out_path)


# ─── JSON ─────────────────────────────────────────────────────────────────────


class TestJSONImport:
    def test_import_list_format(self, tmp_path):
        data = [
            {"tag": "Card A", "text": "Evidence A", "side": "AFF", "citation": "X 2023"},
            {"tag": "Card B", "text": "Evidence B", "side": "NEG", "citation": "Y 2024"},
        ]
        json_file = tmp_path / "backup.json"
        json_file.write_text(json.dumps(data))
        cards = import_from_json(str(json_file))
        assert len(cards) == 2
        assert cards[0]["tag"] == "Card A"

    def test_import_vault_dict_format(self, tmp_path):
        data = {"cards": [{"tag": "Card A", "text": "text", "side": "AFF"}]}
        json_file = tmp_path / "vault.json"
        json_file.write_text(json.dumps(data))
        cards = import_from_json(str(json_file))
        assert len(cards) >= 1

    def test_import_json_missing_file(self):
        with pytest.raises((FileNotFoundError, Exception)):
            import_from_json("/nonexistent/cards.json")


class TestJSONExport:
    def test_export_to_json(self, tmp_path):
        cards = [
            {"tag": "Card 1", "text": "Evidence", "side": "AFF", "citation": "Z 2023"},
        ]
        out_path = str(tmp_path / "export.json")
        export_to_json(cards, out_path)
        assert os.path.exists(out_path)
        with open(out_path) as f:
            loaded = json.load(f)
        assert len(loaded) == 1 or "cards" in loaded

    def test_roundtrip_csv_json(self, tmp_path):
        """Cards exported to CSV then imported should preserve key fields."""
        original = [
            {
                "tag": "Roundtrip test",
                "citation": "Author 2023",
                "text": "Evidence text",
                "side": "AFF",
            },
        ]
        csv_path = str(tmp_path / "rt.csv")
        export_to_csv(original, csv_path)
        imported = import_from_csv(csv_path)
        assert imported[0]["tag"] == "Roundtrip test"
        assert imported[0]["side"] == "AFF"


# ─── URL Import ───────────────────────────────────────────────────────────────


class TestURLImport:
    def test_import_from_url_success(self):
        fake_html = """
        <html><head><title>Economic Growth Study</title></head>
        <body>
          <article>
            <p>Researchers found that carbon taxes reduce emissions by 40%.</p>
            <p>The study covered 15 years of data.</p>
          </article>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = fake_html
        mock_response.raise_for_status = MagicMock()

        with patch("requests.get", return_value=mock_response):
            card = import_from_url("https://example.com/study")

        assert isinstance(card, dict)
        assert "tag" in card or "text" in card or "citation" in card

    def test_import_from_url_network_error(self):
        import requests as _req

        with patch("requests.get") as mock_get:
            mock_get.side_effect = _req.RequestException("Connection refused")
            with pytest.raises(ConnectionError):
                import_from_url("https://unreachable.invalid/page")


# ─── Clipboard ────────────────────────────────────────────────────────────────


class TestClipboard:
    def test_import_from_clipboard_macos(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Clipboard text", returncode=0)
            result = import_from_clipboard()
            assert isinstance(result, str)

    def test_import_from_clipboard_fallback(self):
        """Clipboard raises RuntimeError when tool is missing — expected."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("pbpaste not found")
            with pytest.raises((RuntimeError, Exception)):
                import_from_clipboard()


# ─── Keybindings ──────────────────────────────────────────────────────────────


class TestKeybindings:
    def test_load_keybindings_returns_dict(self):
        from omnishared.config.keybindings import load_keybindings

        kb = load_keybindings()
        assert isinstance(kb, dict)

    def test_get_keybinding_returns_string(self):
        from omnishared.config.keybindings import get_keybinding

        result = get_keybinding("quit")
        assert isinstance(result, str)

    def test_get_nonexistent_keybinding(self):
        from omnishared.config.keybindings import get_keybinding

        result = get_keybinding("nonexistent_action_xyz")
        # Should return empty string or default, not crash
        assert isinstance(result, str)

    def test_vim_mode_returns_bool(self):
        from omnishared.config.keybindings import is_vim_mode

        assert isinstance(is_vim_mode(), bool)
