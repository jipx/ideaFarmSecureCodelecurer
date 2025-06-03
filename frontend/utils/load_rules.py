import json
import os

# File path where the grading rules are stored locally
RULES_FILE_PATH = "grading_rules.json"

def load_rules():
    """Load grading rules from the local JSON file. If not found, return default rules."""
    if os.path.exists(RULES_FILE_PATH):
        # Load existing rules from file
        with open(RULES_FILE_PATH, "r") as f:
            return json.load(f)
    else:
        # Return default rule set if file doesn't exist
        return {
            "allowed_extensions": [".js", ".py"],  # Acceptable file types
            "exclude_dirs": ["node_modules", "__pycache__"],  # Skip these folders during grading
            "required_security_patterns": ["sanitizeInput", "usePreparedStatements"],  # Security patterns to check for
            "min_score_threshold": 60  # Passing threshold
        }

def save_rules(rules: dict):
    """Save the grading rules to the local JSON file."""
    with open(RULES_FILE_PATH, "w") as f:
        json.dump(rules, f, indent=2)  # Write rules with indentation for readability# Local rule loader