#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import cgi
import datetime
import simplejson
import wsgiref.handlers

#from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from appengine_utilities import sessions

import g
import admin
import utility
import login
import balance
from database import *

MAX_RECORD_PER_DAY = 100

def current_user():
  current_user = None
  session = sessions.Session(writer='cookie', session_expire_time=1209600)
  try:
    current_user = session['user_name']
  except KeyError:
    pass
  finally:
    return current_user


class MainPage(webapp.RequestHandler):
  def _query(self, date):
    query = LunchRecord.all()
    query.filter('date =', date)
    return  query.fetch(MAX_RECORD_PER_DAY)

  def _balance(self, user):
    query = User.all()
    query.filter('name =', user)

    user = query.fetch(1)
    if user:
      return user[0].balance
    else:
      return 0

  def get(self):
    user = current_user()
    if not user:
      self.redirect('/login')
      return

    user_balance = self._balance(user)
    today = datetime.date.today()

    last_10_day = []
    for i in range(10):
       last_10_day.append(self._query(today - datetime.timedelta(days=i)))
    
    ### get the balance situation
    balance_helper = balance.BalanceHelper()
    card_balance = balance_helper.getCardBalance()
    expected_balance = balance_helper.getExpectedCardBalance()
    lost = balance_helper.getLost()
    
    template_values = {
      'week': last_10_day,
      'user': user,
      'today': today,
      'balance' : user_balance,
      'card_balance' : card_balance,
      'expect_balance' : expected_balance,
      'balance_string' : balance_helper.getCardBalanceString(),
      'new_lost' : (expected_balance - lost - card_balance)
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class Cost(webapp.RequestHandler):
  def post(self):
    """have to check whether the same day and same user, there is some
      record already.
    """
    user_name = self.request.get('user_name')
    cost_rmb = float(self.request.get('cost_rmb'))
    date = datetime.date(int(self.request.get('date_year')), 
            int(self.request.get('date_month')), 
            int(self.request.get('date_day')))

    query = LunchRecord.all()
    query.filter('date = ', date)
    query.filter('user =', user_name)
    records = query.fetch(1)

    if not records:
      utility.update_balance(user_name, plus_value = 0, minus_value = cost_rmb)

      # TODO simplify it.
      lunchRecord = LunchRecord()
      lunchRecord.user = user_name
      lunchRecord.date = date
      lunchRecord.cost_rmb = cost_rmb
      lunchRecord.put()
    elif records[0].cost_rmb != cost_rmb:
      utility.update_balance(user_name, plus_value = records[0].cost_rmb, minus_value = cost_rmb)

      records[0].cost_rmb = cost_rmb
      records[0].put()

    self.redirect('/')

class Charge(webapp.RequestHandler):
  # TODO should merge to RobotCharge, use hiden form item
  def post(self):
    """
      have to check whether the same day and same user, there is some
      record already.
    """
    user = current_user()
    if not user:
      self.redirect('/login')
      return

    charge_rmb = float(self.request.get('charge_rmb'))

    query = ChargeRecord.all()
    query.filter('date = ', datetime.date.today())
    query.filter('user =', user)
    records = query.fetch(1)

    if not records:
      utility.update_balance(user, plus_value = charge_rmb, minus_value = 0)
      
      # TODO simplify it.
      chargeRecord = ChargeRecord()
      chargeRecord.user = user
      chargeRecord.charge_rmb = charge_rmb
      chargeRecord.put()
    elif records[0].charge_rmb != charge_rmb:
      utility.update_balance(user, plus_value = charge_rmb, minus_value = records[0].charge_rmb)

      records[0].charge_rmb = charge_rmb
      records[0].put()

    self.redirect('/')

class RobotCharge(webapp.RequestHandler):
  def post(self):
    user_name = self.request.get('user_name')
    date = datetime.date(int(self.request.get('date_year')), 
            int(self.request.get('date_month')), 
            int(self.request.get('date_day')))
    charge_rmb = float(self.request.get('charge_rmb'))
      
    query = ChargeRecord.all()
    query.filter('date =', date)
    query.filter('user =', user_name)
    records = query.fetch(1)

    if not records:
      utility.update_balance(user_name, plus_value = charge_rmb, minus_value = 0)

      # TODO simplify it.
      chargeRecord = ChargeRecord()
      chargeRecord.user = user_name
      chargeRecord.date = date
      chargeRecord.charge_rmb = charge_rmb
      chargeRecord.put()
    elif records[0].charge_rmb != charge_rmb:
      utility.update_balance(user_name, plus_value = charge_rmb, minus_value = records[0].charge_rmb)

      records[0].charge_rmb = charge_rmb
      records[0].put()
    #self.redirect('/')


class Who(webapp.RequestHandler):
    def get(self):
        data = {'users':utility.all_users()}
        data_js = simplejson.dumps(data)

        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.out.write(data_js)


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/cost', Cost),
  ('/login', login.Login),
  ('/signup', login.SignUp),
  ('/charge', Charge),
  ('/robotcharge', RobotCharge),
  ('/who', Who),
  ('/admin', admin.Admin),
  ('/card_balance', balance.CardBalance),
  ('/forget_it', balance.ForgetIt)
], debug=True)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
