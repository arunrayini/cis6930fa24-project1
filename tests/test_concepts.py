import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import redactor

def test_redact_concepts():
    sample_text = "Jack pursued his journey. He encountered a giant who was very dangerous."
    expected_output = "Jack pursued his journey. ██████████████████████████████████████████████"

    redaction_counts = {'CONCEPT': 0}
    redacted_text = redactor.redact_concepts(sample_text, ["giant"], redaction_counts)
    

    # Assert the redacted text matches the expected output
    assert redacted_text == expected_output, f"Expected: {expected_output}, but got: {redacted_text}"
