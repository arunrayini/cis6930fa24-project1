 #  cis6930fa24 -- Project 1
 
 Name: Arun Kumar Reddy Rayini

# Project Description:

 #  The Redactor
 "The Redactor" is a powerful tool created to anonymize sensitive data within text documents. Designed for applications that handle confidential information, this tool aims to ensure privacy by identifying and redacting personal and sensitive details. It is particularly suitable for sectors where data privacy is paramount, such as legal, healthcare, and government agencies. The tool recognizes and censors names, dates, phone numbers, addresses, and user-defined concepts by leveraging advanced natural language processing (NLP) capabilities through the spaCy and nltk libraries. These libraries allow for intelligent entity recognition and synonym expansion, which together enable flexible, context-aware redaction.

Using spaCy's robust Named Entity Recognition (NER) model, "The Redactor" can identify names, dates, and addresses in various formats, making it adaptable to diverse document types and structures. The tool also integrates nltk's WordNet to manage concepts through synonym expansion. This means that users can specify a theme or topic to redact, such as "confidentiality" or "privacy," and "The Redactor" will locate not only exact matches but also related terms, thereby redacting entire sentences where these concepts appear. This ensures a comprehensive approach to redaction, going beyond simple keyword-based methods.

Each identified sensitive term is replaced with a customizable block character to maintain document formatting while preventing exposure of the original information. The tool can handle multiple file types and supports bulk processing by taking advantage of flexible command-line arguments. Users can specify files through a glob pattern, control which types of sensitive information to censor, and even define where statistics about the redaction process will be output (e.g., to the terminal or a designated file).

In addition to its redaction capabilities, "The Redactor" provides detailed statistics on each redaction process. It generates a summary for each file, reporting counts of names, dates, phone numbers, addresses, and concepts that were censored. This data is helpful for verifying the tool’s effectiveness and ensuring compliance with privacy standards.

"The Redactor" is an efficient, customizable, and essential tool for automating the anonymization of documents, simplifying the redaction process while offering flexibility and precision for any organization handling sensitive information.

# Installation

Pipenv for virtual environment and dependency management: pip install pipenv

# Setup Instructions
1.Clone the repository and navigate into the project directory:
                      git clone <repository_url>
                      cd <project_directory>
2.Install dependencies using Pipenv:

                      pipenv install -e .
3.Download the spaCy language model:
                      pipenv run python -m spacy download en_core_web_sm

# Running the Program
General Syntax
The program can be executed using the following command-line format:

pipenv run python redactor.py --input '*.txt' \
                    --names --dates --phones --address\
                    --concept 'kids' \
                    --output 'files/' \
                    --stats stderr
commands used for the program specifically in order to execute:
1: pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'house' --concept 'wine'  --output 'files/' --stats 'stderr'
2: pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'house' --concept 'wine'  --output 'files/' --stats 'stdout'    
3: pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'house' --concept 'wine'  --output 'files/' --stats 'stats_file'

# Command-Line Arguments

--input: Takes a glob pattern to specify the input files (e.g., *.txt). This allows flexibility to choose specific files or groups.

--output: Specifies the directory where redacted files will be saved. Each file is saved with a .censored extension, ensuring the original file remains untouched.

--names: Redacts names, utilizing spaCy's PERSON entity. This includes names from sentences or even within email addresses.

--dates: Redacts dates of various formats, ensuring that dates, years, and times are all masked from the documents.

--phones: Redacts phone numbers, covering multiple formats commonly found in written text.

--address: Redacts structured addresses, including street names, city names, and state abbreviations to ensure geographic privacy.

--concept 'word' : Allows users to specify sensitive topics or themes for redaction. The tool uses nltk's WordNet to gather synonyms and related terms, ensuring sentences containing these words are fully redacted.

--stats: Outputs statistics about the redaction process, showing counts of each type of redaction. It can be set to stdout or stderr to display in the terminal or directed to a .stats file in the output directory.

 # Code Structure and Explanation
-- Argument Parsing (parse_arguments)
This function uses the argparse library to define the command-line arguments for the tool. It parses each argument based on the user’s input, making it flexible to choose different redaction flags, output paths, and stats output options.

-- Text Redaction (redact_text)
The redact_text function processes the text and identifies sensitive entity types (such as names and addresses) to be redacted. This function uses spaCy’s natural language processing capabilities:

--The function identifies names using spaCy’s PERSON entity and redacts them from the text.
Addresses: Address detection uses the ORG (organization) and GPE (geopolitical entity) entities from spaCy. This captures structured address patterns like cities, states, and some organization names that could reveal locations.

--Dates: If specified, dates are redacted using DATE entities from spaCy.
-- Email Redaction (redact_emails)
--This function redacts email addresses from the text using regular expressions. Email patterns are identified and masked, with each match counting as a redacted name. The function helps further anonymize personal identifiers within the document.

-- Address Redaction (redact_street_addresses)
Street addresses, city names, and state abbreviations are redacted here. This function is equipped with:

--Street Numbers: Detects and masks numbers that could be part of street addresses.
Street Names and Suffixes: Uses common street suffixes like Ave, St, and Blvd to catch various address patterns.

--State Abbreviations: A predefined list of U.S. state abbreviations is used to ensure full address redaction.
--Concept Redaction (redact_concepts)
The concept redaction function is a customizable feature allowing users to redact sentences containing certain words or phrases:

--WordNet Synonyms: Using nltk’s WordNet, synonyms and related terms of the specified concept are retrieved. 

--Sentence-Level Redaction: Any sentence containing a related term is fully redacted to ensure contextual privacy.

--Date Redaction (redact_dates)

Date patterns, such as day names, specific dates, and years, are redacted through regular expressions. This function recognizes various date formats, making it versatile in handling real-world text entries.

--Phone Number Redaction (redact_phones)
This function redacts phone numbers by identifying different phone number formats, such as (123) 456-7890 or 123.456.7890. It ensures that all phone number formats are consistently redacted to prevent exposure of contact information.

--File Processing (process_files)
This function is responsible for managing file inputs and applying the redaction functions to each file:

--File Parsing: Expands glob patterns to gather all specified input files.
Redaction Execution: For each file, it applies the chosen redaction flags, applies the text transformations, and saves the output to the specified directory with a .censored extension.
Statistics Collection: Redaction statistics are gathered for each file processed, enabling a report on the types and counts of redacted terms.
--Statistics Management (write_stats_to_file and generate_stats_output)

These functions manage the output of statistics:

Console or File Output: Depending on the --stats parameter, stats can be printed directly to stdout or stderr in the terminal, or saved as a .stats file in the output directory.

Content of Stats: Statistics include counts of names, dates, phone numbers, addresses, and concepts redacted, along with details for each redacted item, which can be useful for testing and verification.

--Main Execution (main)
The main function coordinates the entire process by:

Parsing command-line arguments.
Ensuring the output directory exists.
Calling the process_files function to handle redaction and output.
Managing statistics output based on user preferences.

# Test Suite

The project includes a series of test files that verify each major redaction feature. Tests can be run using:   pipenv run python -m pytest

# Provided Test Cases:
-- Address Redaction Test: Verifies the redaction of both street numbers and names to ensure address privacy.
-- Names Redaction Test: Checks that names are consistently redacted, including both first and last names in full names.
-- Date Redaction Test: Confirms the correct identification and redaction of various date formats.
-- Phone Redaction Test: Ensures different phone number formats are redacted, verifying the tool’s flexibility.
-- Concept Redaction Test: Tests that sentences containing user-specified concepts are fully redacted, including synonyms or related terms as defined.

# Stats Output

The --stats flag generates a summary of the redaction process:

executable command for example: pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'house' --concept 'wine'  --output 'files/' --stats 'stdout'    
stdout: Prints statistics to the terminal.

 executable command for example:pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'house' --concept 'wine'  --output 'files/' --stats 'stats_file'
File Output: When a file path is specified, it generates a .stats file in the output directory with details on each redaction

Statistics include counts of each type of redaction, enabling detailed tracking and verification of the redaction process.

# Assumptions and Known Limitations

Assumptions
Concept Synonyms: For concept redaction, all related terms in the WordNet synset are relevant for redaction.
Character Masking: A full-block Unicode character (█) is used for redaction, preserving the layout without revealing the text.
Date Formats: The date redaction only covers common formats and may miss ambiguous date representations.

Limitations

Non-U.S. Address Formats: The tool’s address redaction is focused on U.S. formats and may not work effectively for international addresses.

Multi-word Names: Complex names (e.g., names with titles) may not always redact correctly due to limitations in NER.




