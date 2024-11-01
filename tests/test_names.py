import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import redactor

def test_redact_names():
    sample_text = "John Doe contacted Mary at her house."
    expected_output = "████████ contacted ████ at her house."
    redaction_counts = {'names': 0}
    redacted_text = redactor.redact_text(sample_text, ["names"], redaction_counts)
    redacted_text = redactor.redact_emails(redacted_text, redaction_counts)  # Handles the email redaction
    assert redacted_text == expected_output
    assert redaction_counts['names'] == 2  # Two names and one email
