import sys
import spacy
import re  # Importing the 're' module for regex operations
import argparse
import os
import glob

import nltk
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

# Loading the spaCy model
nlp = spacy.load("en_core_web_md")

# List of common city names to ensure they are redacted, including "Riverside"
COMMON_CITY_NAMES = ["Riverside", "New York", "Los Angeles", "Houston", "Chicago", "Phoenix", "Philadelphia","London", "San Antonio", "San Diego"]

def parse_arguments():
    """Parse command-line arguments for redaction."""
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files.")
    
    # Input files and output directory
    parser.add_argument('--input', required=True, help='Input text files (glob pattern)', nargs='+')
    parser.add_argument('--output', required=True, help='Output directory for redacted files')
    
    # Redaction flags
    parser.add_argument('--names', action='store_true', help='Redact names (includes emails and PERSON entities)')
    parser.add_argument('--dates', action='store_true', help='Redact dates')
    parser.add_argument('--phones', action='store_true', help='Redact phone numbers')
    parser.add_argument('--address', action='store_true', help='Redact addresses (includes ORG, GPE)')
    parser.add_argument('--concept', action='append', help='Redact specified concept(s)', required=False)

    # Stats output
    parser.add_argument('--stats', help='Location to write redaction statistics (stdout, stderr, or file)', default='stdout')
    
    return parser.parse_args()

def redact_text(text, entities_to_redact, redaction_counts):
    """Redact specified entity types using spaCy NER and track redaction counts."""
    doc = nlp(text)
    redacted_text = text

    for ent in doc.ents:
        # Treating PERSON as names
        if ent.label_ == 'PERSON' and 'names' in entities_to_redact:
            redacted_text = redacted_text.replace(ent.text, "█" * len(ent.text))
            redaction_counts['names'] += 1

        # Treating ORG and GPE as addresses
        elif ent.label_ in ['ORG', 'GPE'] and 'address' in entities_to_redact:
            redacted_text = redacted_text.replace(ent.text, "█" * len(ent.text))
            redaction_counts['address'] += 1

        # Handling other redactions (dates, phones)
        elif ent.label_ == 'DATE' and 'DATE' in entities_to_redact:
            redacted_text = redacted_text.replace(ent.text, "█" * len(ent.text))
            redaction_counts['DATE'] += 1

    return redacted_text

def redact_emails(text, redaction_counts):
    """Redact email addresses using regex and count as names."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    redacted_text = re.sub(email_pattern, lambda x: '█' * len(x.group()), text)
    redaction_counts['names'] += len(re.findall(email_pattern, text))  # Counting redacted emails under names
    return redacted_text

def redact_street_addresses(text, redaction_counts):
    """Redact street numbers, street names, city names, and state abbreviations using regex."""
    # Street numbers (e.g., 742, 221B)
    street_number_pattern = r'\b\d+[A-Za-z]?\b'
    redacted_text = re.sub(street_number_pattern, lambda x: '█' * len(x.group()), text)

    # Expanded to cover street names, city names, and state abbreviations
    street_name_pattern = r'\b(?:[A-Za-z]+\s?){1,4}(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Lane|Dr|Drive|Pl|Place|Terrace|Row|Park|Court|Circle|Way|Crescent|Square|Grove|Hill|Riverside)\b'
    redacted_text = re.sub(street_name_pattern, lambda x: '█' * len(x.group()), redacted_text)

    # State abbreviations like TX, NY, CA, etc.
    state_pattern = r'\b(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b'
    redacted_text = re.sub(state_pattern, lambda x: '█' * len(x.group()), redacted_text)

    redaction_counts['address'] += len(re.findall(street_number_pattern, text)) + len(re.findall(street_name_pattern, text)) + len(re.findall(state_pattern, text))

    # Explicitly redacting city names from the COMMON_CITY_NAMES list
    for city in COMMON_CITY_NAMES:
        redacted_text = re.sub(rf'\b{city}\b', lambda x: '█' * len(x.group()), redacted_text)
        redaction_counts['address'] += len(re.findall(rf'\b{city}\b', text))

    return redacted_text

def get_related_words(concept):
    """Retrieve synonyms and related words for a concept using WordNet and include plural forms."""
    related_words = set([concept.lower()])  # Starting with the concept itself
    
    # Retrieving synonyms and hypernyms from WordNet
    for synset in wn.synsets(concept):
        # Synonyms and their morphological variations
        for lemma in synset.lemmas():
            word = lemma.name().replace('_', ' ')
            related_words.add(word.lower())
            # Morphological variations, such as plurals
            if not word.endswith('s'):
                related_words.add(word.lower() + 's')
        
        # Including hypernyms (higher-level concepts for broader redaction)
        for hypernym in synset.hypernyms():
            for lemma in hypernym.lemmas():
                word = lemma.name().replace('_', ' ')
                related_words.add(word.lower())
                if not word.endswith('s'):
                    related_words.add(word.lower() + 's')

    # Using WordNet's morphs to find additional compounds without manual inclusion
    for word in list(related_words):
        compound_forms = wn.morphy(word)
        if compound_forms:
            related_words.add(compound_forms.lower())
    
    return related_words

def redact_concepts(text, concepts, redaction_counts):
    """Redact sentences containing the concept or any related words, including variations and compounds."""
    all_related_words = set()
    
    # Expanding all related terms for each concept and add variations
    for concept in concepts:
        related_words = get_related_words(concept)
        related_words.add(concept)  # Including the concept itself
        all_related_words.update(related_words)

    # Creating a regex pattern to match concept terms without strict word boundaries
    concept_pattern = r'(?<!\w)(?:' + '|'.join(re.escape(word) for word in all_related_words) + r')(?!\w)'
    
    # Splitting text into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)  # Splitting by sentence end punctuation

    # Redacting sentences containing any form of the concept
    redacted_text = []
    for sentence in sentences:
        if re.search(concept_pattern, sentence, re.IGNORECASE):  # Checking if any related term is present
            redacted_text.append("█" * len(sentence))  # Redacting the entire sentence
            redaction_counts['CONCEPT'] += 1  # Incrementing redaction count
        else:
            redacted_text.append(sentence)  # Keeping sentence as-is

    # Joining all sentences back together
    return ' '.join(redacted_text)

def redact_dates(text, redaction_counts):
    """Redact dates in various formats, including day names and years."""
    # Patterns to cover years (4 digits), day names, and full dates with times
    date_patterns = [
        r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b',  # Days of the week
        r'\b\d{1,2} [A-Za-z]+ \d{4}\b',  # Full date (e.g., 18 Apr 2001)
        r'\b\d{4}\b',  # Years (e.g., 2001)
        r'\b\d{1,2}:\d{2} ?(?:AM|PM|am|pm)?\b',  # Times with optional AM/PM
        r'\b\d{1,2}(st|nd|rd|th)?\b',  # Ordinal dates (e.g., 14th)
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'  # Dates with slashes or hyphens (e.g., 10/12/2023)
    ]

    redacted_text = text
    for pattern in date_patterns:
        redacted_text = re.sub(pattern, lambda x: '█' * len(x.group()), redacted_text)
        redaction_counts['DATE'] += len(re.findall(pattern, text))

    return redacted_text

def redact_phones(text, redaction_counts):
    """Redact phone numbers and count them."""
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    redacted_text = re.sub(phone_pattern, lambda x: '█' * len(x.group()), text)
    redaction_counts['PHONE'] += len(re.findall(phone_pattern, text))
    return redacted_text

def process_files(input_patterns, output_dir, args):
    """Process each input file, apply redactions, and save the results."""

    output_dir = "files"  # Directory to save redacted files with .censored extension
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing files, output will be saved in '{output_dir}'")

    # Expanding glob patterns into file paths
    input_files = []
    for pattern in input_patterns:
        expanded_files = glob.glob(pattern, recursive=True)
        input_files.extend(expanded_files)

    if not input_files:
        print(f"No files found matching the pattern: {input_patterns}")
        return

    print(f"Processing the following files: {input_files}")

    entities_to_redact = []
    if args.names:
        entities_to_redact.append("names")
    if args.dates:
        entities_to_redact.append("DATE")
    if args.address:
        entities_to_redact.append("address")

    for file in input_files:
        redaction_counts = {
            'names': 0,
            'DATE': 0,
            'PHONE': 0,
            'address': 0,
            'CONCEPT': 0
        }

        if not os.path.isfile(file):
            continue

        try:
            with open(file, 'r', encoding='utf-8') as f:
                text = f.read()

            redacted_text = redact_text(text, entities_to_redact, redaction_counts)

            if args.phones:
                redacted_text = redact_phones(redacted_text, redaction_counts)

            if args.address:
                redacted_text = redact_street_addresses(redacted_text, redaction_counts)

            if args.names:
                redacted_text = redact_emails(redacted_text, redaction_counts)

            if args.dates:
                redacted_text = redact_dates(redacted_text, redaction_counts)

            if args.concept:
                redacted_text = redact_concepts(redacted_text, args.concept, redaction_counts)

            # Saving redacted file in "files" directory with .censored extension
            output_file = os.path.join(output_dir, os.path.basename(file) + '.censored')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(redacted_text)
            print(f"Redacted file saved to {output_file}")

            # Output stats to terminal or individual stats file
            if args.stats in ['stdout', 'stderr']:
                print(f"\nStats for {file}:\n{generate_stats_output(redaction_counts)}")
            else:
                stats_file_path = os.path.join(output_dir, os.path.basename(file) + '.stats')
                write_stats_to_file(stats_file_path, redaction_counts)

        except OSError as e:
            print(f"Error opening file {file}: {e}")

def write_stats_to_file(stats_file, redaction_counts):
    """Write redaction statistics to a specified file."""
    with open(stats_file, 'w') as f:
        f.write("Redaction Statistics:\n")
        f.write(generate_stats_output(redaction_counts))
    print(f"Stats written to {stats_file}")

def generate_stats_output(redaction_counts):
    """Return a formatted stats output as a string."""
    return (
        f"Names: {redaction_counts['names']}\n"
        f"Dates: {redaction_counts['DATE']}\n"
        f"Phone Numbers: {redaction_counts['PHONE']}\n"
        f"Addresses: {redaction_counts['address']}\n"
        f"Concepts: {redaction_counts['CONCEPT']}\n"
    )

def main():
    args = parse_arguments()

    # Ensuring output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Processing input files and apply redactions
    process_files(args.input, args.output, args)

if __name__ == '__main__':
    main()
