#coding: utf-8

import sqlite3
import sys

assert sys.version_info.major == 3,"Please use Python3"

class Database:
  def __init__(self,filename):
    self.filename = filename
    self.conn = sqlite3.connect(filename)
    if not self.check_db():
      self.new_db()

  def user_to_id(self,s):
    if isinstance(s,int):
      return s
    curr = self.conn.cursor()
    curr.execute("SELECT id FROM user WHERE name=?;",(s,))
    r = curr.fetchone()
    if len(r) == 0:
      raise AttributeError(s)
    curr.close()
    self.conn.commit()
    return r[0]

  def item_to_id(self,s):
    if isinstance(s,int):
      return s
    curr = self.conn.cursor()
    curr.execute("SELECT id FROM item WHERE name=?;",(s,))
    r = curr.fetchone()
    if len(r) == 0:
      raise AttributeError(s)
    curr.close()
    self.conn.commit()
    return r[0]

  def check_db(self):
    curr = self.conn.cursor()
    success = False
    try:
      curr.execute("SELECT * FROM user;")
      curr.execute("SELECT * FROM item;")
      curr.execute("SELECT * FROM checkout;")
      curr.execute("SELECT * FROM refund;")
      success = True
    except sqlite3.OperationalError:
      pass
    curr.close()
    self.conn.commit()
    return success

  def new_db(self):
    if input("Creating a new database. Continue ? (y/[n])").lower() != "y":
      return
    curr = self.conn.cursor()
    for i in ('user','item','checkout','refund'):
      try:
        curr.execute("DROP TABLE %s;"%i)
      except sqlite3.OperationalError:
        pass
    curr.execute("""CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE);"""),
    curr.execute("""CREATE TABLE item(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price INTEGER);""")
    curr.execute("""CREATE TABLE checkout(
    user INTEGER,
    item INTEGER,
    date DATETIME DEFAULT CURRENT_TIMESTAMP);""")
    curr.execute("""CREATE TABLE refund(
    user INTEGER,
    amount INTEGER,
    date DATETIME DEFAULT CURRENT_TIMESTAMP);""")

  def add_user(self,name):
    curr = self.conn.cursor()
    try:
      curr.execute(
        "INSERT INTO user(name) VALUES (?);",
        (name,))
    except sqlite3.IntegrityError:
      print("Impossible: user already exists!")
    curr.close()
    self.conn.commit()

  def add_item(self,name,price):
    curr = self.conn.cursor()
    try:
      curr.execute("INSERT INTO item(name,price) VALUES (?,?);",
        (name,price))
    except sqlite3.IntegrityError:
      print("Impossible: the item already exists!")
    curr.close()
    self.conn.commit()

  def refund(self,user,amount):
    user = self.user_to_id(user)
    curr = self.conn.cursor()
    curr.execute("INSERT INTO refund(user,amount) VALUES (?,?);",(user,amount))
    curr.close()
    self.conn.commit()

  def buy(self,user,item):
    user = self.user_to_id(user)
    item = self.item_to_id(item)
    curr = self.conn.cursor()
    curr.execute("INSERT INTO checkout(user,item) VALUES (?,?);",(user,item))
    curr.close()
    self.conn.commit()

  def get_items(self):
    curr = self.conn.cursor()
    curr.execute("SELECT * FROM item;")
    r = curr.fetchall()
    curr.close()
    self.conn.commit()
    return r

  def get_balance(self,user):
    user = self.user_to_id(user)
    curr = self.conn.cursor()
    user = self.user_to_id(user)
    curr.execute("SELECT amount FROM refund WHERE user=?;",(user,))
    ref = [i[0] for i in curr.fetchall()]
    curr.execute("""SELECT item.price FROM checkout
        JOIN item
        ON item.id = checkout.item
        WHERE user=?
        ;""",(user,))
    exp = [i[0] for i in curr.fetchall()]
    curr.close()
    self.conn.commit()
    return sum(ref) - sum(exp)
