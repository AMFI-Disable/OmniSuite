import os
import json
from omnishared.config import FORMATS_FILE


def load_formats() -> dict:
    if os.path.exists(FORMATS_FILE):
        try:
            with open(FORMATS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback built-in
    return {
        "Public Forum": {
            "prep_time_seconds": 180,
            "speeches": [
                {"name": "Opening Statement (Team A)", "duration_seconds": 240},
                {"name": "Opening Statement (Team B)", "duration_seconds": 240},
                {"name": "Crossfire", "duration_seconds": 180},
                {"name": "Rebuttal (Team A)", "duration_seconds": 240},
                {"name": "Rebuttal (Team B)", "duration_seconds": 240},
                {"name": "Crossfire", "duration_seconds": 180},
                {"name": "Summary (Team A)", "duration_seconds": 180},
                {"name": "Summary (Team B)", "duration_seconds": 180},
                {"name": "Grand Crossfire", "duration_seconds": 180},
                {"name": "Final Focus (Team A)", "duration_seconds": 120},
                {"name": "Final Focus (Team B)", "duration_seconds": 120},
            ],
        },
        "Lincoln-Douglas": {
            "prep_time_seconds": 240,
            "speeches": [
                {"name": "Affirmative Constructive", "duration_seconds": 360},
                {"name": "Cross-Examination (Neg asking)", "duration_seconds": 180},
                {"name": "Negative Constructive", "duration_seconds": 420},
                {"name": "Cross-Examination (Aff asking)", "duration_seconds": 180},
                {"name": "First Affirmative Rebuttal", "duration_seconds": 240},
                {"name": "Negative Rebuttal", "duration_seconds": 360},
                {"name": "Second Affirmative Rebuttal", "duration_seconds": 180},
            ],
        },
        "Policy": {
            "prep_time_seconds": 480,
            "speeches": [
                {"name": "1AC", "duration_seconds": 480},
                {"name": "CX (2NC asks)", "duration_seconds": 180},
                {"name": "1NC", "duration_seconds": 480},
                {"name": "CX (1AC asks)", "duration_seconds": 180},
                {"name": "2AC", "duration_seconds": 480},
                {"name": "CX (1NC asks)", "duration_seconds": 180},
                {"name": "2NC", "duration_seconds": 480},
                {"name": "CX (2AC asks)", "duration_seconds": 180},
                {"name": "1NR", "duration_seconds": 300},
                {"name": "1AR", "duration_seconds": 300},
                {"name": "2NR", "duration_seconds": 300},
                {"name": "2AR", "duration_seconds": 300},
            ],
        },
    }
