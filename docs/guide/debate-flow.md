# Debate Flow

## Overview

The **Flow Screen** is a multi-column interface for tracking arguments during a live debate round. Each column represents a speech, and you record arguments as they're made.

No other TUI tool offers debate flowing — this is unique to OmniSuite.

## Launching The Flow

From the main screen, press `f` to open the Flow Screen.

## Layout

The flow is organized as a table of columns:

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  Pro Case   │  Con Case   │ Pro Rebuttal│ Con Rebuttal│
├─────────────┼─────────────┼─────────────┼─────────────┤
│ Arg 1       │ Arg A       │ ← Resp to A │ ← Resp to 1│
│ Arg 2       │ Arg B       │ ← Resp to B │             │
│ Arg 3       │             │ New arg     │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

Columns are color-coded:
- **Blue** = Pro/Affirmative side
- **Red** = Con/Negative side

## Keyboard Controls

| Key | Action |
|-----|--------|
| `Tab` | Move to next column |
| `Shift+Tab` | Move to previous column |
| `↑/↓` | Navigate entries |
| `Enter` | Add new entry |
| `e` | Edit selected entry |
| `d` | Delete selected entry |
| `l` | Link entry to a card in the vault |
| `x` | Export flow to markdown |
| `Escape` | Back to main |

## Response Tracking

When adding an entry, you can mark it as a response to an argument in another column. This creates a visual `←` indicator showing argument-response chains.

## Linking To Cards

Press `l` on any flow entry to link it to a card in your vault. Linked entries show a `🔗` icon and you can jump directly to the linked card.

## Exporting

Press `x` to export the flow as a markdown table. The export includes:
- All columns with their entries
- Response indicators
- Linked card references
