import numpy as np
import spacy
import random

nlp = spacy.load("en_core_web_lg")

def get_synonyms(word):
    print("Synonyms for word: {}".format(word))
    words = [word + str(random.randrange(100000))]
    return words

if __name__=="__main__":
    your_word = "user_id"
    words = get_synonyms(your_word)
    print(words)