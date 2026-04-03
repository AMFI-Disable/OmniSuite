import json
import argparse
import os
import glob
import time
import sys

DEBATES_DIR = "debates"
DB_FILE = "database.json"
ACTIVE_MOTION = "Default"

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD_WHITE = '\033[1;37m'
RESET = '\033[0m'

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

def ensure_debates_dir():
    if not os.path.exists(DEBATES_DIR):
        os.makedirs(DEBATES_DIR)

def select_motion():
    global DB_FILE, ACTIVE_MOTION
    ensure_debates_dir()
    
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

    print(f"\n{BOLD_WHITE}[ACTIVE MOTION: {ACTIVE_MOTION}]{RESET}")

def load_vault():
    """Reads the JSON database."""
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, 'r') as file:
        return json.load(file)

def save_vault(cards):
    """Writes data back to the JSON database."""
    with open(DB_FILE, 'w') as file:
        json.dump(cards, file, indent=2)

def add_card(tag, citation, side, text):
    """Adds a new evidence card to the vault."""
    cards = load_vault()
    new_id = max([c.get('id', 0) for c in cards], default=0) + 1
    
    new_card = {
        "id": new_id,
        "tag": tag,
        "citation": citation,
        "side": side.upper(),
        "text": text
    }
    
    cards.append(new_card)
    save_vault(cards)
    print(f"✅ Card added successfully! ({CYAN}Vault ID: {new_id}{RESET})")

def search_cards(side=None, keyword=None):
    """Filters and retrieves cards based on parameters."""
    cards = load_vault()
    results = cards
    
    if side:
        results = [c for c in results if c['side'] == side.upper()]
    
    if keyword:
        keyword = keyword.lower()
        results = [c for c in results if keyword in c['tag'].lower() or keyword in c['text'].lower()]
        
    print(f"\n🔍 Found {len(results)} card(s) in {CYAN}{ACTIVE_MOTION}{RESET}:")
    for c in results:
        color = GREEN if c['side'] == 'AFF' else RED
        print(f"{color}==================================================")
        print(f"[{c['side']}] {BOLD_WHITE}{c['tag']}{color}")
        print(f"Source: {c['citation']}")
        print(f"ID: {CYAN}{c['id']}{color}")
        print(f"--------------------------------------------------")
        print(f"{c['text']}")
        print(f"=================================================={RESET}")

def delete_card(card_id):
    """Deletes an evidence card by its ID."""
    cards = load_vault()
    initial_length = len(cards)
    
    cards = [c for c in cards if c.get('id') != card_id]
    
    if len(cards) < initial_length:
        save_vault(cards)
        print(f"✅ Card {CYAN}{card_id}{RESET} successfully purged from the vault.")
    else:
        print(f"❌ Error: No card found with ID {card_id}.")

def export_cards(side, filename):
    """Exports filtered cards to a formatted text file."""
    cards = load_vault()
    
    if side:
        cards = [c for c in cards if c['side'] == side.upper()]
        
    if not filename:
        filename = f"export_{ACTIVE_MOTION.lower().replace(' ', '_')}.txt"
        
    with open(filename, 'w') as file:
        for c in cards:
            file.write("=" * 50 + "\n")
            file.write(f"{c['tag'].upper()}\n")
            file.write(f"Source: {c['citation']}\n")
            file.write(f"Evidence: {c['text']}\n\n")
            
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
        
        # Blink effect
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
        seconds = int(min_in) * 60 + int(sec_in)
    else:
        print("Invalid choice.")
        return

    run_timer(seconds)

def interactive_loop():
    while True:
        print(f"\n{CYAN}--- DEBATE COMMAND CENTER ---{RESET}")
        print("[1] Search Evidence")
        print("[2] Add Evidence")
        print("[3] Delete Evidence")
        print("[4] Chronos Timer")
        print("[5] Change Motion")
        print("[6] Exit")
        
        choice = input("Select action: ").strip()
        
        if choice == '1':
            side = input("Filter Side (AFF/NEG) or Enter to skip: ").strip()
            keyword = input("Search keyword or Enter to skip: ").strip()
            search_cards(side if side else None, keyword if keyword else None)
        elif choice == '2':
            tag = input("Tag: ")
            cite = input("Citation: ")
            side = input("Side (AFF/NEG): ").upper()
            text = input("Evidence Text: ")
            add_card(tag, cite, side, text)
        elif choice == '3':
            try:
                card_id = int(input("Enter the ID of the card to purge: "))
                delete_card(card_id)
            except ValueError:
                print("❌ Error: Invalid ID format.")
        elif choice == '4':
            timer_menu()
        elif choice == '5':
            select_motion()
        elif choice == '6':
            print(f"{CYAN}Exiting Vault. Good luck!{RESET}")
            break
        else:
            print("Invalid choice.")

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="🏛️ Evidence Vault CLI - Debate Command Center")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("add", help="Add a new evidence card interactively")
    
    search_parser = subparsers.add_parser("search", help="Search the vault")
    search_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    search_parser.add_argument("--keyword", help="Search for specific words in tag or text")

    subparsers.add_parser("delete", help="Delete a card by ID interactively")
    
    export_parser = subparsers.add_parser("export", help="Export cards to a tournament brief")
    export_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    export_parser.add_argument("--filename", help="Output text file")
    
    subparsers.add_parser("timer", help="Launch the Chronos Timer")

    args = parser.parse_args()

    # Trigger motion selection first
    select_motion()

    # Route the command
    if not args.command:
        # Launch Interactive REPL if no command provided
        interactive_loop()
    elif args.command == "add":
        tag = input("Tag: ")
        cite = input("Citation: ")
        side = input("Side (AFF/NEG): ").upper()
        text = input("Evidence Text: ")
        add_card(tag, cite, side, text)
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
    elif args.command == "export":
        export_cards(args.side, args.filename)
    elif args.command == "timer":
        timer_menu()
        interactive_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}Exiting Vault. Good luck!{RESET}")
        sys.exit(0)
