import numpy as np
import spacy
import random

nlp = spacy.load("en_core_web_lg")

def get_synonyms(word):
    try:
        print("Synonyms for word: {}".format(word))
        ms = nlp.vocab.vectors.most_similar(
        np.asarray([nlp.vocab.vectors[nlp.vocab.strings[word]]]), n=10)
        words = [nlp.vocab.strings[w] for w in ms[0][0]]
        distances = ms[2]
    except KeyError:
        print("Unable to find synonym for {}. Returning as is".format(word))
        words = [word + str(random.randrange(10))]
    return words

if __name__=="__main__":
    your_word = "user_id"
    words = get_synonyms(your_word)
    print(words)