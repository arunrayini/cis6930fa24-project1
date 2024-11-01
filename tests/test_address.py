import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import redactor

def test_redact_address():
    sample_text = "Send the package to 221B Baker Street"
    expected_output = "Send the package to ████ ████████████"
    redaction_counts = {'address': 0}
    assert redactor.redact_street_addresses(sample_text, redaction_counts) == expected_output
    assert redaction_counts['address'] == 2  # 1 for street number, 1 for street name
