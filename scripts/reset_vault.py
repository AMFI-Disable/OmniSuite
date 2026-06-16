import os
from omnidebate.core.database import setup_db, get_db_path, add_motion, add_card


def reset_vault():
    print("🏛️ INITIALIZING STRATEGIC RESET (HIGH-DENSITY BUILD)...")

    # 1. Purge Existing Database
    db_path = get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
        print("> Legacy vault redacted.")

    # 2. Reconstruct Neural Core
    setup_db()
    print("> Neural core reconstructed.")

    # 3. Define Motions
    motions = [
        "🏛️ THE SINGULARITY PROTOCOL",
        "🧬 MARS COLONIZATION ACT",
        "🌐 UNIVERSAL INCOME EQUILIBRIUM",
    ]

    tags = [
        "SOLVENCY",
        "IMPACT",
        "WARRANT",
        "LINK",
        "UNIQUENESS",
        "OVERVIEW",
        "FRAMEWORK",
    ]
    citations = [
        "Bostrom, 2026",
        "Yudkowsky, 2026",
        "Musk, 2026",
        "Yang, 2026",
        "Harari, 2026",
        "Tegmark, 2026",
    ]

    for m_name in motions:
        m_id = add_motion(m_name)
        print(f"> Synthesizing motion: {m_name}")

        for side in ["AFF", "NEG"]:
            for i in range(1, 11):
                tier = (i % 5) + 1
                mastery = i % 6
                tag = f"{tags[i % len(tags)]} / {side}-{i:02d}"
                cite = f"{citations[i % len(citations)]} (Forensic Vol {i})"
                text = f"Since the implementation of {m_name} involves non-linear {side} dynamics, we argue that the {tags[i % len(tags)]} is critical because the {side} outcome leads to a {tier}-tier impact."

                add_card(
                    m_id,
                    {
                        "tag": tag,
                        "side": side,
                        "tier": tier,
                        "text": text,
                        "citation": cite,
                        "mastery": mastery,
                        "timestamp": "2026-05-04 09:00:00",
                    },
                )

    print("✅ STRATEGIC RESET COMPLETE. 60 HIGH-DENSITY CARDS SYNTHESIZED.")


if __name__ == "__main__":
    reset_vault()
