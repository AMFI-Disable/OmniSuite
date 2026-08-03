from omnidebate.core.oracle import OracleEngine


def test_simulate_sparring_vulnerability():
    # Test that vulnerability calculations are correct and scale down with higher mastery/tier.
    card_vulnerable = {
        "tag": "Generic AFF argument",
        "side": "AFF",
        "text": "This is some generic text.",
        "mastery": 0,
        "tier": 1,
    }
    spar_vulnerable = OracleEngine.simulate_sparring(card_vulnerable)
    # Extract vulnerability from: "**Engagement Vulnerability Rating**: 90% (Mastery: 0, Tier: 1)"
    vuln_line = [line for line in spar_vulnerable if "Vulnerability Rating" in line][0]
    assert "90%" in vuln_line

    card_strong = {
        "tag": "Advanced AFF argument",
        "side": "AFF",
        "text": "This is some generic text.",
        "mastery": 3,
        "tier": 3,
    }
    spar_strong = OracleEngine.simulate_sparring(card_strong)
    vuln_line_strong = [line for line in spar_strong if "Vulnerability Rating" in line][0]
    # 100 - (3 * 20) - (3 * 10) = 100 - 60 - 30 = 10%
    assert "10%" in vuln_line_strong


def test_simulate_sparring_keywords():
    # Test that sparring outputs correct keyword-based attack/rebuttals
    card_climate = {
        "tag": "AFF climate change impacts",
        "side": "AFF",
        "text": "Rising carbon emissions induce climate warming.",
        "mastery": 1,
        "tier": 2,
    }
    spar_climate = OracleEngine.simulate_sparring(card_climate)
    assert any("carbon leakage" in line for line in spar_climate)
    assert any("bio-survival impacts" in line for line in spar_climate)

    card_neg_economy = {
        "tag": "NEG inflation risk",
        "side": "NEG",
        "text": "The plan disrupts the economy and triggers massive inflation.",
        "mastery": 1,
        "tier": 2,
    }
    spar_neg_eco = OracleEngine.simulate_sparring(card_neg_economy)
    assert any("income inequality" in line for line in spar_neg_eco)
    assert any("stifles innovation" in line for line in spar_neg_eco)


def test_calculate_victory_road():
    # Test with empty cards
    empty_road = OracleEngine.calculate_victory_road([])
    assert any("Locked" in line for line in empty_road)
    assert not any("Available" in line for line in empty_road)

    # Test path locking and unlocking
    # Cards without tier 3 should keep paths locked
    low_tier_cards = [
        {
            "tag": "Carbon Tax",
            "side": "AFF",
            "text": "Climate carbon tax saves the environment.",
            "tier": 1,
            "mastery": 1,
        }
    ]
    road_low = OracleEngine.calculate_victory_road(low_tier_cards)
    assert any("BIO-SURVIVAL PATH: 🔴 Locked" in line for line in road_low)

    # Adding a tier 3 card unlocks the pathway
    unlocked_cards = [
        {
            "tag": "Carbon Tax Link",
            "side": "AFF",
            "text": "Climate carbon tax reduces emissions.",
            "tier": 1,
            "mastery": 1,
        },
        {
            "tag": "Eco Survival Impact",
            "side": "AFF",
            "text": "Climate sustainability prevents extinction.",
            "tier": 3,
            "mastery": 2,
        },
    ]
    road_unlocked = OracleEngine.calculate_victory_road(unlocked_cards)
    assert any("BIO-SURVIVAL PATH: 🟢 Available" in line for line in road_unlocked)
    # Check sequence formatting
    seq_line = [line for line in road_unlocked if "➔" in line][0]
    assert "Carbon Tax Link [Link]" in seq_line
    assert "Eco Survival Impact [Terminal Impact]" in seq_line


def test_simulate_judge_deterministic():
    # Test empty cards
    empty_ballot = OracleEngine.simulate_judge([])
    assert any("Indeterminate" in line for line in empty_ballot)

    # Mock an AFF dominating setup
    aff_dominating = [
        {
            "tag": "AFF Economy Solvency",
            "side": "AFF",
            "text": "Plan improves economy GDP.",
            "tier": 3,
            "mastery": 5,
            "citation": "Smith 2024",
        },
        {
            "tag": "AFF Job growth",
            "side": "AFF",
            "text": "Plan grows jobs.",
            "tier": 2,
            "mastery": 3,
        },
        {
            "tag": "NEG weak point",
            "side": "NEG",
            "text": "No solvency.",
            "tier": 1,
            "mastery": 0,
            "citation": "Jones 2023",
        },
    ]
    ballot_aff = OracleEngine.simulate_judge(aff_dominating)
    decision_line = [line for line in ballot_aff if "Decision" in line][0]
    assert "AFF Wins" in decision_line
    assert any(
        "AFF's core card 'AFF Economy Solvency' [Smith 2024] established a clear causal pathway"
        in line
        for line in ballot_aff
    )
    # Verify feedback targets NEG
    assert any("NEG suffered from low average card mastery" in line for line in ballot_aff)

    # Mock a NEG dominating setup
    neg_dominating = [
        {
            "tag": "AFF weak point",
            "side": "AFF",
            "text": "Trade grows.",
            "tier": 1,
            "mastery": 0,
        },
        {
            "tag": "NEG Economy Disaster",
            "side": "NEG",
            "text": "Plan crashes economy GDP.",
            "tier": 3,
            "mastery": 4,
            "citation": "Baker 2025",
        },
        {
            "tag": "NEG Trade war",
            "side": "NEG",
            "text": "Plan triggers trade wars.",
            "tier": 3,
            "mastery": 3,
        },
    ]
    ballot_neg = OracleEngine.simulate_judge(neg_dominating)
    decision_line_neg = [line for line in ballot_neg if "Decision" in line][0]
    assert "NEG Wins" in decision_line_neg
    assert any(
        "NEG's core defense 'NEG Economy Disaster' [Baker 2025] demonstrated key logical vulnerabilities"
        in line
        for line in ballot_neg
    )
    # Verify feedback targets AFF
    assert any("AFF suffered from low average card mastery" in line for line in ballot_neg)


def test_generate_research_queue():
    # Empty queue
    empty_q = OracleEngine.generate_research_queue([])
    assert any("Empty Vault" in line for line in empty_q)

    # Test side defense imbalance gap (AFF count: 5, NEG count: 1)
    imbalanced_cards = [
        {"tag": "AFF 1", "side": "AFF", "text": "Plan text"},
        {"tag": "AFF 2", "side": "AFF", "text": "Plan text"},
        {"tag": "AFF 3", "side": "AFF", "text": "Plan text"},
        {"tag": "AFF 4", "side": "AFF", "text": "Plan text"},
        {"tag": "AFF 5", "side": "AFF", "text": "Plan text"},
        {"tag": "NEG 1", "side": "NEG", "text": "Plan text"},
    ]
    q_imbalance = OracleEngine.generate_research_queue(imbalanced_cards)
    assert any("NEGATIVE DEFENSE GAP" in line for line in q_imbalance)
    assert any("Negative disadvantages to motion" in line for line in q_imbalance)

    # Test Missing Terminal Link: Climate
    climate_no_terminal = [
        {
            "tag": "Warming Trend",
            "side": "AFF",
            "text": "Climate warming carbon greenhouse emissions increase.",
            "tier": 2,
            "mastery": 1,
        },
        {
            "tag": "NEG Climate defense",
            "side": "NEG",
            "text": "Status quo is fine.",
            "tier": 2,
            "mastery": 1,
        },
    ]
    q_climate = OracleEngine.generate_research_queue(climate_no_terminal)
    assert any("MISSING TERMINAL LINK: CLIMATE BIO-SURVIVAL" in line for line in q_climate)
    assert any("climate warming agricultural collapse" in line for line in q_climate)

    # Test Missing Terminal Link: Economy
    economy_no_terminal = [
        {
            "tag": "Economic Growth",
            "side": "AFF",
            "text": "Plan boosts economy GDP finance trade.",
            "tier": 2,
            "mastery": 1,
        },
        {
            "tag": "NEG Economy defense",
            "side": "NEG",
            "text": "Market is unstable.",
            "tier": 2,
            "mastery": 1,
        },
    ]
    q_economy = OracleEngine.generate_research_queue(economy_no_terminal)
    assert any("MISSING TERMINAL LINK: ECONOMIC STABILITY" in line for line in q_economy)
    assert any("economic recession geopolitical conflict link" in line for line in q_economy)

    # Test Missing Terminal Link: Tech
    tech_no_terminal = [
        {
            "tag": "AI Tech",
            "side": "AFF",
            "text": "Technology ai algorithms digital advances.",
            "tier": 2,
            "mastery": 1,
        },
        {
            "tag": "NEG Tech defense",
            "side": "NEG",
            "text": "AI is regular tech.",
            "tier": 2,
            "mastery": 1,
        },
    ]
    q_tech = OracleEngine.generate_research_queue(tech_no_terminal)
    assert any("MISSING TERMINAL LINK: TECHNOLOGICAL SAFEGUARDS" in line for line in q_tech)
    assert any(
        "artificial general intelligence existential risk control" in line for line in q_tech
    )

    # Balanced, no gaps
    balanced_cards = [
        {
            "tag": "AFF Climate Warming",
            "side": "AFF",
            "text": "Climate warming greenhouse emissions.",
            "tier": 2,
            "mastery": 1,
        },
        {
            "tag": "AFF Climate Extinction",
            "side": "AFF",
            "text": "Climate warming causes human extinction and catastrophe.",
            "tier": 2,
            "mastery": 1,
        },
        {
            "tag": "NEG Climate Defense",
            "side": "NEG",
            "text": "No carbon leakage occurred.",
            "tier": 2,
            "mastery": 1,
        },
    ]
    q_balanced = OracleEngine.generate_research_queue(balanced_cards)
    assert any("NO MAJOR LOGICAL GAPS DETECTED" in line for line in q_balanced)
