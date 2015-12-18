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
- sudo apt-get install python-mysql

Set up mysql

- mysql -u root -p
- create user 'chess'@'localhost' identified by 'chess_pwd';
- grant all on whfchess.* to 'chess'@'localhost';
