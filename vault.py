import json
import argparse
import os
import glob
import time
import sys
import random
import textwrap
import shutil
import difflib
import re
import datetime

DEBATES_DIR = "debates"
BACKUPS_DIR = "backups"
EXPORTS_DIR = "exports"
TRASH_FILE = os.path.join(DEBATES_DIR, ".trash.json")
DB_FILE = os.path.join(DEBATES_DIR, "default.json")
ACTIVE_MOTION = "Default"
SESSION_CARDS_EDITED = 0
SESSION_MOTIONS_ARCHIVED = 0


# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD_WHITE = '\033[1;37m'
HIGHLIGHT_YELLOW = '\033[1;33m'
RESET = '\033[0m'
BG_GREEN_BLACK_TEXT = '\033[102;30m'
BG_RED_BLACK_TEXT = '\033[101;30m'
UNDERLINE_CYAN = '\033[4;96m'

def print_banner():
    banner = f"""
{CYAN}
 \ \    / /\\   | |  | | |    |__   __|
  \ \  / /  \\  | |  | | |       | |   
   \ \/ / /\ \\ | |  | | |       | |   
    \  / ____ \\| |__| | |____   | |   
     \/_/    \\_\\\\____/|______|  |_|   
{RESET}
"""
    print(banner)

def run_setup_dirs():
    for d in [DEBATES_DIR, BACKUPS_DIR, EXPORTS_DIR, os.path.join(DEBATES_DIR, "archives")]:
        if not os.path.exists(d):
            os.makedirs(d)

def select_motion():
    global DB_FILE, ACTIVE_MOTION
    run_setup_dirs()
    
    files = glob.glob(os.path.join(DEBATES_DIR, "*.json"))
    # exclude trash
    files = [f for f in files if not f.endswith(".trash.json")]
    
    motions = []
    for f in files:
        basename = os.path.basename(f)
        name = basename[:-5].replace("_", " ").title()
        motions.append({"name": name, "file": f})
        
    print(f"\n{CYAN}--- Available Motions ---{RESET}")
    for i, m in enumerate(motions):
        count = len(load_vault_from_file(m['file']))
        print(f"[{i+1}] {m['name']} ({count} cards)")
    
    print(f"\n[R] Rename a Motion  |  [D] Delete a Motion  |  [A] Archive a Motion")
    
    choice = input("\nSelect a motion by number, or type a new name to initialize a new debate vault, or choose R/D/A: ").strip()
    
    if choice.upper() == 'R':
        target = input("Enter the number of the motion to rename: ").strip()
        if target.isdigit() and 1 <= int(target) <= len(motions):
            old_file = motions[int(target)-1]['file']
            new_name = input("Enter new motion name: ").strip()
            if new_name:
                new_filename = new_name.lower().replace(" ", "_").replace("/", "") + ".json"
                os.rename(old_file, os.path.join(DEBATES_DIR, new_filename))
                print(f"✅ Motion renamed to {new_name}.")
        return select_motion()
    elif choice.upper() == 'D':
        target = input("Enter the number of the motion to delete: ").strip()
        if target.isdigit() and 1 <= int(target) <= len(motions):
            old_file = motions[int(target)-1]['file']
            confirm = input(f'{RED}Type "CONFIRM" to permanently erase this motion: {RESET}')
            if confirm == "CONFIRM":
                os.remove(old_file)
                print(f"✅ Motion deleted.")
            else:
                print("Deletion cancelled.")
        return select_motion()
    elif choice.upper() == 'A':
        target = input("Enter the number of the motion to archive: ").strip()
        if target.isdigit() and 1 <= int(target) <= len(motions):
            old_file = motions[int(target)-1]['file']
            archive_dir = os.path.join(DEBATES_DIR, 'archives')
            os.rename(old_file, os.path.join(archive_dir, os.path.basename(old_file)))
            global SESSION_MOTIONS_ARCHIVED
            SESSION_MOTIONS_ARCHIVED += 1
            print(f"✅ Motion archived.")
        return select_motion()
        
    if choice.isdigit() and 1 <= int(choice) <= len(motions):
        selected = motions[int(choice)-1]
        ACTIVE_MOTION = selected['name']
        DB_FILE = selected['file']
    else:
        if choice:
            ACTIVE_MOTION = choice.title()
            filename = choice.lower().replace(" ", "_").replace("/", "") + ".json"
            DB_FILE = os.path.join(DEBATES_DIR, filename)
def load_vault_from_file(filepath):
    """Safely reads the JSON database."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"{RED}⚠️  Warning: {filepath} is corrupted. Returning empty array.{RESET}")
        return []

def load_vault():
    return load_vault_from_file(DB_FILE)

def save_vault(cards):
    """Writes data back to the JSON database."""
    with open(DB_FILE, 'w') as file:
        json.dump(cards, file, indent=2)

def backup_motion():
    if os.path.exists(DB_FILE):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(BACKUPS_DIR, f"{os.path.basename(DB_FILE)}_{timestamp}.json")
        shutil.copy2(DB_FILE, backup_path)

def get_trash():
    if not os.path.exists(TRASH_FILE): return []
    try:
        with open(TRASH_FILE, 'r') as f: return json.load(f)
    except:
        return []

def save_trash(trash):
    with open(TRASH_FILE, 'w') as f: json.dump(trash, f, indent=2)

def fuzzy_highlight(text, keyword):
    if not keyword: 
        return text
        
    if keyword.lower() in text.lower():
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        tmp = pattern.sub(f"HIGHLIGHT_START\g<0>HIGHLIGHT_END", text)
        tmp = tmp.replace("HIGHLIGHT_START", HIGHLIGHT_YELLOW).replace("HIGHLIGHT_END", RESET)
        return tmp
        
    words = re.findall(r'\b\w+\b', text)
    matches = difflib.get_close_matches(keyword.lower(), [w.lower() for w in words], cutoff=0.7)
    
    if matches:
        match_words = set(matches)
        def repl(m):
            w = m.group(0)
            if w.lower() in match_words:
                return f"{HIGHLIGHT_YELLOW}{w}{RESET}"
            return w
        return re.sub(r'\b\w+\b', repl, text)
        
    return text
    
def fuzzy_match(text, keyword):
    if keyword.lower() in text.lower():
        return True
    words = re.findall(r'\b\w+\b', text)
    return len(difflib.get_close_matches(keyword.lower(), [w.lower() for w in words], cutoff=0.7)) > 0

def print_card(c, motion_name="", keyword=""):
    border_color = GREEN if c['side'] == 'AFF' else RED
    bg_color = BG_GREEN_BLACK_TEXT if c['side'] == 'AFF' else BG_RED_BLACK_TEXT
    width = 80
    
    print(f"{border_color}┏" + "━"*(width-2) + f"┓{RESET}")
    
    # Tag Line with Background
    tag_clean = f"[{c['side']}] {c['tag'].upper()}"
    tag_lines = textwrap.wrap(tag_clean, width-4)
    for line in tag_lines:
        padding = " " * (width - 4 - len(line))
        print(f"{border_color}┃ {bg_color} {line}{padding} {RESET}{border_color} ┃{RESET}")
        
    # Citation / Meta Line
    star = "[⭐] " if c.get('tier') == 3 else ""
    cite_str = f"{star}Source: {c['citation']}"
    meta = f"ID: {c['id']} | Date: {c.get('timestamp', 'Legacy')} | Tier: {c.get('tier', 1)}"
    space_between = width - 4 - len(cite_str) - len(meta)
    if space_between > 0:
        print(f"{border_color}┃ {UNDERLINE_CYAN}{cite_str}{RESET}{border_color}" + " "*space_between + f"{meta} ┃{RESET}")
    elif space_between == 0:
        print(f"{border_color}┃ {UNDERLINE_CYAN}{cite_str}{RESET}{border_color}{meta} ┃{RESET}")
    else:
        print(f"{border_color}┃ {UNDERLINE_CYAN}{cite_str}{RESET}{border_color} ┃{RESET}")
        print(f"{border_color}┃ {meta}{border_color} ┃{RESET}")
    
    if motion_name:
        m_line = f"[From: {motion_name}]"
        print(f"{border_color}┃ {m_line}" + " "*(width - 4 - len(m_line)) + f" ┃{RESET}")
        
    print(f"{border_color}┣" + "━"*(width-2) + f"┫{RESET}")
    
    # Evidence Text
    clean_lines = textwrap.wrap(c['text'], width-4) 
    for line in clean_lines:
        hl_line = fuzzy_highlight(line, keyword)
        padding = " " * (width - 4 - len(line))
        print(f"{border_color}┃ {RESET}{hl_line}{padding} {border_color}┃{RESET}")
        
    print(f"{border_color}┗" + "━"*(width-2) + f"┛{RESET}")

def add_card(tag, citation, side, text, language, tier=1):
    """Adds a new evidence card to the vault."""
    cards = load_vault()
    new_id = max([c.get('id', 0) for c in cards], default=0) + 1
    
    new_card = {
        "id": new_id,
        "tag": tag,
        "citation": citation,
        "side": side.upper(),
        "text": text,
        "language": language.upper(),
        "mastery": 0,
        "tier": int(tier),
        "timestamp": datetime.date.today().strftime("%Y-%m-%d")
    }
    
    cards.append(new_card)
    save_vault(cards)
    print(f"✅ Card added successfully! ({CYAN}Vault ID: {new_id}{RESET})")

def search_cards(side=None, keyword=None, lang=None, global_search=False):
    """Filters and retrieves cards based on parameters."""
    start_time = time.time()
    def match_card(c):
        if side and c['side'] != side.upper(): return False
        if lang and c.get('language', 'EN') != lang.upper(): return False
        if keyword:
            if not (fuzzy_match(c['tag'], keyword) or fuzzy_match(c['text'], keyword)):
                return False
        return True

    results = []
    motions_searched = set()
    
    if global_search:
        files = glob.glob(os.path.join(DEBATES_DIR, "*.json")) + glob.glob(os.path.join(DEBATES_DIR, "archives", "*.json"))
        files = [f for f in files if not f.endswith(".trash.json")]
        for f in files:
            basename = os.path.basename(f)
            motion_name = basename[:-5].replace("_", " ").title()
            motions_searched.add(motion_name)
            cards = load_vault_from_file(f)
            matched = [c for c in cards if match_card(c)]
            for m in matched:
                results.append((m, motion_name))
    else:
        motions_searched.add(ACTIVE_MOTION)
        cards = load_vault()
        matched = [c for c in cards if match_card(c)]
        
        if len(matched) == 0:
            print(f"{CYAN}No local results found. Searching globally...{RESET}")
            return search_cards(side, keyword, lang, global_search=True)
            
        for m in matched:
            results.append((m, ""))
            
    elapsed = time.time() - start_time
    
    if len(results) == 0:
        print(f"\n📊 Found 0 matches across {len(motions_searched)} motions in {elapsed:.3f} seconds.")
        if keyword:
            all_tags = []
            files = [DB_FILE] if not global_search else [f for f in glob.glob(os.path.join(DEBATES_DIR, "*.json")) + glob.glob(os.path.join(DEBATES_DIR, "archives", "*.json")) if not f.endswith(".trash.json")]
            for f in files:
                all_tags.extend([c['tag'] for c in load_vault_from_file(f)])
            close_matches = difflib.get_close_matches(keyword, all_tags, n=1, cutoff=0.3)
            if close_matches:
                print(f"💡 {HIGHLIGHT_YELLOW}Did you mean: '{close_matches[0]}'?{RESET}")
    else:
        scope_name = "Global Vault" if global_search else ACTIVE_MOTION
        print(f"\n🔍 Found {len(results)} card(s) in {CYAN}{scope_name}{RESET}:")
        for c, m_name in results:
            print_card(c, m_name if global_search and m_name != ACTIVE_MOTION else "", keyword)
        print(f"\n📊 Found {len(results)} matches across {len(motions_searched)} motions in {elapsed:.3f} seconds.")


def edit_card(card_id):
    cards = load_vault()
    card = next((c for c in cards if c.get('id') == card_id), None)
    if not card:
        print(f"❌ Error: No card found with ID {card_id}.")
        return
        
    print(f"Editing Card {card_id}: {card['tag']}")
    tag = input(f"Tag [{card['tag']}]: ") or card['tag']
    cite = input(f"Citation [{card['citation']}]: ") or card['citation']
    side = input(f"Side [{card['side']}]: ") or card['side']
    text = input(f"Text [{card['text'][:20]}...]: ") or card['text']
    tier = input(f"Tier [{card.get('tier', 1)}]: ") or card.get('tier', 1)
    
    card['tag'] = tag
    card['citation'] = cite
    card['side'] = side.upper()
    card['text'] = text
    card['tier'] = int(tier)
    card['timestamp'] = datetime.date.today().strftime("%Y-%m-%d")
    
    save_vault(cards)
    global SESSION_CARDS_EDITED
    SESSION_CARDS_EDITED += 1
    print(f"✅ Card {card_id} updated successfully!")

def delete_card(card_id):
    """Soft Deletes an evidence card by its ID."""
    cards = load_vault()
    card_to_del = next((c for c in cards if c.get('id') == card_id), None)
    
    if card_to_del:
        cards.remove(card_to_del)
        backup_motion()  # strict backup
        trash = get_trash()
        trash.append({"motion_file": DB_FILE, "card": card_to_del})
        save_trash(trash)
        save_vault(cards)
        print(f"✅ Card {CYAN}{card_id}{RESET} successfully moved to trash.")
    else:
        print(f"❌ Error: No card found with ID {card_id}.")

def undo_delete():
    trash = get_trash()
    if not trash:
        print("❌ No recently deleted cards found in trash.")
        return
        
    last_item = trash.pop()
    save_trash(trash)
    
    target_file = last_item["motion_file"]
    card = last_item["card"]
    
    cards = load_vault_from_file(target_file)
    cards.append(card)
    
    with open(target_file, 'w') as file:
        json.dump(cards, file, indent=2)
        
    print(f"✅ Undo successful! Recovered '{card['tag']}' to {os.path.basename(target_file)}.")

def export_cards(side, filename):
    """Exports filtered cards to a formatted brief text file with TOC."""
    cards = load_vault()
    
    if side:
        cards = [c for c in cards if c['side'] == side.upper()]
        
    if not filename:
        filename = os.path.join(EXPORTS_DIR, f"brief_{ACTIVE_MOTION.lower().replace(' ', '_')}.txt")
        
    aff_cards = [c for c in cards if c['side'] == 'AFF']
    neg_cards = [c for c in cards if c['side'] == 'NEG']
    
    is_md = filename.endswith('.md')
    
    with open(filename, 'w') as file:
        if is_md:
            file.write(f"# DEBATE BRIEF: {ACTIVE_MOTION}\n\n")
            file.write("## TABLE OF CONTENTS\n\n")
            file.write("### AFFIRMATIVE\n")
            for i, c in enumerate(aff_cards):
                file.write(f"- {c['tag'].upper()} ({c['citation']})\n")
            file.write("\n### NEGATIVE\n")
            for i, c in enumerate(neg_cards):
                file.write(f"- {c['tag'].upper()} ({c['citation']})\n")
            
            file.write("\n---\n\n")
            for c in aff_cards + neg_cards:
                star = "⭐ " if c.get('tier') == 3 else ""
                file.write(f"## [{c['side']}] {c['tag'].upper()}\n")
                file.write(f"**Source:** {star}{c['citation']} | **Date:** {c.get('timestamp', 'Legacy')} | **Tier:** {c.get('tier', 1)}\n\n")
                file.write(f"> {c['text']}\n\n")
        else:
            file.write("=" * 60 + "\n")
            file.write(f"DEBATE BRIEF: {ACTIVE_MOTION}\n")
            file.write("=" * 60 + "\n\n")
            
            file.write("--- TABLE OF CONTENTS ---\n\n")
            file.write("AFFIRMATIVE:\n")
            for i, c in enumerate(aff_cards):
                file.write(f"  [{i+1}] {c['tag'].upper()} ({c['citation']})\n")
            file.write("\nNEGATIVE:\n")
            for i, c in enumerate(neg_cards):
                file.write(f"  [{i+1}] {c['tag'].upper()} ({c['citation']})\n")
                
            file.write("\n" + "=" * 60 + "\n\n")
            
            for c in aff_cards + neg_cards:
                star = "[⭐] " if c.get('tier') == 3 else ""
                file.write("—" * 60 + "\n")
                file.write(f"[{c['side']}] {c['tag'].upper()}\n")
                file.write(f"{star}Source: {c['citation']}  |  Language: {c.get('language', 'EN')} | Date: {c.get('timestamp', 'Legacy')} | Tier: {c.get('tier', 1)}\n")
                file.write("—" * 60 + "\n")
                file.write(f"{c['text']}\n\n")
            
    print(f"📂 Export Complete: {filename} generated with {len(cards)} cards.")

def run_timer(seconds):
    total = seconds
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            
            bar_len = 20
            filled = int((seconds / total) * bar_len) if total else 0
            bar = "#" * filled + "-" * (bar_len - filled)
            
            sys.stdout.write(f"\r{CYAN}⏳ [{timer}] [{bar}] {RESET} ")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
            
        sys.stdout.write(f"\r\a{RED}⚠️  TIME EXPIRED ⚠️                             {RESET}\n")
        sys.stdout.flush()
        
        for _ in range(3):
            time.sleep(0.5)
            sys.stdout.write(f"\r{BOLD_WHITE}⚠️  TIME EXPIRED ⚠️                             {RESET}")
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write(f"\r{RED}⚠️  TIME EXPIRED ⚠️                             {RESET}")
            sys.stdout.flush()
        print()
    except KeyboardInterrupt:
        print(f"\n{CYAN}Timer paused/cancelled.{RESET}")

def timer_menu():
    print(f"\n{CYAN}--- CHRONOS TIMER ---{RESET}")
    print("[1] Constructive (4:00)")
    print("[2] Rebuttal (2:00)")
    print("[3] Crossfire (3:00)")
    print("[4] Custom")
    
    choice = input("Select preset: ").strip()
    seconds = 0
    if choice == '1':
        seconds = 4 * 60
    elif choice == '2':
        seconds = 2 * 60
    elif choice == '3':
        seconds = 3 * 60
    elif choice == '4':
        min_in = input("Enter minutes: ").strip()
        sec_in = input("Enter seconds: ").strip()
        if min_in.isdigit() and sec_in.isdigit():
            seconds = int(min_in) * 60 + int(sec_in)
        else:
            print("Invalid input.")
            return
    else:
        print("Invalid choice.")
        return

    run_timer(seconds)

def drill_mode(weak_points=False):
    cards = load_vault()
    if weak_points:
        cards = [c for c in cards if c.get('mastery', 0) <= 3]
        if not cards:
            print(f"🚀 {CYAN}You have mastered all rated cards! No weak points found.{RESET}")
            return
            
    if not cards:
        print(f"❌ {ACTIVE_MOTION} is empty. Add cards before drilling!")
        return
        
    c = random.choice(cards)
    print(f"\n{CYAN}⚔️  MASTERY DRILL {'(WEAK POINTS)' if weak_points else ''} ⚔️{RESET}")
    border_color = GREEN if c['side'] == 'AFF' else RED
    bg_color = BG_GREEN_BLACK_TEXT if c['side'] == 'AFF' else BG_RED_BLACK_TEXT
    width = 80
    
    print(f"{border_color}┏" + "━"*(width-2) + f"┓{RESET}")
    tag_clean = f"[{c['side']}] {c['tag'].upper()}"
    for line in textwrap.wrap(tag_clean, width-4):
        print(f"{border_color}┃ {bg_color} {line}{' ' * (width - 4 - len(line))} {RESET}{border_color} ┃{RESET}")
    cite_line = f"Source: {c['citation']}"
    print(f"{border_color}┃ {UNDERLINE_CYAN}{cite_line}{RESET}{border_color}{' ' * (width - 4 - len(cite_line))} ┃{RESET}")
    print(f"{border_color}┗" + "━"*(width-2) + f"┛{RESET}")
    
    input(f"\n{BOLD_WHITE}[Press Enter to reveal evidence]{RESET}")
    print(f"\n{c['text']}\n")
    
    rate = input(f"{CYAN}How well did you know this? (1-5): {RESET}").strip()
    if rate.isdigit() and 1 <= int(rate) <= 5:
        all_cards = load_vault()
        for oc in all_cards:
            if oc['id'] == c['id']:
                oc['mastery'] = int(rate)
                break
        save_vault(all_cards)
        print(f"✅ Mastery rating {rate}/5 saved.")
    else:
        print("Rating skipped.")

def print_header():
    cards = load_vault()
    print(f"\n{HIGHLIGHT_YELLOW}>>> [ MOTION: {ACTIVE_MOTION} | {len(cards)} Cards ] <<<{RESET}")

def interactive_loop():
    while True:
        print_header()
        print(f"\n{CYAN}--- DEBATE COMMAND CENTER ---{RESET}")
        print("[1] Search Evidence (Fuzzy Omni-Search)")
        print("[2] Add Evidence")
        print("[3] Edit Evidence")
        print("[4] Delete Evidence")
        print("[5] Undo Delete")
        print("[6] Chronos Timer")
        print("[7] Gladiator Drill Mode")
        print("[8] Weak Point Drill")
        print("[9] Export Brief")
        print("[10] Change Motion")
        print("[11] Exit")
        
        choice = input("Select action: ").strip()
        
        if choice == '1':
            scope = input("Search scope [1] Current Motion [2] Global: ").strip()
            side = input("Filter Side (AFF/NEG) or Enter to skip: ").strip()
            lang = input("Filter Language (e.g. EN) or Enter to skip: ").strip()
            keyword = input("Search keyword or Enter to skip: ").strip()
            search_cards(side if side else None, keyword if keyword else None, lang if lang else None, global_search=(scope=='2'))
        elif choice == '2':
            tag = input("Tag: ")
            cite = input("Citation: ")
            side = input("Side (AFF/NEG): ").upper()
            lang = input("Language [Default EN]: ").strip() or "EN"
            text = input("Evidence Text: ")
            tier = input("Tier (1-3) [Default 1]: ").strip() or "1"
            add_card(tag, cite, side, text, lang, tier)
        elif choice == '3':
            try:
                card_id = int(input("Enter the ID of the card to edit: "))
                edit_card(card_id)
            except ValueError:
                print("❌ Error: Invalid ID format.")
        elif choice == '4':
            try:
                card_id = int(input("Enter the ID of the card to purge: "))
                delete_card(card_id)
            except ValueError:
                print("❌ Error: Invalid ID format.")
        elif choice == '5':
            undo_delete()
        elif choice == '6':
            timer_menu()
        elif choice == '7':
            drill_mode(weak_points=False)
        elif choice == '8':
            drill_mode(weak_points=True)
        elif choice == '9':
            side = input("Filter Side (AFF/NEG) or Enter to export all: ").strip()
            filename = input("Custom filename or Enter for default: ").strip()
            export_cards(side if side else None, filename if filename else None)
        elif choice == '10':
            select_motion()
        elif choice == '11':
            print(f"{CYAN}Exiting Vault. Good luck!{RESET}")
            print(f"\n📊 Session Debrief:")
            print(f"Cards Edited: {SESSION_CARDS_EDITED} | Motions Archived: {SESSION_MOTIONS_ARCHIVED}\n")
            break
        else:
            print("Invalid choice.")

def main():
    print_banner()
    run_setup_dirs()
    select_motion()
    
    parser = argparse.ArgumentParser(description="🏛️ Evidence Vault CLI v3.3.0 - Debate Command Center")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("add", help="Add a new evidence card interactively")
    subparsers.add_parser("edit", help="Edit an evidence card by ID")
    
    search_parser = subparsers.add_parser("search", help="Search the vault")
    search_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    search_parser.add_argument("--keyword", help="Search for specific words in tag or text")

    subparsers.add_parser("delete", help="Delete a card by ID interactively")
    
    subparsers.add_parser("undo", help="Undo the last card deletion")
    
    export_parser = subparsers.add_parser("export", help="Export cards to a tournament brief")
    export_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    export_parser.add_argument("--filename", help="Output text file")
    
    subparsers.add_parser("timer", help="Launch the Chronos Timer")
    subparsers.add_parser("drill", help="Start Gladiator Drill Mode")

    args = parser.parse_args()

    if not args.command:
        interactive_loop()
    elif args.command == "add":
        tag = input("Tag: ")
        cite = input("Citation: ")
        side = input("Side (AFF/NEG): ").upper()
        text = input("Evidence Text: ")
        tier = input("Tier (1-3) [Default 1]: ").strip() or "1"
        add_card(tag, cite, side, text, "EN", tier)
        interactive_loop()
    elif args.command == "edit":
        try:
            card_id = int(input("Enter the ID of the card to edit: "))
            edit_card(card_id)
        except ValueError:
            print("❌ Error: Invalid ID format.")
        interactive_loop()
    elif args.command == "search":
        search_cards(args.side, args.keyword)
        interactive_loop()
    elif args.command == "delete":
        try:
            card_id = int(input("Enter the ID of the card to purge: "))
            delete_card(card_id)
        except ValueError:
            print("❌ Error: Invalid ID format.")
        interactive_loop()
    elif args.command == "undo":
        undo_delete()
        interactive_loop()
    elif args.command == "export":
        export_cards(args.side, args.filename)
    elif args.command == "timer":
        timer_menu()
        interactive_loop()
    elif args.command == "drill":
        drill_mode()
        interactive_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}Exiting Vault. Good luck!{RESET}")
        print(f"\n📊 Session Debrief:")
        print(f"Cards Edited: {SESSION_CARDS_EDITED} | Motions Archived: {SESSION_MOTIONS_ARCHIVED}\n")
        sys.exit(0)
