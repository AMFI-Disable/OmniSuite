# Evidence Vault CLI 🏛️

A command-line interface designed to store, filter, and instantly retrieve AFF and NEG debate cards during crossfire or prep time. 

## ⚙️ Setup
Ensure you have Python installed. This tool uses only built-in libraries, so no external dependencies or `pip installs` are required. Just clone the repo and run it.

## 🚀 Usage Guide

### Adding Evidence
Ingest new cards directly into your local database using the interactive `add` command.

```bash
$ python3 vault.py add
> Tag: Standardized testing flaws
> Citation: Miller 2026
> Side: AFF
> Text: [Paste Evidence Here]
```

### Finding Evidence for Debates
Find exactly what you need in the heat of a debate using the `search` command. You can filter by side and target specific keywords:
```bash
python3 vault.py search --side AFF --keyword "predict"
```

### Deleting Evidence
```bash
$ python3 vault.py delete
> Enter the ID of the card to purge: 1
```

### Exporting for Tournaments
```bash
python3 vault.py export --side AFF --filename aff_brief.txt
```
