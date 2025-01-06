import sys
import string
import re

import nltk
import pycountry

import rowordnet
from rowordnet import Synset
import random
from langdetect import detect
from nltk.probability import FreqDist
from nltk.tokenize import sent_tokenize, word_tokenize

import spacy
from spacy.cli import download
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# initialize models
download("ro_core_news_sm")
nlp = spacy.load("ro_core_news_sm")
rown = rowordnet.RoWordNet()
nltk.download("punkt_tab")

tokenizer = AutoTokenizer.from_pretrained("dumitrescustefan/gpt-neo-romanian-780m")
model = AutoModelForCausalLM.from_pretrained("dumitrescustefan/gpt-neo-romanian-780m")
model.generation_config.pad_token_id = model.generation_config.eos_token_id

seed = random.randint(0, 2**32 - 1)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)


def is_word(word: str):
    return any(c.isalpha() for c in word)


# extract text
if len(sys.argv) < 2:
    text = open("assets/nlp/Klaus Iohannis_texts.txt", encoding="utf8").read()
else:
    text = sys.argv[1]
text = text.strip()

nlp.max_length = len(text)

print("\n\n\nStylometric characteristics:\n")

# detect lang
lang = detect(text)
lang_name = pycountry.languages.get(alpha_2=lang)

print(lang, lang_name)

# extract stylometric information
words = word_tokenize(text)
words_without_punctuation = [word for word in words if is_word(word)]
sentences = sent_tokenize(text)

# lexical features
# type-token ratio (TTR) = unique words / total words.
ttr = len(set(words_without_punctuation)) / len(words_without_punctuation)
print(f"{ttr=}")

# most common words
freq_dist = FreqDist(words_without_punctuation)
print(f"top 5 most common words: {freq_dist.most_common(5)}")

# avg word length
avg_word_length = sum(len(word) for word in words_without_punctuation) / len(words_without_punctuation)
print(f"{avg_word_length=}")

# hapax legomena: count of words that occur only once in the text.
hapax_legomena = [word for word, count in freq_dist.items() if count == 1]
print(f"hapax_legomena={hapax_legomena[:5]}")

# hapax dislegomena: count of words that occur exactly twice.
hapax_dislegomena = [word for word, count in freq_dist.items() if count == 2]
print(f"hapax_dislegomena={hapax_dislegomena[:5]}")

# syntactic features
# avg sentence length
avg_sentence_length = sum(len(word_tokenize(sent)) for sent in sentences) / len(sentences)
print(f"{avg_sentence_length=}")

# count of punctuations
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
# used for determining the "sense" of keywords in sentences
def lesk(sentence: list[str], word: str, pos=None, wn=rown):
    context = set(x for x in sentence if x != "")
    synsets = wn.synsets(word, pos=pos if pos else None)
    if not synsets:
        return None
    _, sense = max((len(context.intersection(wn.synset(ss).definition.split())), ss) for ss in synsets)
    return sense


doc = nlp(text)
replaced_words: list[str] = []


def append_word_with_space(arr, word, pos=None):
    if pos != "PUNCT" and len(arr) > 0 and word[0] != "-" and arr[-1][-1] != "-":
        replaced_words.append(" ")
    replaced_words.append(word)


for token in doc:
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
print("\n\n\nText with words replaced:\n")
print(replaced_words_result)

# get the first paragraph
paragraph = text.split("\n")[0]
paragraph_doc = nlp(paragraph)
named_entities = paragraph_doc.ents
paragraph_words = [x.text for x in paragraph_doc]

keywords_with_meanings = {}

for entity in named_entities:
    synset = lesk(paragraph_words, entity.lemma_)
    keywords_with_meanings[entity.text] = rown.synset(synset).definition if synset else None

print(f"\n\n\nKeywords in first paragraph: {', '.join(keywords_with_meanings.keys())}")

# generate sentences
for keyword, meaning in keywords_with_meanings.items():
    prompt = f'O propoziție conținând cuvântul "{keyword}"'
    if meaning is not None:
        prompt += f', cuvânt care are definiția "{meaning}"'
    prompt += ", este:"
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    text = model.generate(inputs, max_new_tokens=256, no_repeat_ngram_size=2)

    print(f'\n\nSentence with keyword "{keyword}":')
    generated_text = tokenizer.decode(text[0])[len(prompt) :].strip()
    sentence_match = re.match(r'(\"([^"]+)\")|([^.?!]*[.?!])', generated_text)
    if sentence_match:
        sentence = sentence_match.group(0).strip('"')
        if sentence[-1] not in {".", "?", "!"}:
            sentence += "."
        print(sentence)
    else:
        print(generated_text)
