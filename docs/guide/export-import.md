# Export & Import

## Supported Export Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| **Verbatim DOCX** | `.docx` | Standard Verbatim debate template formatting |
| **CaseXC DOCX** | `.docx` | CaseXC styling with structured headings |
| **Standard Brief** | `.md` | Clean markdown brief |
| **Interactive Brief** | `.html` | Web-based brief with collapsible sections |
| **CSV** | `.csv` | Spreadsheet-compatible card export |
| **JSON** | `.json` | Full vault backup with all metadata |

## Exporting

### From The Main Screen
Press `x` to open the export dialog. Select:
1. Target motion
2. Export format
3. Card filters (side, tier, rating)
4. Output directory

### Command-Line Export
```bash
omnisuite --app format --fix
```

## Importing

### DOCX Import
Press `i` to import cards from `.docx` files. OmniSuite extracts:
- Tagged headings as card tags
- Citation blocks as citations
- Body text as evidence text
- Formatting (bold, underline, italic) is preserved

### CSV Import
Import cards from spreadsheet format. Required columns:
- `tag` — Card tag/claim
- `text` — Evidence text
- `side` — AFF or NEG

Optional columns: `citation`, `language`, `tier`, `rating`

### JSON Import
Restore from a full vault backup. Imports all cards with metadata.

### URL Import
Paste a URL to auto-extract article text:
1. Fetches the page content
2. Extracts article text via BeautifulSoup
3. Auto-generates a citation from the page title and URL
4. Creates a new card with the extracted text

### PDF Import
Extract text from PDF evidence files for import.

### Clipboard Paste
Paste text directly from clipboard as a new card.

## Export History

All exports are logged. View your export history from the analytics dashboard to track what was exported, when, and in what format.
