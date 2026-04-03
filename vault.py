import json
import argparse
import os

DB_FILE = "database.json"

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
    print(f"✅ Card added successfully! (Vault ID: {new_id})")

def search_cards(side=None, keyword=None):
    """Filters and retrieves cards based on parameters."""
    cards = load_vault()
    results = cards
    
    # Filter by AFF or NEG
    if side:
        results = [c for c in results if c['side'] == side.upper()]
    
    # Filter by specific keywords in the tag or text
    if keyword:
        keyword = keyword.lower()
        results = [c for c in results if keyword in c['tag'].lower() or keyword in c['text'].lower()]
        
    print(f"\n🔍 Found {len(results)} card(s):")
    for c in results:
        print("=" * 50)
        print(f"[{c['side']}] {c['tag']}")
        print(f"Source: {c['citation']}")
        print(f"Evidence: {c['text']}")
    print("=" * 50)

def delete_card(card_id):
    """Deletes an evidence card by its ID."""
    cards = load_vault()
    initial_length = len(cards)
    
    # Filter the list of cards to remove the entry where the ID matches the user's input
    cards = [c for c in cards if c.get('id') != card_id]
    
    if len(cards) < initial_length:
        save_vault(cards)
        print(f"✅ Card {card_id} successfully purged from the vault.")
    else:
        print(f"❌ Error: No card found with ID {card_id}.")

def export_cards(side, filename):
    """Exports filtered cards to a formatted text file."""
    cards = load_vault()
    
    if side:
        cards = [c for c in cards if c['side'] == side.upper()]
        
    with open(filename, 'w') as file:
        for c in cards:
            file.write("=" * 50 + "\n")
            file.write(f"{c['tag'].upper()}\n")
            file.write(f"Source: {c['citation']}\n")
            file.write(f"Evidence: {c['text']}\n\n")
            
    print(f"📂 Export Complete: {filename} generated with {len(cards)} cards.")

def main():
    parser = argparse.ArgumentParser(description="🏛️ Evidence Vault CLI - Debate Card Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # The 'add' command configuration
    add_parser = subparsers.add_parser("add", help="Add a new evidence card interactively")

    # The 'search' command configuration
    search_parser = subparsers.add_parser("search", help="Search the vault")
    search_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    search_parser.add_argument("--keyword", help="Search for specific words in tag or text")

    # The 'delete' command configuration
    delete_parser = subparsers.add_parser("delete", help="Delete a card by ID interactively")

    # The 'export' command configuration
    export_parser = subparsers.add_parser("export", help="Export cards to a tournament brief")
    export_parser.add_argument("--side", choices=["AFF", "NEG", "aff", "neg"], help="Filter by AFF or NEG")
    export_parser.add_argument("--filename", default="tournament_brief.txt", help="Output text file")

    args = parser.parse_args()

    # Route the command to the correct function
    if args.command == "add":
        tag = input("Tag: ")
        cite = input("Citation: ")
        side = input("Side (AFF/NEG): ").upper()
        text = input("Evidence Text: ")
        add_card(tag, cite, side, text)
    elif args.command == "search":
        search_cards(args.side, args.keyword)
    elif args.command == "delete":
        try:
            card_id = int(input("Enter the ID of the card to purge: "))
            delete_card(card_id)
        except ValueError:
            print("❌ Error: Invalid ID format. Must be an integer.")
    elif args.command == "export":
        export_cards(args.side, args.filename)
    else:
        # If no command is typed, show the help menu
        parser.print_help()

if __name__ == "__main__":
    main()
