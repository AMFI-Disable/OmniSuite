# Evidence Vault CLI 🏛️

A command-line interface designed to store, filter, and instantly retrieve AFF and NEG debate cards during crossfire or prep time. 

## ⚙️ Setup
Ensure you have Python installed. This tool uses only built-in libraries, so no external dependencies or `pip installs` are required. Just clone the repo and run it.

## 🚀 Usage Guide

### Adding Evidence
Ingest new cards directly into your local database using the `add` command. You must provide the tag, citation, side, and text.

```bash
python vault.py add --tag "Standardized tests fail to predict success" --cite "Smith 25" --side "AFF" --text "Soft skills outpace academic scores by 40%."
```

### Finding Evidence for Debates
Find exactly what you need in the heat of a debate using the `search` command. You can filter by side and target specific keywords:
```bash
python3 vault.py search --side AFF --keyword "predict"
```

### Deleting Evidence
```bash
python3 vault.py delete --id 1
```

### Exporting for Tournaments
```bash
python3 vault.py export --side AFF --filename aff_brief.txt
```
