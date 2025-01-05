import sys
import string

import nltk
import pycountry

# pip install setuptools
import rowordnet
from rowordnet import Synset
import random
from langdetect import detect
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize

# pip install stanza spacy-stanza
import stanza
import spacy_stanza

stanza.download("ro")
nlp = spacy_stanza.load_pipeline("ro", processors="tokenize,pos,lemma")
rown = rowordnet.RoWordNet()

nltk.download("punkt_tab")


def is_word(word: str):
    return any(c.isalpha() for c in word)


# extract text
if len(sys.argv) < 2:
    # example data, any english text will do
    text = open("assets/nlp/Klaus Iohannis_texts.txt", encoding="utf8").read()
else:
    text = sys.argv[1]

nlp.max_length = len(text)

# detect lang
lang = detect(text)
lang_name = pycountry.languages.get(alpha_2=lang)

print(lang, lang_name)

# extract stylometric information
words = word_tokenize(text)
words_without_punctuation = [word for word in words if is_word(word)]
sentences = sent_tokenize(text)

# 1. Lexical Features

# Vocabulary richness: Metrics like type-token ratio (TTR), which is the ratio of unique words (types) to total words (tokens).
ttr = len(set(words_without_punctuation)) / len(words_without_punctuation)
print(f"{ttr=}")

# Word frequencies: Commonly used words or distinctive patterns in word usage.
freq_dist = FreqDist(words_without_punctuation)
print(f"top 5 most common words: {freq_dist.most_common(5)}")

# Word length: Average word length or distribution of word lengths.
avg_word_length = sum(len(word) for word in words_without_punctuation) / len(words_without_punctuation)
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


def str_to_synset_pos(pos_str: str):
    synset_pos_map = {
        "NOUN": Synset.Pos.NOUN,
        "VERB": Synset.Pos.VERB,
        "ADV": Synset.Pos.ADVERB,
        "ADJ": Synset.Pos.ADJECTIVE,
    }
    if pos_str in synset_pos_map:
        return synset_pos_map[pos_str]
    return None


# Lesk algorithm, used to find the word meaning in WordNet
# most similar to the sentence/paragraph given;
# might come in handy for determining the "sense" of keywords in sentences.
# normally Lesk is used on a single sentence but I feel like it might be more
# helpful to use it on a whole paragraph;
# we sort words in the paragraph by their frequency,
# we lesk the first few,
# and that's how we get their meanings -- through their wordnet definitions.
def lesk(sentence, word, pos=None, wn=rown):
    context = set(x for x in sentence.split() if x != "")
    synsets = wn.synsets(word, pos=pos if pos else None)
    if not synsets:
        return None
    _, sense = max((len(context.intersection(wn.synset(ss).definition.split())), ss) for ss in synsets)
    return sense


tagged_words = nlp(text)
replaced_words: list[str] = []


def append_word_with_space(arr, word, pos=None):
    if pos != "PUNCT" and len(arr) > 0 and word[0] != "-" and arr[-1][-1] != "-":
        replaced_words.append(" ")
    replaced_words.append(word)


for index, token in enumerate(tagged_words):
    synsets = rown.synsets(token.lemma_, pos=str_to_synset_pos(token.pos_), strict=True)
    if not synsets:
        append_word_with_space(replaced_words, token.text, token.pos_)
        continue

    synonyms = [
        literal for ss in synsets for literal in rown.synset(ss).literals if literal.strip() != token.text.strip()
    ]

    outbound_relations = [x for ss in synsets for x in rown.outbound_relations(ss)]
    hypernym_synsets = [ss for ss, relation in outbound_relations if relation == "hypernym"]
    antonym_synsets = [ss for ss, relation in outbound_relations if relation in {"antonym", "near_antonym"}]
    hypernyms = [literal for ss in hypernym_synsets for literal in rown.synset(ss).literals]
    not_antonyms = ["nu " + literal for ss in antonym_synsets for literal in rown.synset(ss).literals]

    possible_words = [*synonyms, *hypernyms, *not_antonyms]
    if not possible_words or random.randint(0, 4) != 0:
        append_word_with_space(replaced_words, token.text, token.pos_)
        continue

    final_word = (
        possible_words[random.randint(0, len(possible_words) - 1) if len(possible_words) > 1 else 0]
        .replace("_", " ")
        .replace("[", "")
        .replace("]", "")
        .replace("|", "")
    )
    append_word_with_space(replaced_words, final_word, token.pos_)


replaced_words_result = "".join(replaced_words)
print(replaced_words_result)
