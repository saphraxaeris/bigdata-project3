var express = require('express');
var bodyParser = require('body-parser');
var fs = require('fs');

var flag = false;
var data = [];

var app = express();
app.use(bodyParser.json());

app.use(express.static('assets'));
app.use(express.static('styles'));
app.use(express.static('scripts'));
app.use(express.static('data'));

app.get('/',function(req, res){
  //res.send(data);
  res.sendFile('index.html',{root:"./views"});
});

app.post('/SetFlag', function(req, res){
  var flagValue = req.body.val;
  if(flag === false && flagValue === true) {
    flag = true;
    res.send(true);
  }
  else if(flag === true && flagValue === false) {
    flag = false;
    //Save data to file
    var textToWrite = "var data = " + JSON.stringify(data) + ";";
    fs.writeFile("data/data.js", textToWrite, function(err) {
      if(err) {
          return console.log(err);
      }
    });
    //Clear data
    data = [];
    res.send(true);
  }
  else {
    res.send(true);
  }
});

app.post('/SendData', function(req, res){
  if(flag === true) {
    var tweet = req.body;
    if(tweet) {
      data.push(tweet);
      res.send(true);
    }
  }
  res.send(true);
});

app.listen(8080);