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
from pyspark.sql import SQLContext
from pyspark.sql.types import *

try:
    import json
except ImportError:
    import simplejson as json

def PrepareServerForInput(trash):
    print("Prepare")
    #requests.post("http:/localhost:8080/SetFlag", data={"val":True})

def SendInput(jsonData):   
    print("Sent")
    #requests.post("http:/localhost:8080/SendData", data="{'text':'%s','sentiment':%s}" % (jsonData[0], jsonData[1]), headers={'content-type': 'application/json'})

def TellServerDone(trash):
    print("Done")
    #requests.post("http:/localhost:8080/SetFlag", data={"val":false})

def VerifyNotDelete(tweet):
    if 'delete' not in tweet:
       return tweet

def VerifyNotUnicode(word):
    if not isinstance(word, unicode):
        return word

def VerifyTrumpWord(tweet):
    if tweet['text'] is not None:
        for word in ['TRUMP', 'MAGA', 'DICTATOR', 'IMPEACH', 'SWAMP', 'DRAIN', 'CHANGE']:
            if word in tweet['text'].upper():
                return tweet

def sanitize(tweetText):
    text = re.sub(r'[^\x00-\x7F]+',' ', tweetText)
    #print("Sanitized Text: %s" % text)
    return text
    # encodedText = ("%s" % tweetText).encode("utf-8")
    # return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", encodedText).split())

def get_sentiment(tweet):
    analysis = TextBlob(tweet)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def sentiment(tweet):

    return get_sentiment(tweet)

if __name__ == "__main__":

    # json = json.load(open("tweets.json"))
    # for tweet in json:
    #     analysedTweet = sentiment(tweet['text'])
    #     print(("Text: %s" % analysedTweet['text']).encode("utf-8"))
    #     print("Sentiment: %s" % analysedTweet['sentiment'])
    #     print("\n")

    spark = SparkSession \
    .builder \
    .appName("Sentiment Anaylis") \
    .getOrCreate()
    #sc = SparkContext(appName="Sentiment Anaylis")

    #data = consumer.map(lambda tweets: json.loads(tweets[1])) 
    data = spark.read.json("tweets.json")
    filteredTweets = data.rdd.filter(VerifyNotDelete).filter(VerifyNotUnicode).filter(VerifyTrumpWord).map(lambda tweet: sentiment(sanitize(("%s" % tweet['text']).encode("utf-8"))))
    fields = [StructField(field_name, StringType(), True) for field_name in "sentiment"]
    schema = StructType(fields)
    df = spark.createDataFrame(filteredTweets, schema)
    df = spark.createDataFrame(filteredTweets, new StructType(new StructField("sentiment", StringType, nullable=false)))
    df.groupBy('sentiment').count().show()


    sentimentCount = filteredTweets.countByValueAndWindow(86400,3600)
    hack = sentimentCount.countByValueAndWindow(86400, 3600).transform(lambda rdd: spark.parallelize(rdd.take(0)))
    hack.foreachRDD(PrepareServerForInput)
    hack.pprint()
    sentimentCount.foreachRDD(lambda row: row.foreach(SendInput))
    sentimentCount.pprint()
    hack.foreachRDD(TellServerDone)
    hack.pprint()

