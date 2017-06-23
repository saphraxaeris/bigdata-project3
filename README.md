# Prerequisites
## Python
* pip intsall twitter
* pip intsall textblob
* pip intsall requests
* pip intsall kafka
## NodeJS
## NPM
## Spark
## Kafka

# Running the code
* cd to project folder
* Run `npm install` and `npm start` to start the server
* Run `python producer.py` to start loading tweets into kafka
* Run `<location of spark>/bin/spark-submit consumer.py` to start analysing tweets from kafka
* Go to `localhost:8080` to view the data