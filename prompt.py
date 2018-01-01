#coding: utf-8

from database import Database

DBFILE = "data.db"

d = Database(DBFILE)

class Command():
  instances = []
  def __init__(self,name,man,f,alias=[]):
    Command.instances.append(self)
    self.name = name
    self.alias = alias
    self.man = man
    self.f = f

  def __call__(self,*args,**kwargs):
    return self.f(*args,**kwargs)

def admin_prompt():
  pass

# == Helper functions ==

# Turns an invalid cased string or an int into the correct item string

def adapt_item(s):
  items = {}
  for i,name,price in d.get_items():
    items[i] = name
  try:
    return items[int(s)]
  except ValueError:
    pass
  if s in items.values():
    return s
  s = s.lower()
  for i in items.values():
    if i.lower() == s:
      return i
  return s

# == Defining user prompt callbacks ==

def u_buy(user,item,amount=1):
  item = adapt_item(item)
  try:
    for i in range(int(amount)):
      d.buy(user,item)
  except AttributeError:
    print("Unknown item:",item)
    return
  print("Bought %s %s"%(amount,item))
  print("You have %.2f € left"%(d.get_balance(user)/100))
Command("buy","",u_buy,['b'])

def u_list(user=None):
  l = d.get_items()
  print("Here are all the available items:")
  for i,name,price in l:
    print('  (%d) %s %.2f €'%(i,name,price/100))
Command("list","",u_list,['l','ls'])

user_cmd_dict = {}

for cmd in Command.instances:
  for a in [cmd.name]+cmd.alias:
    user_cmd_dict[a] = cmd.f


def user_prompt(user):
  """
  Simply type the name or id of the item to buy one and disconnect
  If you want to buy multiple items, use "b" (or "buy")

  Type ? (or help) to see this help

  Type b <item> [amount] (or buy) to buy amount items (default=1)
  Unlike the previous method, this will not disonnect you

  Type l (or list or ls) to see the items, their ids and their price

  Type h (or hist) to view your transaction history

  Type u (or undo) and follow the prompt to undo a transaction
  You can only undo transactions that happened less than 1h ago
  """
  print("Hello %s! Type 'help' for help"%user)
  u_list()
  balance = d.get_balance(user)/100
  print("Your balance is %.2f €"%balance)
  if balance < 0:
    print("Think about paying your debts !")
  while True:
    s = input("[Godersi] %s> "%user).split(" ")
    if not s:
      continue
    cmd,*args = s
    if cmd in user_cmd_dict:
      user_cmd_dict[cmd](user,*args)
    elif cmd in ['exit','quit','disconnect','logout']:
      break
    else:
      cmd = adapt_item(cmd)
      if args:
        print("%s takes no argument",cmd)
        continue
      try:
        d.buy(user,cmd)
      except AttributeError:
        print("Unknown comand or item:",cmd)
        continue
      print("Bought a %s"%cmd)
      print("You have %.2f € left"%(d.get_balance(user)/100))
      break

def main_prompt():
  while True:
    username = input("[Godersi] login> ")
    if username == "admin":
      try:
        admin_prompt()
      except EOFError:
        pass
      print("Exiting admin prompt")
      continue
    if username in ['exit','quit','q','logout']:
      break
    elif username not in d.get_users():
      print("Unknown username:", username)
      continue
    try:
      user_prompt(username)
    except EOFError:
      pass
    print("\n%s disconnected"%username)

if __name__ == "__main__":
  try:
    main_prompt()
  except EOFError:
    pass
  print("\nQuitting Godersi, bye!")
