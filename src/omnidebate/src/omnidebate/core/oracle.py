import re


class OracleEngine:
    """The central heuristic engine for strategic debate analysis and metric computation."""

    @staticmethod
    def analyze_impacts_2(card):
        text = card.get("text", "").lower()
        markers = ["resolve", "actualize", "materialize", "trigger", "outcome"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_impacts_2(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_impacts_2(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_narrative(card):
        text = card.get("text", "").lower()
        markers = ["narrative", "story", "theme", "frame", "worldview"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_narrative(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_narrative(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_synergy(card):
        text = card.get("text", "").lower()
        markers = ["synergy", "bridge", "connection", "global", "unify"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_synergy(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_synergy(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_mastery(card):
        text = card.get("text", "").lower()
        markers = ["mastery", "execution", "delivery", "fluency", "precision"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_mastery(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_mastery(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_singularity(card):
        text = card.get("text", "").lower()
        markers = ["singularity", "absolute", "unanswerable", "terminal"]
        score = sum(25 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_singularity(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(
                    sum(OracleEngine.analyze_singularity(c) for c in cards) / len(cards)
                ),
            )
        except Exception:
            return 50

    @staticmethod
    def predict_victory(cards):
        if not cards:
            return 50, "Indeterminate"
        prob = min(
            95,
            max(
                5,
                int(sum(OracleEngine.analyze_victory(c) for c in cards) / len(cards))
                + 20,
            ),
        )
        status = (
            "DOMINANT" if prob > 70 else "COMPETITIVE" if prob > 40 else "VULNERABLE"
        )
        return prob, status

    @staticmethod
    def analyze_victory(card):
        text = card.get("text", "").lower()
        markers = ["victory", "win", "ballot", "decisive", "conclusive", "rfd"]
        score = sum(15 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_victory(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_victory(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_argument(card):
        text = card.get("text", "").lower()
        markers = ["causes", "leads to", "results in", "therefore", "consequently"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_argument(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_argument(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_evidence(card):
        text = card.get("text", "").lower()
        markers = ["study", "proves", "shows", "indicates", "analysis"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_evidence(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_evidence(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_risk(card):
        text = card.get("text", "").lower()
        markers = ["but", "however", "conversely", "risks", "turn"]
        score = sum(20 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_risk(cards):
        try:
            if not cards:
                return 50
            return min(
                100, int(sum(OracleEngine.analyze_risk(c) for c in cards) / len(cards))
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_timeline(card):
        text = card.get("text", "").lower()
        markers = ["imminent", "immediate", "short-term", "now"]
        score = sum(25 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_timeline(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_timeline(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_probability(card):
        text = card.get("text", "").lower()
        markers = ["inevitable", "imminent", "likely", "certain"]
        score = sum(25 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_probability(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(
                    sum(OracleEngine.analyze_probability(c) for c in cards) / len(cards)
                ),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_impacts(card):
        text = card.get("text", "").lower()
        magnitude = ["extinction", "millions", "billions", "catastrophic"]
        score = sum(25 for m in magnitude if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_impacts(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_impacts(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_warrants(card):
        text = card.get("text", "").lower()
        markers = ["because", "since", "leads to", "warrants"]
        score = sum(25 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_warrants(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_warrants(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_forensics(card):
        text = card.get("text", "").lower()
        data = ["study", "analysis", "data", "empirical"]
        score = sum(25 for d in data if d in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_forensics(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_forensics(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def analyze_immersion(card):
        text = card.get("text", "").lower()
        rhetoric = ["suffering", "collapse", "catastrophe", "vivid"]
        score = sum(25 for r in rhetoric if r in text)
        return min(100, max(10, score))

    @staticmethod
    def analyze_persuasion(card):
        text = card.get("text", "").lower()
        logos = text.count("data") + text.count("percent")
        return {"logos": min(100, logos * 20), "pathos": 50, "ethos": 50}

    @staticmethod
    def analyze_intuition(card):
        text = card.get("text", "").lower()
        connectives = ["therefore", "thus", "consequently"]
        score = sum(45 for c in connectives if c in text)
        return min(100, max(10, score))

    @staticmethod
    def calculate_master_clarity(cards):
        try:
            if not cards:
                return 50
            return min(
                100,
                int(sum(OracleEngine.analyze_intuition(c) for c in cards) / len(cards)),
            )
        except Exception:
            return 50

    @staticmethod
    def calculate_strategic_tension(cards):
        tension = len(cards) * 2
        return min(100, int(tension))

    @staticmethod
    def calculate_strategic_weight(cards):
        try:
            if not cards:
                return 50
            weight = sum(
                (c.get("tier", 3) * 20) + (len(c.get("text", "")) // 100) for c in cards
            )
            return min(100, int(weight / (len(cards) if len(cards) > 0 else 1)))
        except Exception:
            return 50

    @staticmethod
    def generate_cx_questions(card):
        return [
            f"How does {card.get('tag')} account for current trends?",
            "What is the specific causal warrant here?",
        ]

    @staticmethod
    def detect_fallacies(text):
        return (
            ["Potential Slippery Slope in link-chain."]
            if "leads to" in text.lower()
            else []
        )

    @staticmethod
    def detect_clash(card, all_cards):
        return [
            c
            for c in all_cards
            if c["side"] != card["side"] and c["tag"][:5] in card["tag"]
        ]

    @staticmethod
    def generate_cx_strategy(card):
        return [
            "Focus on the empirical gap in the warrant.",
            "Pressure the terminal magnitude.",
        ]

    @staticmethod
    def calculate_victory_road(cards):
        pathway_definitions = [
            {
                "name": "Economic Security Path",
                "keywords": [
                    "economy",
                    "economic",
                    "gdp",
                    "trade",
                    "finance",
                    "fiscal",
                    "inflation",
                    "market",
                ],
                "description": "Leverage market stability, trade relations, and fiscal health to establish solvency.",
            },
            {
                "name": "Existential Risk Path",
                "keywords": [
                    "existential",
                    "extinction",
                    "security",
                    "defense",
                    "military",
                    "war",
                    "conflict",
                    "deterrence",
                    "nato",
                ],
                "description": "Argue geopolitical stability and deterrence against systemic or existential threats.",
            },
            {
                "name": "Bio-Survival Path",
                "keywords": [
                    "climate",
                    "warming",
                    "carbon",
                    "greenhouse",
                    "environment",
                    "health",
                    "medical",
                    "disease",
                    "pandemic",
                    "vaccine",
                    "biotech",
                ],
                "description": "Prioritize long-term biosphere protection, public health systems, and ecological resilience.",
            },
        ]

        report = [
            "# 🛣️ VICTORY ROAD ROADMAP",
            "Identify strategic warrant chains to construct an unanswerable route to the ballot.",
            "",
        ]

        for p_def in pathway_definitions:
            pathway_cards = []
            for card in cards:
                card_text = (card.get("tag", "") + " " + card.get("text", "")).lower()
                if any(kw in card_text for kw in p_def["keywords"]):
                    pathway_cards.append(card)

            # Check if available: must have at least one Tier-3 card
            has_tier3 = any(card.get("tier", 1) == 3 for card in pathway_cards)
            available = len(pathway_cards) > 0 and has_tier3

            status_symbol = "🟢 Available" if available else "🔴 Locked"
            report.append(f"## {p_def['name'].upper()}: {status_symbol}")
            report.append(p_def["description"])

            if available:
                # Sort pathway cards by tier ascending, then mastery ascending
                sorted_cards = sorted(
                    pathway_cards, key=lambda c: (c.get("tier", 1), c.get("mastery", 0))
                )

                tags = []
                for idx, c in enumerate(sorted_cards):
                    tag = c.get("tag", "Card")
                    cite = c.get("citation", "")
                    label = f"{tag}" + (f" ({cite})" if cite else "")
                    if idx == 0:
                        tags.append(f"{label} [Link]")
                    elif idx == len(sorted_cards) - 1:
                        tags.append(f"{label} [Terminal Impact]")
                    else:
                        tags.append(f"{label} [Internal Link]")

                sequence_str = " ➔ ".join(tags)
                report.append("**Suggested Speech Flow Sequence**:")
                report.append(f"  `{sequence_str}`")
            else:
                report.append(
                    "*Locked: Requires at least one Tier-3 card in this category to anchor the terminal impact.*"
                )
            report.append("")

        return report

    @staticmethod
    def generate_link_cloud(all_motions):
        return ["# 🌐 LINK-CLOUD", "## SEMANTIC BRIDGES: [Calculated]"]

    @staticmethod
    def simulate_sparring(card):
        tag = card.get("tag", "Untitled")
        side = card.get("side", "AFF").upper()
        mastery = card.get("mastery", 0)
        tier = card.get("tier", 1)

        # Calculate Vulnerability
        vulnerability = max(0, min(100, 100 - (mastery * 20) - (tier * 10)))

        # ─── OPTIONAL GENERATIVE AI PATHWAY ───
        from omnishared.ai import check_ollama_status, generate_completion

        if check_ollama_status():
            try:
                prompt = (
                    "You are a sparring opponent in a competitive forensic debate round.\n"
                    "Analyze the following evidence card:\n"
                    f"TAG: {tag}\n"
                    f"SIDE: {side}\n"
                    f"TEXT: {card.get('text', '')}\n\n"
                    "Provide a highly specific, strategically lethal debate attack/disadvantage against this card (under '🔴 OPPONENT CLASH ATTACK'), "
                    "followed by a recommended counter-rebuttal for the debater to defend their card (under '🟢 RECOMMENDED COUNTER-REBUTTAL').\n"
                    "Keep your response structured exactly as follows (use markdown, do not add headers other than the ones specified):\n"
                    "OPPONENT ATTACK:\n"
                    "[Your strategic attack here]\n\n"
                    "COUNTER-REBUTTAL:\n"
                    "[Your recommended counter-rebuttal defense here]"
                )
                response = generate_completion(
                    prompt,
                    system_prompt="You are a debate coach and grandmaster forensician.",
                )
                if response:
                    opp_attack = ""
                    c_rebuttal = ""
                    if (
                        "OPPONENT ATTACK:" in response
                        and "COUNTER-REBUTTAL:" in response
                    ):
                        parts = response.split("COUNTER-REBUTTAL:")
                        opp_attack = parts[0].replace("OPPONENT ATTACK:", "").strip()
                        c_rebuttal = parts[1].strip()
                    elif "OPPONENT ATTACK:" in response:
                        opp_attack = response.replace("OPPONENT ATTACK:", "").strip()
                        c_rebuttal = "Focus on the empirical warrant and outweigh on impact magnitude."
                    else:
                        opp_attack = response
                        c_rebuttal = "Analyze the link validity and check for alternative causality."

                    if opp_attack and c_rebuttal:
                        return [
                            "# ⚔️ NEURAL SPARRING (GENERATIVE)",
                            f"**Card Tag**: {tag}",
                            f"**Engagement Vulnerability Rating**: {vulnerability}% (Mastery: {mastery}, Tier: {tier})",
                            "",
                            "## 🔴 OPPONENT CLASH ATTACK",
                            opp_attack,
                            "",
                            "## 🟢 RECOMMENDED COUNTER-REBUTTAL",
                            c_rebuttal,
                        ]
            except Exception:
                pass

        # ─── HEURISTIC FALLBACK ───
        # Categorize
        text_content = (card.get("tag", "") + " " + card.get("text", "")).lower()

        category = None
        if any(
            k in text_content
            for k in [
                "economy",
                "economic",
                "gdp",
                "trade",
                "finance",
                "fiscal",
                "inflation",
                "market",
            ]
        ):
            category = "economy"
        elif any(
            k in text_content
            for k in [
                "climate",
                "warming",
                "carbon",
                "emission",
                "greenhouse",
                "environment",
                "leakage",
            ]
        ):
            category = "climate"
        elif any(
            k in text_content
            for k in [
                "technology",
                "tech",
                "ai",
                "algorithm",
                "digital",
                "cyber",
                "internet",
            ]
        ):
            category = "technology"
        elif any(
            k in text_content
            for k in ["health", "medical", "disease", "pandemic", "vaccine", "biotech"]
        ):
            category = "health"
        elif any(
            k in text_content
            for k in [
                "security",
                "defense",
                "military",
                "war",
                "conflict",
                "deterrence",
                "alliance",
                "nato",
            ]
        ):
            category = "security"

        if side == "AFF":
            if category == "climate":
                opponent_attack = "Climate regulations induce carbon leakage and hurt transition economics, shifting emissions to less regulated jurisdictions."
                counter_rebuttal = "Argue terminal bio-survival impacts out-weigh transition timelines and emphasize historical responsibility."
            elif category == "economy":
                opponent_attack = "Economic intervention causes market distortions, increases public debt, and triggers inflationary pressures."
                counter_rebuttal = "Empirically demonstrate that strategic investment stimulates long-term productivity and reduces systemic risks."
            elif category == "technology":
                opponent_attack = "Rapid technological deployment outpaces regulatory safety frameworks, creating severe systemic vulnerabilities and privacy risks."
                counter_rebuttal = "Establish that early adoption allows for active testing, setting international standards, and proactive threat mitigation."
            elif category == "health":
                opponent_attack = "Centralized health mandates restrict individual liberty, strain public resources, and lead to medical black markets."
                counter_rebuttal = "Argue that public health security is a prerequisite for economic stability and that collective defense prevents catastrophic outbreaks."
            elif category == "security":
                opponent_attack = "Aggressive defense postures escalate security dilemmas, provoking adversaries and making accidental conflict more likely."
                counter_rebuttal = "Show that credible deterrence is the only effective check against expansionist states and preserves regional peace."
            else:
                opponent_attack = "The proposed advocacy lacks solvency, relies on speculative link chains, and triggers severe unintended consequences."
                counter_rebuttal = "Focus on high-probability link pathways, leverage strong empirical evidence, and outweigh on impact magnitude."
        else:  # side == "NEG"
            if category == "climate":
                opponent_attack = "Failing to act on climate change leads to irreversible ecological tipping points, threatening global bio-survival."
                counter_rebuttal = "Highlight structural flaws in climate mitigation models and show that premature transition collapses industrial energy grids."
            elif category == "economy":
                opponent_attack = "Unregulated markets exacerbate income inequality, cause catastrophic financial crises, and neglect public goods."
                counter_rebuttal = "Argue that state intervention stifles innovation, reduces capital efficiency, and harms the poorest through slow growth."
            elif category == "technology":
                opponent_attack = "Stagnation in technology adoption leads to national competitive decline, allowing adversaries to dominate digital frontiers."
                counter_rebuttal = "Highlight critical security gaps, algorithmic biases, and existential threats posed by unchecked tech developments."
            elif category == "health":
                opponent_attack = "Inaction on public health infrastructure leads to preventable mortality, pandemics, and systemic labor shortages."
                counter_rebuttal = "Argue that decentralized or private health initiatives are more agile, cost-effective, and avoid state overreach."
            elif category == "security":
                opponent_attack = "Isolationism and lack of international commitments weaken alliances, inviting foreign aggression and instability."
                counter_rebuttal = "Point out that overextension and foreign interventions lead to resource exhaustion and drag the nation into endless conflicts."
            else:
                opponent_attack = "Rejecting the status quo alternative leads to systemic stagnation and fails to address urgent structural harms."
                counter_rebuttal = "Expose the logical leaps in the opponent's solvency mechanism and emphasize status quo resilience."

        return [
            "# ⚔️ NEURAL SPARRING",
            f"**Card Tag**: {tag}",
            f"**Engagement Vulnerability Rating**: {vulnerability}% (Mastery: {mastery}, Tier: {tier})",
            "",
            "## 🔴 OPPONENT CLASH ATTACK",
            opponent_attack,
            "",
            "## 🟢 RECOMMENDED COUNTER-REBUTTAL",
            counter_rebuttal,
        ]

    @staticmethod
    def simulate_judge(cards):
        if not cards:
            return [
                "# ⚖️ NEURAL JUDGE BALLOT",
                "### **Decision**: Indeterminate (No cards in the vault)",
                "Please add evidence cards to both sides to run the ballot simulation.",
            ]

        aff_cards = [c for c in cards if c.get("side", "").upper() == "AFF"]
        neg_cards = [c for c in cards if c.get("side", "").upper() == "NEG"]

        def compute_side_score(side_cards):
            if not side_cards:
                return 0.0
            count = len(side_cards)
            avg_tier = sum(c.get("tier", 1) for c in side_cards) / count
            avg_mastery = sum(c.get("mastery", 0) for c in side_cards) / count
            # Weighted formula
            return (count * 2.0) + (avg_tier * 5.0) + (avg_mastery * 3.0)

        aff_score = compute_side_score(aff_cards)
        neg_score = compute_side_score(neg_cards)

        if aff_score >= neg_score:
            winner = "AFF"
            loser = "NEG"
            winning_cards = aff_cards
            losing_cards = neg_cards
        else:
            winner = "NEG"
            loser = "AFF"
            winning_cards = neg_cards
            losing_cards = aff_cards

        total_score = aff_score + neg_score
        if total_score > 0:
            confidence = int(50 + (abs(aff_score - neg_score) / total_score) * 49)
        else:
            confidence = 50

        # Find key voting issue card (highest tier/mastery)
        if winning_cards:
            key_card = max(
                winning_cards,
                key=lambda c: (c.get("tier", 1) * 100) + c.get("mastery", 0),
            )
            key_tag = key_card.get("tag", "evidence")
            key_cite = key_card.get("citation", "")
            cite_str = f" [{key_cite}]" if key_cite else ""
        else:
            key_card = None
            key_tag = "evidence"
            cite_str = ""

        # Craft heuristic fallback values in case AI fails
        # Craft RFD
        text_content = (
            key_tag + " " + (key_card.get("text", "") if key_card else "")
        ).lower()
        clash_description = "the broad structural layout of the debate"
        if any(
            k in text_content
            for k in [
                "economy",
                "economic",
                "gdp",
                "trade",
                "finance",
                "fiscal",
                "inflation",
                "market",
            ]
        ):
            clash_description = (
                "the economic impacts and resource allocation trade-offs"
            )
        elif any(
            k in text_content
            for k in [
                "climate",
                "warming",
                "carbon",
                "emission",
                "greenhouse",
                "environment",
                "leakage",
            ]
        ):
            clash_description = "climate warming, environmental regulations, and ecological sustainability"
        elif any(
            k in text_content
            for k in [
                "technology",
                "tech",
                "ai",
                "algorithm",
                "digital",
                "cyber",
                "internet",
            ]
        ):
            clash_description = (
                "technological disruption, digital security, and governance timelines"
            )
        elif any(
            k in text_content
            for k in ["health", "medical", "disease", "pandemic", "vaccine", "biotech"]
        ):
            clash_description = (
                "public health readiness, pandemic risk, and medical infrastructure"
            )
        elif any(
            k in text_content
            for k in [
                "security",
                "defense",
                "military",
                "war",
                "conflict",
                "deterrence",
                "alliance",
                "nato",
            ]
        ):
            clash_description = "geopolitical security, deterrence frameworks, and conflict escalation risks"

        if winner == "AFF":
            rfd = f"The Affirmative team secured the ballot primarily by winning the clash on {clash_description}. AFF's core card '{key_tag}'{cite_str} established a clear causal pathway, supported by empirical evidence, demonstrating a high-probability link to their terminal impact. The Negative's responses failed to adequately mitigate this systemic advantage, leaving the AFF's solvency narrative largely intact at the end of the round."
        else:
            rfd = f"The Negative team won the ballot by successfully defending against the Affirmative's solvency claims and winning the clash on {clash_description}. NEG's core defense '{key_tag}'{cite_str} demonstrated key logical vulnerabilities in the AFF's link-chain, showing that the proposed plan leads to significant unintended consequences. With the AFF's terminal impacts mitigated or turned, the NEG's defense stood as the more robust framework."

        # Strategic Feedback
        if not losing_cards:
            feedback = f"{loser} suffered from a complete lack of evidence cards. You must add cards to this side to mount a viable defense."
        else:
            loser_count = len(losing_cards)
            avg_tier = sum(c.get("tier", 1) for c in losing_cards) / loser_count
            avg_mastery = sum(c.get("mastery", 0) for c in losing_cards) / loser_count
            winner_count = len(winning_cards)

            if avg_mastery < 2:
                feedback = f"{loser} suffered from low average card mastery. Focus on practicing speech delivery and spoken card drills to increase mastery ratings."
            elif avg_tier < 2:
                feedback = f"{loser} relied too heavily on low-tier evidence. Prioritize researching and deploying Tier-3 cards to anchor your critical strategic pathways."
            elif winner_count - loser_count >= 2:
                feedback = f"{loser} suffered from low empirical density and a thin evidence pool. AFF/NEG card disparity allowed the opponent to overwhelm defenses."
            else:
                feedback = f"{loser} suffered from weak link defenses in key areas of clash. Deepen your causal warrants and focus on turning the opponent's core impacts."

        # ─── OPTIONAL GENERATIVE AI PATHWAY ───
        from omnishared.ai import check_ollama_status, generate_completion

        if check_ollama_status():
            try:
                aff_details = "\n".join(
                    f"- TAG: {c.get('tag')} | CITE: {c.get('citation')} | TEXT: {c.get('text')[:300]}"
                    for c in aff_cards
                )
                neg_details = "\n".join(
                    f"- TAG: {c.get('tag')} | CITE: {c.get('citation')} | TEXT: {c.get('text')[:300]}"
                    for c in neg_cards
                )
                prompt = (
                    "You are a debate judge evaluating a round based on the following evidence cards:\n\n"
                    "=== AFFIRMATIVE CARDS ===\n"
                    f"{aff_details}\n\n"
                    "=== NEGATIVE CARDS ===\n"
                    f"{neg_details}\n\n"
                    "Evaluate the clash between the arguments. Decide the winner (AFF or NEG). "
                    "Provide a Reason for Decision (RFD), identify a Key Voting Issue (KVI) card from the winning side, "
                    "and offer strategic feedback to the losing side.\n"
                    "Format your response exactly as follows:\n"
                    "DECISION: [AFF or NEG]\n"
                    "CONFIDENCE: [A number between 50 and 99 representing your confidence percentage]\n"
                    "RFD:\n"
                    "[Your reason for decision detailing why the winning team won the clash]\n\n"
                    "KEY VOTING ISSUE:\n"
                    "Card: [Winning Card Tag] [Citation]\n"
                    "[Brief explanation of why this card anchored the decision]\n\n"
                    "STRATEGIC FEEDBACK:\n"
                    "[Specific, constructive feedback for the losing side to improve their strategy]"
                )
                response = generate_completion(
                    prompt,
                    system_prompt="You are a professional forensics judge who awards ballots based on logical warrant evaluation and clash impact weighing.",
                )
                if response:
                    ai_decision = winner
                    ai_confidence = confidence
                    rfd_text = ""
                    kvi_card = key_tag + (f" ({key_cite})" if key_cite else "")
                    kvi_expl = ""
                    feedback_text = ""

                    lines = response.splitlines()
                    current_section = None
                    rfd_lines = []
                    kvi_lines = []
                    feedback_lines = []

                    for line in lines:
                        if line.startswith("DECISION:"):
                            ai_decision = line.replace("DECISION:", "").strip()
                        elif line.startswith("CONFIDENCE:"):
                            try:
                                ai_confidence = int(re.sub(r"\D", "", line))
                            except Exception:
                                pass
                        elif line.startswith("RFD:"):
                            current_section = "rfd"
                        elif line.startswith("KEY VOTING ISSUE:"):
                            current_section = "kvi"
                        elif line.startswith("STRATEGIC FEEDBACK:"):
                            current_section = "feedback"
                        else:
                            if current_section == "rfd":
                                rfd_lines.append(line)
                            elif current_section == "kvi":
                                kvi_lines.append(line)
                            elif current_section == "feedback":
                                feedback_lines.append(line)

                    rfd_text = "\n".join(rfd_lines).strip()
                    feedback_text = "\n".join(feedback_lines).strip()

                    # Parse KVI card
                    kvi_all = "\n".join(kvi_lines).strip()
                    if kvi_all.startswith("Card:"):
                        kvi_parts = kvi_all.split("\n", 1)
                        kvi_card = kvi_parts[0].replace("Card:", "").strip()
                        if len(kvi_parts) > 1:
                            kvi_expl = kvi_parts[1].strip()
                    else:
                        kvi_expl = kvi_all

                    if not rfd_text:
                        rfd_text = rfd
                    if not feedback_text:
                        feedback_text = feedback

                    return [
                        "# ⚖️ NEURAL JUDGE BALLOT (GENERATIVE)",
                        f"### **Decision**: {ai_decision} Wins ({ai_confidence}% Confidence)",
                        "",
                        "## 📝 REASON FOR DECISION (RFD)",
                        rfd_text,
                        "",
                        "## 🔑 KEY VOTING ISSUE",
                        f"**Card**: {kvi_card}",
                        kvi_expl
                        or "This card anchored the decision due to its superior warrant structure and impact weighing.",
                        "",
                        "## 🎯 STRATEGIC FEEDBACK",
                        feedback_text,
                    ]
            except Exception:
                pass

        # Return standard heuristic fallback
        return [
            "# ⚖️ NEURAL JUDGE BALLOT",
            f"### **Decision**: {winner} Wins ({confidence}% Confidence)",
            "",
            "## 📝 REASON FOR DECISION (RFD)",
            rfd,
            "",
            "## 🔑 KEY VOTING ISSUE",
            f"**Card**: {key_tag}{cite_str}",
            f"This card anchored the round due to its high tier (Tier {key_card.get('tier', 1) if key_card else 1}) and mastery (Mastery {key_card.get('mastery', 0) if key_card else 0}).",
            "",
            "## 🎯 STRATEGIC FEEDBACK",
            feedback,
        ]

    @staticmethod
    def generate_research_queue(cards):
        if not cards:
            return [
                "# 📋 STRATEGIC RESEARCH QUEUE",
                "### **Status**: Empty Vault",
                "Please add evidence cards to analyze gaps in the research queue.",
            ]

        aff_cards = [c for c in cards if c.get("side", "").upper() == "AFF"]
        neg_cards = [c for c in cards if c.get("side", "").upper() == "NEG"]

        gaps = []
        search_terms = []

        # 1. Flag category imbalances (Side Defense Gaps)
        aff_count = len(aff_cards)
        neg_count = len(neg_cards)
        if abs(aff_count - neg_count) >= 3:
            if aff_count > neg_count:
                gaps.append(
                    {
                        "title": "⚠️ NEGATIVE DEFENSE GAP",
                        "description": f"Affirmative has {aff_count} cards while Negative has only {neg_count} cards. The Negative side is highly vulnerable to being overwhelmed in empirical density.",
                    }
                )
                search_terms.extend(
                    [
                        "Negative disadvantages to motion",
                        "Counter-warrants status quo resilience",
                        "Alternative solvency mechanisms debate",
                    ]
                )
            else:
                gaps.append(
                    {
                        "title": "⚠️ AFFIRMATIVE ADVOCACY GAP",
                        "description": f"Negative has {neg_count} cards while Affirmative has only {aff_count} cards. The Affirmative side lacks sufficient proactive advocacy warrants.",
                    }
                )
                search_terms.extend(
                    [
                        "Affirmative solvency policy reform",
                        "Plan benefits empirical outcomes",
                        "Advocacy advantages structural change",
                    ]
                )

        # 2. Check for missing logical links
        all_text = " ".join(
            (c.get("tag", "") + " " + c.get("text", "")).lower() for c in cards
        )

        has_climate = any(
            k in all_text for k in ["climate", "warming", "carbon", "greenhouse"]
        )
        has_climate_terminal = any(
            k in all_text
            for k in [
                "migration",
                "collapse",
                "famine",
                "extinction",
                "survival",
                "catastrophe",
            ]
        )

        if has_climate and not has_climate_terminal:
            gaps.append(
                {
                    "title": "⚠️ MISSING TERMINAL LINK: CLIMATE BIO-SURVIVAL",
                    "description": "The evidence pool contains climate warming arguments, but lacks cards linking climate change to terminal human impacts (e.g., climate-induced migration, agricultural collapse, or extinction risks).",
                }
            )
            search_terms.extend(
                [
                    "climate warming agricultural collapse",
                    "climate change migration conflict link",
                    "ecological catastrophe human extinction",
                ]
            )

        has_economy = any(k in all_text for k in ["economy", "gdp", "trade", "finance"])
        has_economy_terminal = any(
            k in all_text
            for k in ["security", "conflict", "war", "stability", "hegemony"]
        )

        if has_economy and not has_economy_terminal:
            gaps.append(
                {
                    "title": "⚠️ MISSING TERMINAL LINK: ECONOMIC STABILITY",
                    "description": "The evidence pool has economic growth/trade arguments, but lacks cards linking economic downturns or trade disruptions to terminal impacts like conflict, geopolitical hegemony loss, or social instability.",
                }
            )
            search_terms.extend(
                [
                    "economic recession geopolitical conflict link",
                    "trade disruption hegemony decline",
                    "economic crisis systemic war risk",
                ]
            )

        has_tech = any(k in all_text for k in ["technology", "tech", "ai", "algorithm"])
        has_tech_terminal = any(
            k in all_text
            for k in ["extinction", "catastrophe", "safety", "existential", "control"]
        )

        if has_tech and not has_tech_terminal:
            gaps.append(
                {
                    "title": "⚠️ MISSING TERMINAL LINK: TECHNOLOGICAL SAFEGUARDS",
                    "description": "The evidence pool has technology adoption/growth arguments, but lacks cards linking unchecked technological development to terminal existential risk or control failures.",
                }
            )
            search_terms.extend(
                [
                    "artificial general intelligence existential risk control",
                    "cyber security infrastructure vulnerability impact",
                    "emerging technology existential threat governance",
                ]
            )

        # Default if no gaps found
        if not gaps:
            gaps.append(
                {
                    "title": "🟢 NO MAJOR LOGICAL GAPS DETECTED",
                    "description": "The current evidence pool shows a balanced distribution of arguments and stable link pathways across both sides.",
                }
            )
            search_terms.extend(
                [
                    "motion empirical studies 2025",
                    "systemic review impact assessment policy",
                    "recent debate literature analysis",
                ]
            )

        # Deduplicate search terms
        unique_terms = []
        for term in search_terms:
            if term not in unique_terms:
                unique_terms.append(term)

        # Format report
        report = [
            "# 📋 STRATEGIC RESEARCH QUEUE",
            "Identify logical gaps and generate targeted search terms to strengthen your case.",
            "",
        ]

        report.append("## 🔍 IDENTIFIED GAPS")
        for g in gaps:
            report.append(f"### {g['title']}")
            report.append(g["description"])
            report.append("")

        report.append("## 🎯 ACTIONABLE RESEARCH SEARCH TERMS")
        for term in unique_terms:
            report.append(f"*   `{term}`")

        return report

    @staticmethod
    def analyze_linguistics(card):
        text = card.get("text", "").lower()
        markers = ["study", "proves", "indicates"]
        score = sum(30 for m in markers if m in text)
        return min(100, max(10, score))

    @staticmethod
    def generate_flow_outline(cards):
        return [
            "# 📜 SPEECH FLOW OUTLINE",
            "## 1AC: [Automated]",
            "## 1NC: [Predicted]",
        ]

    @staticmethod
    def calculate_balance(cards):
        return 50

    @staticmethod
    def analyze_matrix(cards):
        return [{"tag": c.get("tag", "Card"), "m": 3, "p": 3} for c in cards[:10]]

    @staticmethod
    def synthesize_rebuttal_block(card):
        tag = card.get("tag", "Untitled")
        side = card.get("side", "AFF").upper()
        text = card.get("text", "")

        from omnishared.ai import check_ollama_status, generate_completion

        if check_ollama_status():
            try:
                prompt = (
                    "You are a debate consultant. Construct a structured 'Rebuttal Speech Block' defending against or answering the following card:\n"
                    f"TAG: {tag}\n"
                    f"SIDE: {side}\n"
                    f"TEXT: {text}\n\n"
                    "Output exactly in this format (use markdown, do not add other headers):\n"
                    "# 🛡️ REBUTTAL SPEECH BLOCK (GENERATIVE)\n"
                    "## LINK-DEFENSE:\n"
                    "[Your link defense argument against their causal chain]\n\n"
                    "## TURN-PROBABILITY:\n"
                    "[Your turn/counter-impact argument showing why the opponent's claim turns against them]"
                )
                response = generate_completion(
                    prompt,
                    system_prompt="You are a debate consultant specialized in card turn strategies and link defense.",
                )
                if response:
                    lines = response.splitlines()
                    link_def = ""
                    turn_prob = ""
                    current = None
                    ld_lines = []
                    tp_lines = []
                    for line in lines:
                        if "LINK-DEFENSE:" in line:
                            current = "ld"
                        elif "TURN-PROBABILITY:" in line:
                            current = "tp"
                        else:
                            if current == "ld":
                                ld_lines.append(line)
                            elif current == "tp":
                                tp_lines.append(line)

                    link_def = "\n".join(ld_lines).strip()
                    turn_prob = "\n".join(tp_lines).strip()

                    if link_def or turn_prob:
                        return [
                            "# 🛡️ REBUTTAL SPEECH BLOCK (GENERATIVE)",
                            "## LINK-DEFENSE:",
                            link_def or "No specific defense suggested.",
                            "",
                            "## TURN-PROBABILITY:",
                            turn_prob or "No turn suggested.",
                        ]
            except Exception:
                pass

        return [
            "# 🛡️ REBUTTAL SPEECH BLOCK",
            "## LINK-DEFENSE: [Active]",
            "## TURN-PROBABILITY: [Low]",
        ]

    @staticmethod
    def log_round_progression(card_id, time):
        return f"TIMELINE: Card {card_id} Mastered at T+{time}s."

    @staticmethod
    def calculate_resilience(card):
        text = card.get("text", "").lower()
        warrants = ["because", "since", "proves"]
        score = sum(10 for w in warrants if w in text)
        return min(95, max(10, score))

    @staticmethod
    def weigh_evidence(card_a: dict, card_b: dict) -> dict:
        """Heuristically weigh two evidence cards against each other."""
        res_a = OracleEngine.calculate_resilience(card_a)
        res_b = OracleEngine.calculate_resilience(card_b)

        # Warrant density
        w_markers = ["because", "since", "therefore", "warrants", "causality", "link"]
        w_count_a = sum(card_a.get("text", "").lower().count(m) for m in w_markers)
        w_density_a = min(100, max(10, w_count_a * 25))
        w_count_b = sum(card_b.get("text", "").lower().count(m) for m in w_markers)
        w_density_b = min(100, max(10, w_count_b * 25))

        # Fact-Level Evidence Score
        f_markers = [
            "study",
            "proves",
            "shows",
            "indicates",
            "analysis",
            "empirical",
            "data",
            "percent",
            "%",
        ]
        f_count_a = sum(card_a.get("text", "").lower().count(m) for m in f_markers)
        f_score_a = min(100, max(10, f_count_a * 20))
        f_count_b = sum(card_b.get("text", "").lower().count(m) for m in f_markers)
        f_score_b = min(100, max(10, f_count_b * 20))

        # Core weighted scoring including tier and mastery
        tier_a = card_a.get("tier", 1)
        tier_b = card_b.get("tier", 1)
        mastery_a = card_a.get("mastery", 0)
        mastery_b = card_b.get("mastery", 0)

        score_a = int(
            (tier_a * 25)
            + (mastery_a * 10)
            + (res_a * 0.1)
            + (w_density_a * 0.1)
            + (f_score_a * 0.1)
        )
        score_b = int(
            (tier_b * 25)
            + (mastery_b * 10)
            + (res_b * 0.1)
            + (w_density_b * 0.1)
            + (f_score_b * 0.1)
        )

        diff = abs(score_a - score_b)
        if score_a > score_b:
            winner = "A"
        elif score_b > score_a:
            winner = "B"
        else:
            winner = "TIE"

        return {
            "winner": winner,
            "diff": diff,
            "score_a": score_a,
            "score_b": score_b,
            "resilience_a": res_a,
            "resilience_b": res_b,
            "warrant_density_a": w_density_a,
            "warrant_density_b": w_density_b,
            "fact_score_a": f_score_a,
            "fact_score_b": f_score_b,
        }

    @staticmethod
    def auto_redact_text(text, role="1AC"):
        """Performs multi-color forensic syntax highlighting based on semantic role."""
        if not text:
            return ""
        try:
            # 🎨 Color Mapping: Gold (Warrants), Red (Impacts), Emerald (Empirical)
            warrants = ["because", "since", "therefore", "warrant", "causality", "link"]
            impacts = [
                "victory",
                "mastery",
                "singularity",
                "extinction",
                "catastrophe",
                "terminal",
            ]
            empirical = [
                "study",
                "proves",
                "indicates",
                "data",
                "empirical",
                "analysis",
            ]

            redacted = text
            # Highlight Warrants (Gold/Underline)
            for w in warrants:
                redacted = re.sub(
                    f"(?i)({w})", r"[b][u][#f59e0b]\1[/#f59e0b][/u][/b]", redacted
                )

            # Highlight Impacts (Red/Bold)
            for i in impacts:
                redacted = re.sub(
                    f"(?i)({i})", r"[b][#ef4444]\1[/#ef4444][/b]", redacted
                )

            # Highlight Empirical (Emerald/Bold)
            for e in empirical:
                redacted = re.sub(
                    f"(?i)({e})", r"[b][#10b981]\1[/#10b981][/b]", redacted
                )

            return redacted
        except Exception:
            return text
