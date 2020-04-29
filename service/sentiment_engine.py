import nltk

from nltk.sentiment.vader import SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')



class SentimentEngine(object):

    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()



    def get_scores_headline(self, headline):
        scores = self.sia.polarity_scores(headline)

        return scores['compound']


#
# for name, passage in headlines:
#     scores = sia.polarity_scores(passage)
#     print (name, scores)
