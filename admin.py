#!/usr/bin/env python
# -*- coding: GB2312 -*-
# Last modified: 

"""admin is used to get each user's balance and total balance.
"""

__revision__ = '0.1'

from google.appengine.ext import webapp
from database import *
import utility

class Admin(webapp.RequestHandler):
    def get(self):
        # first caculate each user's balance
        # then update them in schema 'User'
        for user in User.all():
            user.balance = utility.balance(user.name)
            user.put()

        self.response.out.write("""
        <html>
	      <head>
		    <title>Admin Page</title>
	      </head>
	      <body>""")

        total_balance = 0
        for user in User.all():
            self.response.out.write(user.name + ' : ' + str(user.balance) + "<br>")
            total_balance += user.balance

        self.response.out.write("------------------<br>")
        self.response.out.write("card expect : " + str(total_balance))
        
        self.response.out.write("""
	      </body>
        </html>""")

