#!/usr/bin/env python
# -*- coding: GB2312 -*-
# Last modified: 

"""docstring
"""

__revision__ = '0.1'

import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from appengine_utilities import sessions

import utility
from database import *

hidden_users = ['Bai Jingping', 'Ben Fu', 'Chen Xi', 'Deng Xuegang', 'Dou Jianming', 'Lin Ruhan', 'Wang Lili','Zhou Yi', 'Zhou Jian', 'Jia Xiangdong', 'Yu Ye', 'Zhang Jizheng']

class Login(webapp.RequestHandler):
  def get(self):
    show_users = []

    for user in utility.all_users():
      if user not in hidden_users:
        show_users.append(user)  

    show_users.sort()

    template_values = {
      'users': show_users
      }

    path = os.path.join(os.path.dirname(__file__), 'login.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    session = sessions.Session(writer='cookie')
    try:
      session['user_name'] = self.request.get('user') 
    except:
      pass
    finally:
      self.redirect('/')


class SignUp(webapp.RequestHandler):
  def post(self):
    for user in utility.all_users():
      if user == self.request.get('user_name'):
        self.redirect('/login')
        return

    if self.request.get('user_name'):
      new_user = User()
      new_user.name = self.request.get('user_name')
      new_user.put()

    self.redirect('/login')
