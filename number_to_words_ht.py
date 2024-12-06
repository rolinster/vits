single_digits = {
    0: "zero", 1: "en", 2: "de", 3: "twa", 4: "kat", 5: "senk",
    6: "sis", 7: "sèt", 8: "uit", 9: "nèf"
}

teens = {
    10: "dis", 11: "onz", 12: "douz", 13: "trèz", 14: "katòz",
    15: "kenz", 16: "sèz", 17: "disèt", 18: "dizuit", 19: "diznèf"
}

tens = {
    20: "ven", 30: "trant", 40: "karant", 50: "senkant",
    60: "swasant", 70: "swasant-dis", 80: "katreven", 90: "katreven-dis"
}

thousands = {
    1000: "mil", 1000000: "milyon", 1000000000: "milya", 1000000000000: "bilion"
}

def number_to_words_ht(number):
    if number < 10:
        return single_digits[number]
    elif 10 <= number < 20:
        return teens[number]
    elif 20 <= number < 100:
        ten, remainder = divmod(number, 10)
        ten_word = tens[ten * 10]
        if remainder:
            return f"{ten_word}-{single_digits[remainder]}"
        else:
            return ten_word
    elif 100 <= number < 1000:
        hundred, remainder = divmod(number, 100)
#        print(f"hundred: {hundred}, remainder: {remainder}")
        hundred_word = f"{single_digits[hundred]} san" if hundred > 1 else "san"
        if remainder:
            return f"{hundred_word} {number_to_words_ht(remainder)}"
        else:
            return hundred_word
    else:
        # Handle thousands and above
        for key in sorted(thousands.keys(), reverse=True):
            if number >= key:
                major, remainder = divmod(number, key)
                if major == 1:
                    major_word = thousands[key]
                else:
                    major_word = f"{number_to_words_ht(major)} {thousands[key]}"
                if remainder:
                    return f"{major_word} {number_to_words_ht(remainder)}"
                else:
                    return major_word

#print(number_to_words_ht(123))  # Expected: "san ven-twa"
#print(number_to_words_ht(1001))  # Expected: "mil en"
#print(number_to_words_ht(2023))  # Expected: "de mil ven-twa"