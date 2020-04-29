import nltk
sentence = """At eight o'clock on Thursday morning
... Arthur didn't feel very good."""
tokens = nltk.word_tokenize(sentence)
tagged = nltk.pos_tag(tokens)
print(tagged[0:6])



def download_binaries():
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
