#!/usr/bin/env python
# -*- coding: GB2312 -*-
# Last modified: 

"""docstring
"""

__revision__ = '0.1'

from database import *

def all_users():
    users = []
    for user in User.all():
        users.append(user.name)

    return users

def balance(user):
    """ This is a cpu consume function
      use as less as you can.
    """
    charges = ChargeRecord.all()
    charges.filter('user = ', user)
    all_charge = 0.0

    for charge in charges:
        all_charge += charge.charge_rmb

    lunchs = LunchRecord.all()
    lunchs.filter('user = ', user)
    all_cost = 0.0

    for lunch in lunchs:
        all_cost += lunch.cost_rmb

    return all_charge - all_cost

def update_balance(user, plus_value, minus_value):
    query = User.all()
    query.filter('name =', user)

    user = query.fetch(1)
    user[0].balance += plus_value - minus_value

    user[0].put()

def card_balance():
    #query = CardBalanceRecord.All()
    #query.filter()
    pass

def card_balance_expection():
    pass
