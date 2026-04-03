# Evidence Vault CLI 🏛️

A command-line interface designed to store, filter, and instantly retrieve AFF and NEG debate cards during crossfire or prep time. 

## ⚙️ Setup
Ensure you have Python installed. This tool uses only built-in libraries, so no external dependencies or `pip installs` are required. Just clone the repo and run it.

## 🚀 Usage Guide

## 🎨 High-Visibility Architecture
The Vault is now a **Debate Command Center**. All cards rendered dynamically adapt ANSI coloring: **AFF** cards display in stark bold Green, and **NEG** cards display in red. 

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

### The Omni-Search Protocol
Find exactly what you need in the heat of a debate. You can choose to search your current active motion, or deploy a **Global Search** to scrape every single motion file in your `debates/` folder.
```bash
$ python3 vault.py search
> Search scope [1] Current Motion [2] Global: 2
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

### ⏱️ Chronos Timer Module
Keep track of your speech and prep time without ever leaving your brief! Launch the timer either straight from the setup menu or via terminal:
```bash
python3 vault.py timer
```
The timer runs visibly in your terminal without clogging history. Once finished, it will beep (`\\a`) and flash an alert! 
**Shortcut:** Press `Ctrl+C` at any time to immediately cancel or pause a running timer and return safely back to the Command Center menu.

### ⚔️ Gladiator Drill Mode
Test your memory and lock in your strategy during prep time. Run Drill Mode to randomly pull up the tag and source of an evidence card from your active motion without showing the text:
```bash
python3 vault.py drill
```
Hit **Enter** to reveal the actual evidence text to check if you successfully recalled the arguments by heart!
