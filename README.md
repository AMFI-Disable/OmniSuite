# Evidence Vault CLI 🏛️

A command-line interface designed to store, filter, and instantly retrieve AFF and NEG debate cards during crossfire or prep time. 

## ⚙️ Setup
Ensure you have Python installed. This tool uses only built-in libraries, so no external dependencies or `pip installs` are required. Just clone the repo and run it.

## 🚀 Usage Guide

### The "Motion First" Workflow
This tool is built on a **Multi-Tenant System**. Instead of clumping all debate evidence into one massive file, the vault organizes your cards into independent JSON databases located in the `debates/` folder. This means you can maintain separate, logical isolation between wildly different tournament topics!

Upon executing any command, the vault will prompt you to initialize or select a motion.

**Example selection screen:**
```text
--- Available Motions ---
[1] Climate Change Policy
[2] Universal Basic Income

Select a motion by number, or type a new name to initialize a new debate vault: 
```
Once your motion is established, all `add`, `search`, `delete`, and `export` functions are **temporarily locked** strictly to that motion's corresponding storage file inside `debates/`.

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
The vault will automatically name your output file based on your currently active motion (e.g., `export_school_uniforms.txt`) unless you provide a custom one.

```bash
python3 vault.py export --side AFF
```
