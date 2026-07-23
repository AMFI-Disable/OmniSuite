# Card Management

## Overview

Cards are the fundamental unit of evidence in OmniSuite. Each card represents a piece of evidence with structured metadata for competitive debate.

## Card Structure

| Field | Description | Required |
|-------|-------------|----------|
| **Tag** | Short claim or headline | ✅ |
| **Citation** | Author, year, and source | No |
| **Text** | Full evidence text | ✅ |
| **Side** | AFF (Affirmative) or NEG (Negative) | ✅ |
| **Language** | Content language (EN, DE, ES) | No |
| **Tier** | Priority level (1–3, where 3 = ⭐) | No |
| **Rating** | Quality rating (1–5 stars) | No |
| **Mastery** | Drill familiarity score (0–5) | Auto |

## Adding Cards

Press `a` on the main screen to open the card editor:

- Use **Smart Cite** (`🔑` button) to auto-format citations from author + year fields
- Tags are auto-suggested from citation text as you type

## Searching

Press `s` to open the search screen. OmniSuite supports:

- **Simple search**: Type any term to search across tags, citations, and text
- **Boolean search**: Use `AND`, `OR`, `NOT` operators
  - `economy AND growth` — cards containing both terms
  - `trade OR tariff` — cards containing either term
  - `economy AND NOT recession` — economy cards without recession
- **Fuzzy matching**: Automatically finds close matches (75% similarity threshold)
- **FTS5 search**: Full-text search with ranking via SQLite FTS5

## Tagging System

Cards support multiple custom tags for flexible organization:

- Tags are lowercase, normalized
- Filter cards by tag from the search screen
- View all tags and their card counts

## Rating Cards

Rate cards 1–5 stars to mark evidence quality:

- ⭐ = Weak evidence
- ⭐⭐⭐ = Solid evidence
- ⭐⭐⭐⭐⭐ = Tournament-ready

## Card History

Every edit to a card is tracked:

- View the full edit history for any card
- See what changed, when, and the before/after values

## Bulk Operations

Select multiple cards for batch operations:

- Move cards between motions
- Delete multiple cards at once
- Export selected cards only

## Card Templates

Pre-defined card structures per debate format help ensure consistency in evidence cutting.
