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
    "ligature": 62.64,
    "enclitic": 21.67,
    "hyphenation": 6.37,
    "ng_nang": 4.66,
    "morphological": 3.04,
    "repetition": 1.62,
}

# -----------------------------
# Substitution Handlers
# -----------------------------
def apply_ligature_confusion(output, sub_indices):
    print("Checking for error type: ligature") # for tracking

    # Randomly choose a valid, untampered token
    target_tokens = ['na', 'ng']
    matching_indices = [
        i for i, value in enumerate(output) 
        if value.lower() in target_tokens and i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

    # Substitution logic: replace 'na' with 'ng' and vice versa
    if output[rand_index] == 'na':
        output[rand_index] = 'ng'
    elif output[rand_index] == 'ng':
        output[rand_index] = 'na'

    print(output[rand_index]) # for tracking
    sub_indices.append(rand_index)
    return True

def apply_enclitic_confusion(output, sub_indices):
    print("Checking for error type: enclitic") # for tracking

    # Randomly choose a valid, untampered token
    target_tokens = ['din', 'rin', 'daw', 'raw', 'doon', 'roon']
    matching_indices = [
        i for i, value in enumerate(output) 
        if value.lower() in target_tokens and i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

    # Substitution logic: replace the first letter /d/ to /r/ and vice versa
    if output[rand_index][0] == 'd':
        output[rand_index] = 'r' + output[rand_index][1:]    
    elif output[rand_index] == 'r':
        output[rand_index] = 'd' + output[rand_index][1:]

    print(output[rand_index]) # for tracking
    sub_indices.append(rand_index)
    return True

def apply_hyphenation_error(output, sub_indices):
    print("Checking for error type: hyphenation") # for tracking

    # Randomly choose a valid, untampered token
    matching_indices = [
        i for i, value in enumerate(output) 
        if '-' in value and i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

        # Substitution logic: remove the hyphen
        output[rand_index] = output[rand_index].replace('-', '')

        print(output[rand_index]) # for tracking
        sub_indices.append(rand_index)
        return True

def apply_ng_nang_confusion(output, sub_indices):
    print("Checking for error type: ng_nang") # for tracking

    # Randomly choose a valid, untampered token
    target_tokens = ['ng', 'nang']
    matching_indices = [
        i for i, value in enumerate(output) 
        if value.lower() in target_tokens and i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

    # Substitution logic: replace 'ng' with 'nang' and vice versa
    if output[rand_index] == 'ng':
        output[rand_index] = 'nang'
    elif output[rand_index] == 'nang':
        output[rand_index] = 'ng'

    print(output[rand_index]) # for tracking
    sub_indices.append(rand_index)
    return True

def apply_morphological_error(output, sub_indices):
    print("Checking for error type: morphological") # for tracking

    # Randomly choose a valid, untampered token
    target_subtokens = ['pang', 'pam', 'pan']
    matching_indices = [
        i for i, value in enumerate(output) 
        if value.lower().startswith(tuple(target_subtokens)) and i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

    # Substitution logic: replace the prefix with another random one
    for token in target_subtokens:
        if output[rand_index].startswith(token):
            alternatives = [t for t in target_subtokens if t != token]
            if alternatives:
                replacement = random.choice(alternatives)
                output[rand_index] = replacement + output[rand_index][len(token):]
                break
            else: return False

    print(output[rand_index]) # for tracking
    sub_indices.append(rand_index)
    return True

def apply_repetition(output, sub_indices):
    print("Checking for error type: repetition") # for tracking

    # Randomly choose an untampered token
    matching_indices = [
        i for i, value in enumerate(output) 
        if i not in sub_indices
    ]

    if not matching_indices:
        print("No valid token found.") # for tracking 
        return False
    else: 
        rand_index = random.choice(matching_indices)
        print(f"Substituted '{output[rand_index]}' →") # for tracking

        # Substitution logic: insert a duplication of the token
        output.insert(rand_index, output[rand_index])

        print(output[rand_index] + output[rand_index]) # for tracking

        # Keep track of indices shift
        sub_indices = [i + 1 if i >= rand_index else i for i in sub_indices]
        sub_indices.append(rand_index)

        return True

error_function_map = {
    "ligature": apply_ligature_confusion,
    "enclitic": apply_enclitic_confusion,
    "hyphenation": apply_hyphenation_error,
    "ng_nang": apply_ng_nang_confusion,
    "morphological": apply_morphological_error,
    "repetition": apply_repetition,
}

# -----------------------------
# GEG Logic
# -----------------------------
def apply_artificial_errors(tokens, max_errors = 2):
    output = tokens.copy()
    error_count = random.randint(1, max_errors)
    operation = ['insert', 'delete', 'substitute', 'swap']
    performed_operation = [] # Keep a list of operations already performed
    generated_error_type = []
    sub_indices = [] # Keep a list of tokens already replaced

    while error_count > 0:
        filtered_operation = [
            value for value, value in enumerate(operation)
            if value not in performed_operation
        ]

        rand_operation = random.choice(filtered_operation)

        # Insert operation
        if rand_operation == 'insert':
            # Insert a random token at a random non-empty index
            rand_token = random.choice(function_words)
            rand_index = random.randint(0, len(output) - 1)
            output.insert(rand_index, rand_token)

            sub_indices = [i + 1 if i > rand_index else i for i in sub_indices] # Keep track of indices shift

            print(f"Inserted '{rand_token}' before '{output[rand_index + 1]}'") # for tracking

        # Delete operation
        elif rand_operation == 'delete':
            rand_index = random.randint(0, len(output) - 1) # Choose a random index

            print(f"Deleted '{output[rand_index]}'") # for tracking

            del output[rand_index]

            sub_indices = [i - 1 if i > rand_index else i for i in sub_indices if i != rand_index] # Keep track of indices shift

        # Substitution operation
        elif rand_operation == 'substitute': 
            checked_error_types = []; # Keep a list of error types already tried
            
            # Choose a random weighted error type for substitution
            while True:
                filter_error_type = [
                    (k, substitution_errors[k])
                    for k in substitution_errors
                    if k not in checked_error_types
                ]

                if filter_error_type: 
                    population, weights = zip(*filter_error_type)
                    error_type = random.choices(
                        population=population, 
                        weights=weights, 
                        k=1
                    )[0]
                else:
                    print("No valid substitution operation can be performed.") # for tracking
                    break

                # Repeat choosing of error type until a valid one is performed
                substituted = error_function_map[error_type](output, sub_indices)

                if substituted:
                    generated_error_type.append(error_type) 
                    break
                else: checked_error_types.append(error_type)
        
        # Swap operation
        elif rand_operation == 'swap':
            while True:
                rand_index = random.randint(0, len(output) - 2)
                if output[rand_index] != output[rand_index + 1]:
                    break

            print(f"Swapped '{output[rand_index]}' ↔ '{output[rand_index + 1]}'")

            output[rand_index], output[rand_index + 1] = output[rand_index + 1], output[rand_index]

            # Keep track of index swapping
            new_sub_indices = []
            for i in sub_indices:
                if i == rand_index:
                    new_sub_indices.append(i + 1)
                elif i == rand_index + 1:
                    new_sub_indices.append(i - 1)
                else:
                    new_sub_indices.append(i)
            sub_indices = new_sub_indices

        error_count -= 1 # Decrement remaining error count to apply
        performed_operation.append(rand_operation)

    return output, performed_operation, generated_error_type

def tokenize(text):
    # Splits words and keeps punctuation as separate tokens
    return re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text, re.UNICODE)

def detokenize(tokens):
    text = ' '.join(tokens)
    # Remove space before punctuation
    text = re.sub(r'\s+([?.!",;:])', r'\1', text)
    return text

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
        writer.writerow(["incorrect", "correct", "errors"])

        for tokens in sentence_list:
            correct = detokenize(tokens)
            print(f"Original Sentence: {correct}\n")
            incorrect_tokens, performed_operation, generated_error_type = apply_artificial_errors(tokens, max_errors = 2)
            incorrect = detokenize(incorrect_tokens)
            error_info = f"operations: {', '.join(performed_operation)}; errors: {', '.join(generated_error_type)}"
            print(f"\nGenerated Erroneous Sentence: {incorrect}")
            print("-----------------------------")
            writer.writerow([incorrect, correct, error_info])

    print("✅ 'error_data.csv' successfully generated.")