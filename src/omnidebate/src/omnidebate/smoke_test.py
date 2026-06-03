import sys
import os
import datetime

# Ensure project root is in path for standalone execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnidebate.core.database import add_motion, add_card


def smoke_test_data():
    print("🚀 Initializing Smoke Test Data...")

    # Add a motion
    m_id = add_motion("AI Legal Ban")
    print(f"✅ Added Motion: AI Legal Ban (ID: {m_id})")

    # Add an AFF card (Tier 3 - Power Card)
    add_card(
        m_id,
        {
            "side": "AFF",
            "tag": "ALGORITHMIC BIAS",
            "text": "AI models trained on historical data perpetuate systemic racial and socioeconomic biases.",
            "citation": "O'Neil (2016) 'Weapons of Math Destruction'",
            "tier": 3,
            "language": "EN",
            "timestamp": datetime.datetime.now().isoformat(),
        },
    )

    # Add a NEG card (Tier 2)
    add_card(
        m_id,
        {
            "side": "NEG",
            "tag": "EFFICIENCY & SCALE",
            "text": "Human judges are bottlenecked; AI can process case law 10,000x faster.",
            "citation": "IBM Legal Insights (2023)",
            "tier": 2,
            "language": "EN",
            "timestamp": datetime.datetime.now().isoformat(),
        },
    )

    print("✅ Smoke Test Evidence Injected.")


if __name__ == "__main__":
    smoke_test_data()
