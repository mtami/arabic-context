import datetime
from typing import Dict, Tuple

import spacy
import streamlit as st

from utils import clean_str, load_words

start_date = datetime.date(2023, 2, 1)


class Preprocessor:
    def __init__(self, tokenizer, **cfg):
        self.tokenizer = tokenizer

    def __call__(self, text):
        preprocessed = clean_str(text)
        return self.tokenizer(preprocessed)


@st.experimental_singleton
def load_model():
    model = spacy.load("./spacyModel/")
    model.tokenizer = Preprocessor(model.tokenizer)
    return model


@st.experimental_memo
def build_nlp_words():
    model = load_model()
    nlp_words = [model(word) for word in load_words()]
    return nlp_words


def scale_val(val, max_val=1, scale=1000):
    return val / abs(max_val) * scale


nlp = load_model()
nlp_words = build_nlp_words()


def calculate_distance(day: int, word: str) -> tuple[bool, dict]:
    today = datetime.date.today()
    word_index = (today - start_date).days
    if day not in range(0, word_index + 1):
        return False, {"detail": "Bad day!"}

    if word not in nlp.vocab.strings:
        return False, {"detail": "I'm sorry, I don't know this word"}

    similarity = nlp_words[day].similarity(nlp(word))
    distance = 1 - similarity
    scaled_distance = scale_val(distance)

    return True, {"word": word, "distance": int(scaled_distance)}
