import random
import csv
import re
import pandas as pd
from collections import Counter

# -----------------------------
# Reference tokens
# -----------------------------
# Words for the new, realistic insertion function
filler_words = ['at', 'mga', 'nga', 'naman', 'po', 'ulit']
# Small, common function words prone to stuttering/repetition
repeatable_words = ['ang', 'ng', 'sa', 'na', 'ay']
# Words for the legacy 'insert' operation (now just a fallback)
function_words = ['ng', 'nang', 'ay', 'na', 'pa', 'ang', 'si', 'sa', 'mga', 'ito', 'niya']


# -----------------------------
# Substitution Handlers (With New Insertion Logic)
# -----------------------------

def apply_insertion_error(output, sub_indices):
    """
    A more realistic insertion function. It either repeats a common function
    word (stutter) or adds a common filler word between tokens.
    """
    action = random.choice(['repeat', 'filler'])

    # Action 1: Repeat an existing common word (e.g., "ang ang bata")
    if action == 'repeat':
        eligible_indices = [i for i, token in enumerate(output)
                            if token.lower() in repeatable_words and i not in sub_indices]
        if not eligible_indices: return False # Can't repeat if no repeatable words found

        rand_index = random.choice(eligible_indices)
        output.insert(rand_index + 1, output[rand_index]) # Insert duplicate after the original
        # Update indices and mark both as involved
        sub_indices[:] = [idx + 1 if idx > rand_index else idx for idx in sub_indices]
        sub_indices.extend([rand_index, rand_index + 1])
        return True

    # Action 2: Add a filler word between two existing words
    elif action == 'filler':
        # Find a valid spot between two tokens to insert a word
        if len(output) < 2: return False
        rand_index = random.randint(1, len(output) - 1)
        rand_word = random.choice(filler_words)
        output.insert(rand_index, rand_word)
        # Update indices and mark the new word
        sub_indices[:] = [idx + 1 if idx >= rand_index else idx for idx in sub_indices]
        sub_indices.append(rand_index)
        return True

    return False

def apply_ligature_confusion(output, sub_indices):
    """Simulates ligature error: split token ending in '-ng' or '-g' into token + 'na'."""

    exclude_tokens = {
        "ng", "nang", "lang", "lamang", "habang", "kung",
        "bilang", "kabilang", "maging", "naging", "ang"
    }

    truncate_g_tokens = {
        "gayong", "gayunmang", "ganyang", "ganong", "ganung",
        "aling", "saang", "kailang", "ilang", "anumang", "sinomang",
        "alinmang", "aking", "aming", "ating"
    }

    matching_indices = [
        i for i, value in enumerate(output)
        if ((value.lower().endswith("ng") and value.lower() not in exclude_tokens)
            or value.lower() in truncate_g_tokens)
        and i not in sub_indices
    ]

    if not matching_indices:
        return False

    rand_index = random.choice(matching_indices)
    token = output[rand_index]

    if token.lower() in truncate_g_tokens:
        stripped = token[:-1]  # strip "-g"
    else:
        stripped = token[:-2]  # strip "-ng"

    output[rand_index] = stripped
    output.insert(rand_index + 1, "na")

    # Adjust sub_indices in-place
    for idx in range(len(sub_indices)):
        if sub_indices[idx] > rand_index:
            sub_indices[idx] += 1

    sub_indices.append(rand_index)      # Mark modified token
    sub_indices.append(rand_index + 1)  # Mark inserted "na"

    return True

def apply_morphological_error(output, sub_indices):
    """Simulates confusion between related morphophonemic prefixes."""
    morph_confusions = {'pam': ['pan', 'pang'], 'pan': ['pam', 'pang'], 'pang': ['pam', 'pan'],
                        'man': ['mam', 'mang'], 'mam': ['man', 'mang'], 'mang': ['man', 'mam'],
                        'mag': ['nag', 'pag'], 'nag': ['mag', 'pag'], 'pag': ['mag', 'nag']}
    matching_indices, original_prefixes = [], {}
    for i, token in enumerate(output):
        if i not in sub_indices:
            for prefix in morph_confusions.keys():
                if token.lower().startswith(prefix):
                    matching_indices.append(i)
                    original_prefixes[i] = prefix
                    break
    if not matching_indices: return False
    rand_index = random.choice(matching_indices)
    original_token = output[rand_index]
    found_prefix = original_prefixes[rand_index]
    replacement_prefix = random.choice(morph_confusions[found_prefix])
    new_token = replacement_prefix + original_token[len(found_prefix):]
    if original_token.istitle(): new_token = new_token.capitalize()
    output[rand_index] = new_token
    sub_indices.append(rand_index)
    return True

def apply_ng_nang_confusion(output, sub_indices):
    """Swaps 'ng' and 'nang'."""
    matching_indices = [i for i, value in enumerate(output)
                        if value.lower() in ['ng', 'nang'] and i not in sub_indices]
    if not matching_indices: return False
    rand_index = random.choice(matching_indices)
    original_token = output[rand_index]
    if original_token.lower() == 'ng':
        output[rand_index] = 'nang' if original_token.islower() else 'Nang'
    else:
        output[rand_index] = 'ng' if original_token.islower() else 'Ng'
    sub_indices.append(rand_index)
    return True

def apply_missing_space(output, sub_indices):
    """Simulates missing spaces by merging tokens"""

    # Randomly choose an untampered token
    matching_indices = [
        i for i, value in enumerate(output)
        if i not in sub_indices
    ]

    if len(matching_indices) < 2:  # Need at least 2 tokens to merge
        return False

    rand_index = random.choice(matching_indices)

    # Decide randomly: merge with previous or next token
    merge_with_prev = random.choice([True, False])

    if merge_with_prev and rand_index > 0:
        merge_index = rand_index - 1
        output[merge_index] = output[merge_index] + output[rand_index]
        del output[rand_index]

        # Adjust indices due to deletion
        sub_indices = [i - 1 if i > rand_index else i for i in sub_indices]
        sub_indices.append(merge_index)

    elif not merge_with_prev and rand_index < len(output) - 1:
        merge_index = rand_index
        output[merge_index] = output[merge_index] + output[merge_index + 1]
        del output[merge_index + 1]

        # Adjust indices due to deletion
        sub_indices = [i - 1 if i > merge_index + 1 else i for i in sub_indices]
        sub_indices.append(merge_index)

    else:
        # If merge not possible in chosen direction (e.g., first token, no prev),
        # retry by merging with the available neighbor
        if rand_index > 0:
            merge_index = rand_index - 1
            output[merge_index] = output[merge_index] + output[rand_index]
            del output[rand_index]
            sub_indices = [i - 1 if i > rand_index else i for i in sub_indices]
            sub_indices.append(merge_index)
        elif rand_index < len(output) - 1:
            merge_index = rand_index
            output[merge_index] = output[merge_index] + output[merge_index + 1]
            del output[merge_index + 1]
            sub_indices = [i - 1 if i > merge_index + 1 else i for i in sub_indices]
            sub_indices.append(merge_index)
        else:
            return False  # Single-token case — cannot merge

    return True

def apply_extra_space(output, sub_indices):
    """Simulates extra spaces by splitting a random token"""

    # Randomly choose an untampered token
    matching_indices = [
        i for i in range(len(output))
        if i not in sub_indices and len(output[i]) > 1  # must be splittable
    ]

    if not matching_indices:
        return False

    rand_index = random.choice(matching_indices)
    token = output[rand_index]

    # Pick a random split point (not at start or end, to avoid empty token)
    split_pos = random.randint(1, len(token) - 1)
    first_half = token[:split_pos]
    second_half = token[split_pos:]

    # Replace token with first half, then insert second half right after
    output[rand_index] = first_half
    output.insert(rand_index + 1, second_half)

    # Adjust indices due to insertion (shift any later sub_indices)
    sub_indices = [i + 1 if i > rand_index else i for i in sub_indices]
    sub_indices.append(rand_index)       # mark first half as modified
    sub_indices.append(rand_index + 1)   # mark second half as modified

    return True

def apply_enclitic_confusion(output, sub_indices):
    """Simulates the common d/r interchange rule error."""
    target_pairs = {'din': 'rin', 'daw': 'raw', 'doon': 'roon', 'diyan': 'riyan'}
    reverse_pairs = {v: k for k, v in target_pairs.items()}
    all_targets = list(target_pairs.keys()) + list(reverse_pairs.keys())
    matching_indices = [i for i, value in enumerate(output)
                        if value.lower() in all_targets and i not in sub_indices]
    if not matching_indices: return False
    rand_index = random.choice(matching_indices)
    original_token = output[rand_index]
    if original_token.lower() in target_pairs:
        replacement = target_pairs[original_token.lower()]
    else:
        replacement = reverse_pairs[original_token.lower()]
    output[rand_index] = replacement if original_token.islower() else replacement.capitalize()
    sub_indices.append(rand_index)
    return True

def apply_incorrect_syllable_reduplication(output, sub_indices):
    """
    Simulates incorrect reduplication placement.
    E.g. kagigising (correct) → kakagising (error)
    by moving reduplication to the previous syllable.
    Skips words starting with common Filipino prefixes
    """

    target_prefixes = ( "ka", "ika" )

    matching_indices = [
        i for i, value in enumerate(output)
        if (
            i not in sub_indices
            and value.lower().startswith(target_prefixes)
            and re.search(r"([bcdfghjklmnpqrstvwxyz][aeiou])\1", value, re.IGNORECASE)
        )
    ]

    if not matching_indices:
        return False

    rand_index = random.choice(matching_indices)
    token = output[rand_index]

    # Match CV reduplication inside the token (e.g., gi-gi)
    m = re.match(r"^(.+?)([bcdfghjklmnpqrstvwxyz])([aeiou])\2\3(.+)$", token, re.IGNORECASE)
    if not m:
        return False

    prefix, consonant, vowel, rest = m.groups()

    # Match first CV of the prefix (e.g., ka- from kagigising)
    first_cv_match = re.match(r"^([bcdfghjklmnpqrstvwxyz])([aeiou])(.+)$", prefix, re.IGNORECASE)
    if not first_cv_match:
        return False

    first_consonant, first_vowel, remaining_prefix = first_cv_match.groups()

    # Construct erroneous token: move reduplication earlier
    erroneous_token = (
        first_consonant + first_vowel + first_consonant + first_vowel +
        remaining_prefix + consonant + vowel + rest
    )

    output[rand_index] = erroneous_token
    sub_indices.append(rand_index)
    return True


def apply_morphological_punctuation_error(output, sub_indices):
    """Simulates omission of hyphen or apostrophe"""

    target_tokens = ['-', "'"]

    # Randomly choose a valid, untampered token
    matching_indices = [
        i for i, value in enumerate(output)
        if value in target_tokens and i not in sub_indices
    ]

    if not matching_indices:
        return False
    else:
        rand_index = random.choice(matching_indices)

        # Substitution logic: remove hyphen or apostrophe
        output[rand_index] = output[rand_index].replace('-', '').replace("'", '')
        sub_indices.append(rand_index)
        return True

def apply_sentence_level_punc_error(output, sub_indices):
    """Simulates sentence-level punctuation error by repeating punctuation marks.
    - Periods won't be repeated exactly 3 times (to avoid forming an ellipsis).
    - Existing ellipses (...) will be replaced with a different number of periods.
    """

    target_punc = ['.', ',', '?', '!', '"', '...']
    matching_indices = [
        i for i, value in enumerate(output)
        if value in target_punc and i not in sub_indices
    ]

    if not matching_indices:
        return False

    rand_index = random.choice(matching_indices)
    token = output[rand_index]

    # Determine repetition count
    if token == '.':
        repeat_count = random.choice([2, 4])  # avoid 3 to prevent ellipsis
        output[rand_index] = '.' * repeat_count

    elif token == '...':
        # Replace with a different number of periods (not 3)
        repeat_count = random.choice([1, 2, 4])
        output[rand_index] = '.' * repeat_count

    else:
        # Other punctuation can repeat freely (2–5 times)
        repeat_count = random.randint(2, 4)
        output[rand_index] = token * repeat_count

    sub_indices.append(rand_index)
    return True

# -----------------------------
# Error Map (Now includes the new insertion error type)
# -----------------------------
error_function_map = {
    "insertion": apply_insertion_error,
    "ligature": apply_ligature_confusion,
    "morphological": apply_morphological_error,
    "ng_nang": apply_ng_nang_confusion,
    "missing_space": apply_missing_space,
    "extra_space": apply_extra_space,
    "enclitic": apply_enclitic_confusion,
    "incorrect_syllable_reduplication": apply_incorrect_syllable_reduplication,
    "morphological_punctuation": apply_morphological_punctuation_error,
    "sentence_level_punctuation": apply_sentence_level_punc_error,
}

def havePunctuation(token): # holding for marks in swapping
  return bool(re.fullmatch(r'[.,!?;:]', token))

# Typo-style functions (not in the map, called directly as basic operations)
def perform_deletion(output):
    if len(output) <= 1: return False
    rand_index = random.randrange(len(output))
    del output[rand_index]
    return True

def perform_swap(output):
    if len(output) <= 1: return False

    validIndex = []
    restrictedWords = {'ng', 'nang'}

    for i in range(len(output) - 1):
        tokA = output[i].lower()
        tokB = output[i + 1].lower()

        haveRestrictedWord = tokA in restrictedWords or tokB in restrictedWords
        bothPunct = havePunctuation(output[i]) and havePunctuation(output[i + 1])

        createsCluster = (
            havePunctuation(output[i]) and (i > 0 and havePunctuation(output[i - 1]))
        ) or (
            havePunctuation(output[i + 1]) and (i + 2 < len(output) and havePunctuation(output[i + 2]))
        )

        if not haveRestrictedWord and not bothPunct and not createsCluster:
            validIndex.append(i)

    if not validIndex: return False

    rand_index = random.choice(validIndex)
    output[rand_index], output[rand_index + 1] = output[rand_index + 1], output[rand_index]
    return True


# -----------------------------
# GEG LOGIC (MODIFIED FOR ONE ERROR and new insertion)
# -----------------------------
def apply_one_artificial_error(tokens):
    """
    Tries to apply exactly one operation to the token list.
    Prioritizes enclitic confusion if the sentence contains target enclitics.
    Then tries other substitution-style errors, then deletion/swapping.
    """
    output = list(tokens)

    # --- Priority Step: Check for enclitic candidates ---
    enclitic_targets = ['din', 'rin', 'daw', 'raw', 'doon', 'roon', 'diyan', 'riyan']
    contains_enclitic = any(token.lower() in enclitic_targets for token in output)

    if contains_enclitic:
        temp_output = list(output)
        if apply_enclitic_confusion(temp_output, []):
            return temp_output, ['substitute'], ['enclitic']

    # --- If no enclitic error applied, proceed with other operations ---
    operations_to_try = ['substitute', 'delete', 'swap']
    random.shuffle(operations_to_try)

    for operation in operations_to_try:
        if operation == 'substitute':
            error_types_to_try = list(error_function_map.keys())
            random.shuffle(error_types_to_try)
            for error_type in error_types_to_try:
                # Skip enclitic confusion here since it was already prioritized above
                if error_type == "enclitic":
                    continue
                temp_output = list(output)
                if error_function_map[error_type](temp_output, []):
                    return temp_output, ['substitute'], [error_type]

        elif operation == 'delete':
            temp_output = list(output)
            if perform_deletion(temp_output):
                return temp_output, ['delete'], []

        elif operation == 'swap':
            temp_output = list(output)
            if perform_swap(temp_output):
                return temp_output, ['swap'], []

    return tokens, [], []  # Return original if no error could be applied

def tokenize(text):
    """Tokenizer that splits words, punctuation, and common Filipino clitics."""
    tokens = re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text, re.UNICODE)
    processed_tokens = []
    for token in tokens:
        match = re.match(r"(\w+)(['’])([yt]|ng)$", token, re.UNICODE)
        if match:
            processed_tokens.extend([match.group(1), match.group(2) + match.group(3)])
        else:
            processed_tokens.append(token)
    return processed_tokens

def detokenize(tokens):
    """Joins tokens back into a string with correct spacing."""
    if not tokens: return ""
    text = ""
    no_space_after = False
    for i, token in enumerate(tokens):
        if i == 0 or token in ".,?!:;" or token.startswith("'") or token.startswith("’") or no_space_after:
            text += token
        else:
            text += " " + token
        no_space_after = token in "([{"
    return re.sub(r'\s+', ' ', text).strip()

def normalize_punctuation(text):
    text = re.sub(r'([!?.,]){2,}', lambda m: m.group(0)[0], text) # avoid duplicates marks
    return text

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    try:
        print("Attempting to load cleaned dataset from local folder...")

        # If the CSV is in the same folder, just use its filename
        file_path = "cleanedTintaDataset.csv"
        df = pd.read_csv(file_path)

        # Extract text column
        sentence_sources = [text for text in df["Correct"] if isinstance(text, str) and text.strip()]

        print(f"✅ Loaded {len(sentence_sources)} cleaned sentences from CSV.")
    except Exception as e:
        print(f"⚠️  Could not load dataset from Hub. Reason: {e}")
        print("--> Using built-in sample sentences as a fallback.")
        sentence_sources = ["Fallback EncountereD"]

    tokenized_sentences = [tokenize(text) for text in sentence_sources]

    error_summary = Counter()
    operation_summary = Counter()

    with open("error_data.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["correct", "incorrect", "operation", "error_type"])
        for tokens in tokenized_sentences:
            if len(tokens) < 3: continue

            correct = normalize_punctuation(detokenize(tokens))
            incorrect_tokens, performed_ops, generated_errors = apply_one_artificial_error(tokens)
            incorrect = normalize_punctuation(detokenize(incorrect_tokens))

            if incorrect != correct:
                op = performed_ops[0] if performed_ops else "none"
                err = generated_errors[0] if generated_errors else "none"
                writer.writerow([correct, incorrect, op, err])
                if generated_errors:
                    error_summary.update(generated_errors)
                operation_summary.update(performed_ops)

    print("\n✅ 'error_data.csv' successfully generated.")

    # --- Summary Writing ---
    summary_file = "error_distribution.csv"
    total_errors = sum(error_summary.values())
    error_label_map = {
        "insertion": "Realistic Insertion (Stutter/Filler)",
        "ligature": "Ligature Confusion (-ng/-g vs. na)",
        "morphological": "Morphological Prefix Confusion",
        "ng_nang": "Grammatical Confusion (ng vs. nang)",
        "missing_space": "Missing Space",
        "extra_space": "Extra Space",
        "enclitic": "Enclitic D/R Confusion (din vs. rin)",
        "incorrect_syllable_reduplication": "Incorrect Syllable Reduplication",
        "morphological_punctuation": "Hyphen/Apostrophe Error",
        "sentence_level_punctuation": "Sentence-Level Punctuation Error",

    }
    with open(summary_file, "w", newline='', encoding="utf-8") as summary_csv:
        writer = csv.writer(summary_csv)
        writer.writerow(["Category of Errors", "Frequency", "Percentage"])
        if total_errors > 0:
            for error, freq in sorted(error_summary.items()):
                label = error_label_map.get(error, error)
                percent = (freq / total_errors) * 100
                writer.writerow([label, freq, f"{percent:.1f}%"])
            writer.writerow(["Total Substitution Errors", total_errors, "100%"])
    print(f"📁 '{summary_file}' successfully generated.")

    operation_file = "operation_distribution.csv"
    total_operations = sum(operation_summary.values())
    with open(operation_file, "w", newline='', encoding="utf-8") as op_csv:
        writer = csv.writer(op_csv)
        writer.writerow(["Type of Operation", "Frequency", "Percentage"])
        if total_operations > 0:
            for operation, freq in sorted(operation_summary.items()):
                percent = (freq / total_operations) * 100
                writer.writerow([operation.capitalize(), freq, f"{percent:.1f}%"])
            writer.writerow(["Total Operations", total_operations, "100%"])
    print(f"📁 '{operation_file}' successfully generated.")