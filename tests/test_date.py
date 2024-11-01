import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import redactor

def test_redact_dates():
    sample_text = "The meeting is scheduled for Monday at 10:30 AM on 10/12/2023"
    expected_output = "The meeting is scheduled for Monday at ████████ on ██/██/████"

    redaction_counts = {'DATE': 0}
    redacted_text = redactor.redact_dates(sample_text, redaction_counts)

    # Assert the redacted text matches the expected output
    assert redacted_text == expected_output, f"Expected: {expected_output}, but got: {redacted_text}"
