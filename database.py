#!/usr/bin/env python
# -*- coding: GB2312 -*-
# Last modified: 

"""docstring
"""

__revision__ = '0.1'

from google.appengine.ext import db


class LunchRecord(db.Model):
  user = db.StringProperty()
  date = db.DateProperty(auto_now_add=False)
  cost_rmb = db.FloatProperty()


class ChargeRecord(db.Model):
  user = db.StringProperty()
  date = db.DateProperty(auto_now_add=True)
  charge_rmb = db.FloatProperty()


class User(db.Model):
  name = db.StringProperty()
  balance = db.FloatProperty(default=0.0)


class CardBalanceRecord(db.Model):
  date = db.DateProperty(auto_now_add=True)
  submitor = db.StringProperty()
  balance = db.FloatProperty()


class GlobalVariableRecord(db.Model):
  lost = db.FloatProperty()


