/*
 * Name: server.js
 * Rev1
 * Date: 05/05/2018
 * @author Brian Hickey, x17126622
 *References: The core of this js file is taken from class work( IoT softwaredev NCIRL) but usage of different aspects were found in the following:
 *http://www.sqlitetutorial.net/sqlite-nodejs/query/
 *https://stackoverflow.com/questions/37991995/passing-a-variable-from-node-js-to-html?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
 *https://nodejs.org/en/docs/guides/anatomy-of-an-http-transaction/
 *http://www.sqlitetutorial.net/sqlite-max/
 *https://www.sqlite.org/autoinc.html  ---use of rowid to find the correct row was extremely useful for this project.
 *
 */


var http = require('http');                                     // get http module
var fs = require("fs");                                         // get file system
const sqlite3 = require('sqlite3').verbose();                   // get sqlite3 module

let db = new sqlite3.Database('\TankLevel.db', (err) => {       // connect to Tanklevel database
  if (err) {                                                    // if something goes wrong, display the error
    console.error(err.message);
  }
  console.log('Connected to the TankLevel database.');          // if ok, display 'connected'
});

let current =  'SELECT Level FROM level ORDER BY rowid DESC LIMIT 1'    // set the query to the database to get the tank
                                                                        // level of the last enry
db.get(current, function(err, result, fields){                          // if error throw error
  if (err) throw err;
  currlevel = result.Level                                              // set current level to equal retrieved level value
});

let levelMinus24 = 'SELECT Level FROM level WHERE rowid = (SELECT Rowid FROM level ORDER BY rowid DESC LIMIT 1)-96'
                                                                        // get the level 24 hours ago which is current level
                                                                        // minus 96 enties or rows. 96 in 24 hours
db.get(levelMinus24, function(err, result, fields){                     // get the level
  if (err) throw err;
  level24hours = result.Level                                           // set the level 24hrs ago to equal retrieved value
});

let levelMinus7 = 'SELECT Level FROM level WHERE rowid = (SELECT Rowid FROM level ORDER BY rowid DESC LIMIT 1)-672'
                                                                        // get the level 7 days ago. This is current level
                                                                        // minus 96*7 which is 672
db.get(levelMinus7, function(err, result, fields){                      // get the level 7 days ago and throw error if error
  if (err) throw err;
  level7days = result.Level
});

    http.createServer(function(request, res) {                          // create the server and activate if request from client
        res.writeHeader(200, {"Content-Type": "text/html"});            // set up html...
        res.write('<html>');
        res.write('<head>');
        res.write('<title>Oil Level Monitor</title>')                   // title on tab of browser
        res.write('</head>')
        res.write('<body Style="background-color:grey;">');
        res.write('<h1 style="color:red;font-size:28;text-align:center;">Oil Tank Monitor</h1>'); // text with 'style' included
        res.write('<h1 style="color:black;font-size:20;">The current level in the tank is:</h1>') // start of test to display values
        res.write('<h1 style="color:blue;font-size:20;">'+currlevel+' Litres</h1>');              // retrieved from database
        res.write('<h1 style="color:black;font-size:20;">In the last 24 Hours we used:</h1>')
        res.write('<h1 style="color:blue;font-size:20;">'+(level24hours-currlevel)+' Litres, to heat the house</h1>');
        res.write('<h1 style="color:blue;font-size:20;">This cost: '+((level24hours-currlevel)*0.60)+' Euro @ 60c per Litre </h1>')
        res.write('<h1 style="color:black;font-size:20;">In the last week we used:</h1>')
        res.write('<h1 style="color:blue;font-size:20;">'+(level7days-currlevel)+' Litres, to heat the house</h1>');
        res.write('<h1 style="color:blue;font-size:20;">This cost: '+((level7days-currlevel)*0.60)+' Euro @ 60c per Litre </h1>')
        res.write('</body>');
        res.write('</html>');
        res.end();
    }).listen(8080); // listen on port 8080 for clients. When client 'calls' display results of queries to database of oil usage.
