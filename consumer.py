#from pathlib import Path

# Import Spark packages
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import requests
import json
import urllib
from textblob import TextBlob
import re

try:
    import json
except ImportError:
    import simplejson as json

def PrepareServerForInput(trash):
    requests.post("http:/localhost:8080/SetFlag", data={"val":True})

def SendInput(jsonData):   
    requests.post("http:/localhost:8080/SendData", data="{'text':'%s','sentiment':%s}" % (jsonData[0], jsonData[1]), headers={'content-type': 'application/json'})

def VerifyNotDelete(tweet):
    if 'delete' not in tweet:
       return tweet

def VerifyNotUnicode(word):
    if not isinstance(word, unicode):
        return word

def VerifyTrumpWord(tweet):
    for word in ['TRUMP', 'MAGA', 'DICTATOR', 'IMPEACH', 'SWAMP', 'DRAIN', 'CHANGE']:
        if word in tweet['text'].upper():
            return tweet

def sanitize(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_sentiment(tweet):
    anaylis = TextBlob(sanitize(tweet))
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def sentiment(tweet):
    analysed_tweet = {}
    analysed_tweet['text'] = tweet
    analysed_tweet['sentiment'] = get_sentiment(tweet)
    return analysed_tweet

if __name__ == "__main__":
    sc = SparkContext(appName="Sentiment Anaylis")

    # Create a local StreamingContext with two working thread and batch interval of 10 minutes
    ssc = StreamingContext(sc, 1)

    sc.setCheckpointDir("/tmp/checkpoints/")

    consumer = KafkaUtils.createStream(ssc,"localhost:2181","twitter-streaming",{'tweets':1})

    data = consumer.map(lambda tweets: json.loads(tweets[1])) 

    analysedTweets = data.filter(VerifyNotDelete).filter(VerifyNotUnicode).flatMap(lambda tweet: sentiment(tweet['text']))

    # Trump Words
    trumpWordTweets = analysedTweets.filter(VerifyTrumpWord).countByValueAndWindow(2,1).transform(lambda rdd: rdd.sortBy(lambda row: row[1]['sentiment'],ascending=False))
    hack = trumpWordTweets.countByValueAndWindow(2,1).transform(lambda rdd:sc.parallelize(rdd.take(0)))
    hack.foreachRDD(PrepareServerForInput)
    hack.pprint()
    trumpWordsCounted.foreachRDD(lambda row: row.foreach(SendInput))
    trumpWordsCounted.pprint()
    
    ssc.start()             # Start the computation
    ssc.awaitTermination()