# refactored-octo-spoon
My chess stuff


/* Copyright (C) 2015 Jon Stephan - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Jon Stephan <jfstepha@gmail.com>, 2015

 */

Install python chess
- https://pypi.python.org/pypi/python-chess
- pip install python-chess

Install python mysql
- sudo apt-get install python-mysqldb

Set up mysql

- sudo apt-get install mysql-server
- mysql -u root -p
- create user 'chess'@'localhost' identified by 'chess_pwd';
- create database testdb
- create database whfchess
- grant all on testdb.* to 'chess'@'localhost';
- grant all on whfchess.* to 'chess'@'localhost';
