import re
from wordfreq import zipf_frequency, top_n_list

# ====================
# 1. LANGUAGE SELECTION
# ====================

print("Select language / زبان را انتخاب کنید:")
print("1: English")
print("2: فارسی")

while True:
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        LANG = "en"
        break
    elif choice == "2":
        LANG = "fa"
        break
    else:
        print("Invalid input. Please enter 1 or 2.")

# ====================
# 2. DICTIONARY SETUP
# ====================

if LANG == "en":
    VOCAB_SIZE = 200_000
    DICTIONARY = set(top_n_list("en", n=VOCAB_SIZE))
    WORD_FREQ = {word: zipf_frequency(word, "en") for word in DICTIONARY}
elif LANG == "fa":
    VOCAB_SIZE = 200_000  
    DICTIONARY = set(top_n_list("fa", n=VOCAB_SIZE))
    WORD_FREQ = {word: zipf_frequency(word, "fa") for word in DICTIONARY}

# ==============================
# 3. KEYBOARD NEIGHBORS
# ==============================

if LANG == "en":
    KEYBOARD_NEIGHBORS = {
        'q': set("was"), 'w': set("qes"), 'e': set("wrsd"), 'r': set("etdf"),
        't': set("ryfgh"), 'y': set("tughj"), 'u': set("yihjk"),
        'i': set("uojkl"), 'o': set("ipkl"), 'p': set("ol"),
        'a': set("qwsz"), 's': set("weaxz"), 'd': set("ersfcx"),
        'f': set("rtdgvc"), 'g': set("tyfhbv"), 'h': set("yugbjn"),
        'j': set("uihkmn"), 'k': set("iojlm"), 'l': set("opk"),
        'z': set("asx"), 'x': set("zsdc"), 'c': set("xdfv"),
        'v': set("cfgb"), 'b': set("vghn"), 'n': set("bhnm"),
        'm': set("njk")
    }
elif LANG == "fa":
    KEYBOARD_NEIGHBORS = {
        'ض': set("صق"), 'ص': set("ضث"), 'ث': set("صق"), 'ق': set("فض"), 'ف': set("ققغ"), 'غ': set("فقع"), 
        'ع': set("غح"), 'ح': set("عهج"), 'ج': set("حچ"), 'چ': set("جحخ"), 'خ': set("چح"), 'س': set("شذ"), 
        'ش': set("سض"), 'ذ': set("شظ"), 'ط': set("ظ"), 'ظ': set("طز"), 'ز': set("ژر"), 'ر': set("زر"), 
        'ژ': set("ز"), 'د': set("ذ"), 'ئ': set("ی"), 'ی': set("ءئ"), 'ک': set("گ"), 'گ': set("ک"), 
        'ل': set("لا"), 'م': set("ن"), 'ن': set("م"), 'و': set("ؤ"), 'ؤ': set("و"), 'ه': set("ة"), 'ة': set("ه"),
        'ب': set("نم"), 'پ': set("چ"), 'ا': set("آ"), 'ت': set("ث"), 'ث': set("ت")
    }

# =============================
# 4. INPUT PREPROCESSING
# =============================

def preprocess_word(word: str) -> str:
    if word is None:
        return ""
    word = word.lower()
    if LANG == "en":
        return re.sub(r'[^a-z]', '', word)
    else:
        return re.sub(r'[^اآبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیءؤة]', '', word)

# ===================================
# 5. KEYBOARD‑AWARE DISTANCE FUNCTION
# ===================================

def keyboard_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    total_cost = 0
    len_a, len_b = len(a), len(b)
    max_len = max(len_a, len_b)
    for i in range(max_len):
        if i >= len_a or i >= len_b:
            total_cost += 2
        else:
            char_a, char_b = a[i], b[i]
            if char_a == char_b:
                continue
            neighbors = KEYBOARD_NEIGHBORS.get(char_a, set())
            if char_b in neighbors:
                total_cost += 1
            else:
                total_cost += 2
    total_cost += abs(len_a - len_b)
    return total_cost

# ========================================
# 6. SEARCH SPACE REDUCTION / CANDIDATES
# ========================================

def candidate_words(word: str, dictionary: set) -> list[str]:
    length = len(word)
    exact = [w for w in dictionary if len(w) == length]
    if exact:
        return exact
    return [w for w in dictionary if abs(len(w) - length) <= 2]

# ===============================
# 7. SPELL CORRECTION LOGIC
# ===============================

def correct_spelling(input_word: str) -> tuple[str, int]:
    word = preprocess_word(input_word)
    if not word:
        return "", -1
    candidates = candidate_words(word, DICTIONARY)
    scored = []
    for cand in candidates:
        dist = keyboard_distance(word, cand)
        scored.append((dist, -WORD_FREQ.get(cand, 0), cand))
    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    if not scored:
        return word, -1
    best_dist, _, best_word = scored[0]
    return best_word, best_dist

# ===========================
# 8. MAIN PROGRAM INTERFACE
# ===========================

def main():
    if LANG == "en":
        exit_msg = "Type 'exit' to quit."
    else:
        exit_msg = "برای خارج شدن، 'خروج' را تایپ کنید."

    print(f"=== Keyboard Proximity Spell Checker ({'English' if LANG=='en' else 'فارسی'}) ===")
    print(exit_msg)

    while True:
        user_input = input("Word: ").strip()
        if user_input.lower() == "exit" or user_input == "خروج":
            print("Exiting. Goodbye!" if LANG=="en" else "خروج. بدرود!")
            break

        suggestion, distance = correct_spelling(user_input)

        if not suggestion:
            print("Invalid input." if LANG=="en" else "ورودی نامعتبر است.")
            continue

        if distance == 0:
            print(f"'{user_input}' is correct!" if LANG=="en" else f"'{user_input}' درست است!")
        else:
            print(f"Suggested: {suggestion}" if LANG=="en" else f"پیشنهاد: {suggestion}")
            print(f"Distance: {distance}" if LANG=="en" else f"فاصله: {distance}")

        print("-" * 40)

if __name__ == "__main__":
    main()
