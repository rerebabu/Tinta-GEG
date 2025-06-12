import random
import csv

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
def apply_artificial_errors(tokens, prob=0.6):
    output = []
    i = 0

    while i < len(tokens):
        current = tokens[i]
        operation = None

        if random.random() < prob:
            operation = random.choice(['insert', 'delete', 'substitute', 'swap'])

        if operation == 'insert':
            output.append(random.choice(function_words))
            output.append(current)

        elif operation == 'delete':
            pass  # skip

        elif operation == 'substitute':
            error_type = random.choices(
                population=list(substitution_errors.keys()),
                weights=list(substitution_errors.values()),
                k=1
            )[0]
            substituted = error_function_map[error_type](current)
            if substituted:
                output.append(substituted)

        elif operation == 'swap' and i + 1 < len(tokens):
            output.append(tokens[i + 1])
            output.append(current)
            i += 1

        else:
            output.append(current)

        i += 1

    return output

# -----------------------------
# Load clean sentences
# -----------------------------
def load_sentences_from_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        return [line.strip().split() for line in f if line.strip()]

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
            incorrect_tokens = apply_artificial_errors(tokens, prob=0.6)
            incorrect = ' '.join(incorrect_tokens)
            writer.writerow([incorrect, correct])

    print("✅ 'error_data.csv' successfully generated.")
