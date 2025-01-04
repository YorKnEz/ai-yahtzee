import string
import sys

import nltk
import pycountry
from langdetect import detect
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize

nltk.download("punkt_tab")

# extract text
if len(sys.argv) < 2:
    # example data, any english text will do
    text = open("/home/yorknez/Downloads/data/federalist_4.txt").read()
else:
    text = sys.argv[1]

# detect lang
lang = detect(text)
lang_name = pycountry.languages.get(alpha_2=lang)

print(lang, lang_name)

# extract stylometric information
words = word_tokenize(text)
sentences = sent_tokenize(text)

# 1. Lexical Features

# Vocabulary richness: Metrics like type-token ratio (TTR), which is the ratio of unique words (types) to total words (tokens).
ttr = len(set(words)) / len(words)
print(f"{ttr=}")

# Word frequencies: Commonly used words or distinctive patterns in word usage.
freq_dist = FreqDist(words)
print(f"top 5 most common words: {freq_dist.most_common(5)}")

# Word length: Average word length or distribution of word lengths.
avg_word_length = sum(len(word) for word in words) / len(words)
print(f"{avg_word_length=}")

# Hapax legomena: Count of words that occur only once in the text.
hapax_legomena = [word for word, count in freq_dist.items() if count == 1]
print(f"hapax_legomena={hapax_legomena[:5]}")

# Hapax dislegomena: Count of words that occur exactly twice.
hapax_dislegomena = [word for word, count in freq_dist.items() if count == 2]
print(f"hapax_dislegomena={hapax_dislegomena[:5]}")

# 2. Syntactic Features

# Sentence length: Average sentence length and variability.
avg_sentence_length = sum(len(word_tokenize(sent)) for sent in sentences) / len(sentences)
print(f"{avg_sentence_length=}")

# Punctuation usage: Frequency and types of punctuation marks.
punctuation_count = sum(1 for char in text if char in string.punctuation)
print(f"{punctuation_count=}")
