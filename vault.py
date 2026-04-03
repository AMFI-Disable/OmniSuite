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

DEBATES_DIR = "debates"
BACKUPS_DIR = "backups"
EXPORTS_DIR = "exports"
DB_FILE = "database.json"
ACTIVE_MOTION = "Default"

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
    for d in [DEBATES_DIR, BACKUPS_DIR, EXPORTS_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def select_motion():
    global DB_FILE, ACTIVE_MOTION
    run_setup_dirs()
    
    files = glob.glob(os.path.join(DEBATES_DIR, "*.json"))
    motions = []
    for f in files:
        basename = os.path.basename(f)
        name = basename[:-5].replace("_", " ").title()
        motions.append({"name": name, "file": f})
        
    print(f"\n{CYAN}--- Available Motions ---{RESET}")
    for i, m in enumerate(motions):
        print(f"[{i+1}] {m['name']}")
    
    choice = input("\nSelect a motion by number, or type a new name to initialize a new debate vault: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(motions):
        selected = motions[int(choice)-1]
        ACTIVE_MOTION = selected['name']
        DB_FILE = selected['file']
    else:
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
        print(f"{CYAN}Data backed up to {backup_path}{RESET}")

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
    cite_str = f"Source: {c['citation']}"
    meta = f"ID: {c['id']} | Lang: {c.get('language', 'EN')} | Mastery: {c.get('mastery', 'Unrated')}"
    space_between = width - 4 - len(cite_str) - len(meta)
    if space_between > 0:
        print(f"{border_color}┃ {UNDERLINE_CYAN}{cite_str}{RESET}{border_color}" + " "*space_between + f"{meta} ┃{RESET}")
    
    if motion_name:
        m_line = f"[From: {motion_name}]"
        print(f"{border_color}┃ {m_line}" + " "*(width - 4 - len(m_line)) + f" ┃{RESET}")
        
    print(f"{border_color}┣" + "━"*(width-2) + f"┫{RESET}")
    
    # Evidence Text
    evidence = fuzzy_highlight(c['text'], keyword)
    clean_lines = textwrap.wrap(c['text'], width-4) 
    # Highlighting wrapped text correctly is tricky with ANSI inside textwrap. 
    # We will wrap first, then highlight each line independently.
    for line in clean_lines:
        hl_line = fuzzy_highlight(line, keyword)
        # padding based on original length
        padding = " " * (width - 4 - len(line))
        print(f"{border_color}┃ {RESET}{hl_line}{padding} {border_color}┃{RESET}")
        
    print(f"{border_color}┗" + "━"*(width-2) + f"┛{RESET}")

def add_card(tag, citation, side, text, language):
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
        "mastery": 0
    }
    
    cards.append(new_card)
    save_vault(cards)
    print(f"✅ Card added successfully! ({CYAN}Vault ID: {new_id}{RESET})")

def search_cards(side=None, keyword=None, lang=None, global_search=False):
    """Filters and retrieves cards based on parameters."""
    def match_card(c):
        if side and c['side'] != side.upper(): return False
        if lang and c.get('language', 'EN') != lang.upper(): return False
        if keyword:
            if not (fuzzy_match(c['tag'], keyword) or fuzzy_match(c['text'], keyword)):
                return False
        return True

    results = []
    
    if global_search:
        files = glob.glob(os.path.join(DEBATES_DIR, "*.json"))
        for f in files:
            basename = os.path.basename(f)
            motion_name = basename[:-5].replace("_", " ").title()
            cards = load_vault_from_file(f)
            matched = [c for c in cards if match_card(c)]
            for m in matched:
                results.append((m, motion_name))
    else:
        cards = load_vault()
        matched = [c for c in cards if match_card(c)]
        
        if len(matched) == 0:
            print(f"{CYAN}No local results found. Searching globally...{RESET}")
            return search_cards(side, keyword, lang, global_search=True)
            
        for m in matched:
            results.append((m, ""))
            
    scope_name = "Global Vault" if global_search else ACTIVE_MOTION
    print(f"\n🔍 Found {len(results)} card(s) in {CYAN}{scope_name}{RESET}:")
    for c, m_name in results:
        print_card(c, m_name if global_search and m_name != ACTIVE_MOTION else "", keyword)

def delete_card(card_id):
    """Deletes an evidence card by its ID."""
    cards = load_vault()
    initial_length = len(cards)
    
    cards = [c for c in cards if c.get('id') != card_id]
    
    if len(cards) < initial_length:
        backup_motion()
        save_vault(cards)
        print(f"✅ Card {CYAN}{card_id}{RESET} successfully purged from the vault.")
    else:
        print(f"❌ Error: No card found with ID {card_id}.")

def export_cards(side, filename):
    """Exports filtered cards to a formatted brief text file with TOC."""
    cards = load_vault()
    
    if side:
        cards = [c for c in cards if c['side'] == side.upper()]
        
    if not filename:
        filename = os.path.join(EXPORTS_DIR, f"brief_{ACTIVE_MOTION.lower().replace(' ', '_')}.txt")
        
    aff_cards = [c for c in cards if c['side'] == 'AFF']
    neg_cards = [c for c in cards if c['side'] == 'NEG']
    
    with open(filename, 'w') as file:
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
            file.write("—" * 60 + "\n")
            file.write(f"[{c['side']}] {c['tag'].upper()}\n")
            file.write(f"Source: {c['citation']}  |  Language: {c.get('language', 'EN')}\n")
            file.write("—" * 60 + "\n")
            file.write(f"{c['text']}\n\n")
            
    print(f"📂 Export Complete: {filename} generated with {len(cards)} cards.")

def run_timer(seconds):
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            sys.stdout.write(f"\r{CYAN}⏳ Time Remaining: {BOLD_WHITE}{timer}{RESET} ")
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
        print("[3] Delete Evidence")
        print("[4] Chronos Timer")
        print("[5] Gladiator Drill Mode")
        print("[6] Weak Point Drill (Mastery <= 3)")
        print("[7] Export Brief")
        print("[8] Change Motion")
        print("[9] Exit")
        
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
            add_card(tag, cite, side, text, lang)
        elif choice == '3':
            try:
                card_id = int(input("Enter the ID of the card to purge: "))
                delete_card(card_id)
            except ValueError:
                print("❌ Error: Invalid ID format.")
        elif choice == '4':
            timer_menu()
        elif choice == '5':
            drill_mode(weak_points=False)
        elif choice == '6':
            drill_mode(weak_points=True)
        elif choice == '7':
            side = input("Filter Side (AFF/NEG) or Enter to export all: ").strip()
            filename = input("Custom filename or Enter for default: ").strip()
            export_cards(side if side else None, filename if filename else None)
        elif choice == '8':
            select_motion()
        elif choice == '9':
            print(f"{CYAN}Exiting Vault. Good luck!{RESET}")
            break
        else:
            print("Invalid choice.")

def main():
    print_banner()
    run_setup_dirs()
    select_motion()
    interactive_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}Exiting Vault. Good luck!{RESET}")
        sys.exit(0)
