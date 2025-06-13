import random
import csv
import re

# -----------------------------
# Reference tokens and affixes
# -----------------------------
function_words = ['ng', 'nang', 'ay', 'na', 'pa', 'ang', 'si']
affixes = ['nag', 'mag', 'um', 'in', 'ka', 'pa', 'ma']

# -----------------------------
# Substitution Error Frequencies
# -----------------------------
substitution_errors = {
    "ng_nang": 0.25,
    "verb_affix": 0.20,
    "reduplication": 0.15,
    "enclitic_shift": 0.10,
    "determiner_confusion": 0.10,
    "copula_drop": 0.10,
    "spacing_error": 0.10
}

# -----------------------------
# Substitution Handlers
# -----------------------------
def apply_ng_nang_confusion(word):
    return "nang" if word == "ng" else "ng" if word == "nang" else word

def apply_verb_affix_error(word):
    for affix in affixes:
        if word.lower().startswith(affix):
            root = word[len(affix):]
            options = [
                root,
                affix + root + 'an',
                affix + root[::-1]
            ]
            return random.choice(options)
    return word

def apply_reduplication(word):
    return word + word

def apply_enclitic_shift(word):
    return '' if word in ['na', 'pa', 'din', 'rin'] else word

def apply_determiner_confusion(word):
    return "si" if word == "ang" else "ang" if word == "si" else word

def apply_copula_drop(word):
    return '' if word == "ay" else word

def apply_spacing_error(word):
    return word + random.choice(["siya", "ito", "kami", "na"])

error_function_map = {
    "ng_nang": apply_ng_nang_confusion,
    "verb_affix": apply_verb_affix_error,
    "reduplication": apply_reduplication,
    "enclitic_shift": apply_enclitic_shift,
    "determiner_confusion": apply_determiner_confusion,
    "copula_drop": apply_copula_drop,
    "spacing_error": apply_spacing_error
}

# -----------------------------
# GEG Logic
# -----------------------------
def apply_artificial_errors(tokens, max_errors = 2):
    output = tokens.copy()

    # Randomly choose at most two token indices to introduce an error to
    indices_to_modify = sorted(random.sample(range(len(tokens)), k = min(max_errors, len(tokens)))) 

    for i in indices_to_modify:
        current = output[i]
        operation = random.choice(['insert', 'delete', 'substitute', 'swap'])

        # Insert operation
        if operation == 'insert':
            rand_token = random.choice(function_words)
            output.insert(i, rand_token) # Insert a random token at i
            print(f"Inserted '{rand_token}' before '{current}'")

        # Delete operation
        elif operation == 'delete':
            output[i] = ''  # Mark for deletion
            print(f"Deleted '{current}'")

        # Substitute operation
        elif operation == 'substitute':
            error_type = random.choices(
                population=list(substitution_errors.keys()),
                weights=list(substitution_errors.values()),
                k=1
            )[0]
            substituted = error_function_map[error_type](current)
            if substituted:
                output[i] = substituted
            print(f"Substituted '{current}' → '{substituted}' | Error type: {error_type}")

        # Swap operation
        elif operation == 'swap' and i < len(tokens) - 1:
            output[i], output[i + 1] = output[i + 1], output[i]
            print(f"Swapped '{current}' ↔ '{output[i]}'")

    # Remove empty strings from 'delete'
    return [token for token in output if token != '']

def tokenize(text):
    # Splits words and keeps punctuation as separate tokens
    return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

# -----------------------------
# Load clean sentences
# -----------------------------
def load_sentences_from_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        return [tokenize(line.strip()) for line in f if line.strip()]

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    # 1. Load input
    sentence_list = load_sentences_from_file("sentences.txt")

    # 2. Write to CSV
    with open("error_data.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["incorrect", "correct"])

        for tokens in sentence_list:
            correct = ' '.join(tokens)
            print(f"Original Sentence: {correct}\n")
            incorrect_tokens = apply_artificial_errors(tokens, max_errors = 2)
            incorrect = ' '.join(incorrect_tokens)
            print(f"\nGenerated Erroneous Sentence: {incorrect}")
            print("-----------------------------")
            writer.writerow([incorrect, correct])

    print("✅ 'error_data.csv' successfully generated.")