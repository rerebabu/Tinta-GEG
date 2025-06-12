import random

# Function words and affixes commonly used in Filipino grammar errors
function_words = ['ng', 'nang', 'ay', 'na', 'pa', 'ang', 'si']
affixes = ['nag', 'mag', 'um', 'in', 'ka', 'pa', 'ma']

# Substitution based on Filipino affixes
def substitute_affix_based(word):
    word_lc = word.lower()
    for affix in affixes:
        if word_lc.startswith(affix):
            root = word[len(affix):]
            options = [
                root,                  # Drop affix
                root + root,           # Reduplication
                'na' + root,           # Wrong prefix
                affix + root + 'an'    # Overextended
            ]
            return random.choice(options)
    return random.choice(function_words)  # Fallback

# Main function to apply random operations
def apply_artificial_errors(tokens, prob=0.5):
    output = []
    i = 0

    while i < len(tokens):
        current = tokens[i]
        operation = None

        # Decide randomly whether to perform an operation
        if random.random() < prob:
            operation = random.choice(['insert', 'delete', 'substitute', 'swap'])
            print(f"Applying {operation} on token: '{current}'")

        if operation == 'insert':
            rand_token = random.choice(function_words)
            output.append(rand_token)
            output.append(current)

        elif operation == 'delete':
            # Skip the current token
            print(f"Deleted token: '{current}'")

        elif operation == 'substitute':
            new_token = substitute_affix_based(current)
            output.append(new_token)
            print(f"Substituted '{current}' → '{new_token}'")

        elif operation == 'swap' and i + 1 < len(tokens):
            next_token = tokens[i + 1]
            output.append(next_token)
            output.append(current)
            print(f"Swapped '{current}' ↔ '{next_token}'")
            i += 1  # Skip the next token after swap

        else:
            # No operation or invalid swap — keep original
            output.append(current)

        i += 1

    return output

# Example usage
if __name__ == "__main__":
    original = ['Naglakad', 'siya', 'sa', 'parke', 'kahapon', '.']
    print("\nOriginal: ", ' '.join(original))

    noisy = apply_artificial_errors(original, prob=0.6)
    print("With Errors:", ' '.join(noisy))
