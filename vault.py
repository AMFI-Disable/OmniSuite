import json

def load_vault(filepath="database.json"):
    """Reads the JSON database and returns the evidence cards."""
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return [] # Returns an empty list if the vault doesn't exist yet

def main():
    cards = load_vault()
    print("==================================")
    print("🏛️ Evidence Vault CLI Initialized")
    print("==================================")
    print(f"System status: Online.")
    print(f"Cards currently loaded in vault: {len(cards)}")

if __name__ == "__main__":
    main()
