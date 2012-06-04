#!/usr/bin/env python
# -*- coding: GB2312 -*-
# Last modified: 

"""It seems to me that there should be three class to do some thing, 
    the page (handler), the model and the datebase 
"""

__revision__ = '0.1'
import datetime

from google.appengine.ext import webapp

from database import *


class CardBalance(webapp.RequestHandler):
  def post(self):
    user_name = self.request.get('user_name')
    balance = float(self.request.get('card_balance'))

    query = CardBalanceRecord.all()
    query.filter('date =', datetime.date.today())
    records = query.fetch(1)

    if not records:
      CardBalanceRecord(submitor = user_name, balance = balance).put()
      #cardBalanceRecord.submitor = user_name
      #cardBalanceRecord.balance = balance 
      #cardBalanceRecord.put()
    elif records[0].balance != balance:
      records[0].balance = balance 
      records[0].put()
 
    self.redirect('/')

class ForgetIt(webapp.RequestHandler):
  def post(self):
    balance_helper = BalanceHelper()
    balance_helper.lostIt()

    self.redirect('/')

class BalanceHelper():
  """BalanceMonitor is going to answer three questions:
      1. actual balance in card
      2. balance expected
      3. new lost and lost already happend.
     and BalanceMonitor is going to help convert new lost to old one.
  """
  def __init__(self):
    self.date = datetime.date.today()
    self.submitor = 'Nobody'
    self.card_balance = 0.0

  def _updateCardBalance(self):
    query = CardBalanceRecord.all()
    query.order('-date')
    latest_balance = query.fetch(1)

    if latest_balance:
      self.date = latest_balance[0].date
      self.submitor = latest_balance[0].submitor
      self.card_balance = latest_balance[0].balance

  def getCardBalance(self):
    self._updateCardBalance()
    return self.card_balance
 
  def getCardBalanceString(self):
    self._updateCardBalance()
    return str(self.card_balance) + ', submitted by ' + self.submitor +\
        ' at ' + str(self.date.month) + '/' + str(self.date.day)

  def getExpectedCardBalance(self):
    #query = User.all()
    expected_balance = 0.0
    for user in User.all():
      expected_balance += user.balance  
    return expected_balance

  def getLost(self):
    query = GlobalVariableRecord.all()
    g = query.fetch(1)
    if g:
      return g[0].lost
    else:
      GlobalVariableRecord(lost = 0.0).put()
      return 0.0

  def lostIt(self):
    """Update old_lost value to current
    """
    query = GlobalVariableRecord.all()
    g = query.fetch(1)
    if g:
      g[0].lost = self.getExpectedCardBalance() - self.getCardBalance()
      g[0].put()
    else:
      g = GlobalVariableRecord()
      g.lost = self.getExpectedCardBalance() - self.getCardBalance()
      g.put()

