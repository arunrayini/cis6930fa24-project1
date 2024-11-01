import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import redactor

def test_redact_phones():
    sample_text = "Call me at (123) 456-7890 or at 123.456.7890."
    expected_output = "Call me at ██████████████ or at ████████████."
    redaction_counts = {'PHONE': 0}
    assert redactor.redact_phones(sample_text, redaction_counts) == expected_output
    assert redaction_counts['PHONE'] == 2  # Two phone numbers
