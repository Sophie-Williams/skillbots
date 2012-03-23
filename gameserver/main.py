#!/usr/bin/python

import os
import math
import random
import MySQLdb
import traceback
import BotProgram
from time import sleep

class Weapon(object):

  def __init__(self, bot):
    self.aim = 0.0
    self.power = 1.0
    self.id = 1
    self.bot = bot

  def fire(self):
    pass

class Bot(object):

  def __init__(self, dbbot):
    self.bid = dbbot[0]
    self.uid = dbbot[1]
    self.nid = dbbot[2]
    self.ispublic = dbbot[3]
    self.training = dbbot[4]
    self.language = dbbot[5]
    self.path = dbbot[6]
    self.program = BotProgram.open(dbbot[6], dbbot[5])
    self.x = 0
    self.y = 0
    self.max_energy = 25
    self.energy = 25
    self.condition = 1.0
    self.speed = 1.0
    self.scanning_range = 8
    self.dir = 'n'
    self.state = 'move'
    self.weapons = [ Weapon(self) ]

  def inrange(self, other):
    pass

class Obstacle(object):

  def __init__(self, id, x, y, r):
    self.x = x
    self.y = y
    self.r = r
    self.id = id

  def inrange(self, bot):
    pass

db=MySQLdb.connect(user="root", db="damnart_com")

if __name__ == '__main__':

  c = db.cursor()

  while True:

    sleep(1)

    # fetch an arena
    c.execute("""
      SELECT aid,run
      FROM skb_arena
      WHERE NOT run
      LIMIT 1
    """)
    arena = c.fetchone()
    if not arena: continue

    # fetch bots in arena
    c.execute("""
      SELECT b.bid,b.uid,b.nid,b.ispublic,b.training,b.language,b.path
      FROM skb_bot b
      LEFT JOIN skb_arena_bot a ON b.bid = a.bid
      WHERE a.aid = %d
    """ % arena[0])
    dbbots = c.fetchall()

    # build bot objects
    bots = []
    for dbbot in dbbots:
      bots.append(Bot(dbbot))

    # init arena
    arenaduration = 1000
    arenawidth = len(bots) * 6 + random.randint(2, 20)
    arenaheight = len(bots) * 6 + random.randint(2, 20)
    for bot in bots: bot.program.cmd_init(arenawidth, arenaheight, arenaduration)
    print('TODO: create db arena ' + str(arenawidth) + ' ' + str(arenaheight) + str(arenaduration))

    # init obstacles
    obstacles = []
    numobstacles = int(math.sqrt(arenawidth * arenaheight) / 2)
    numobstacles += random.randint(-5, 5)
    for i in range(numobstacles):
      r = random.randint(1, 4)
      x = random.randint(0, arenawidth)
      y = random.randint(0, arenaheight)
      obstacle = Obstacle(i, x, y, r)
      for bot in bots: bot.program.cmd_obstacle(obstacle)
      obstacles.append(obstacle)
      print('TODO: create db obstacle ' + str(obstacle))

    # bot starting locations
    print('TODO: add bots to arena ' + str(bots))

    # init enemies
    for bot in bots:
      bot.enemies = []
      for enemy in bots:
        if bot.bid != enemy.bid:
          bot.enemies.append(enemy)
          bot.program.cmd_enemy(enemy)

    # Run the arena.
    for x in range(duration):

      # Update everybody's state.
      for bot in bots:

        # Update remote bot state.
        bot.program.cmd_bot(bot)

        # Tell remote if obstacles are in range.
        for obstacle in obstacles:
          bot.program.cmd_obstacle_in_range(obstacle, obstacle.inrange(bot))

        # Update remote enemy state.
        for enemy in bot.enemies:
          bot.program.cmd_enemy(enemy, enemy.inrange(bot))

        # Invoke stateChange().
        bot.state = bot.program.cmd_state_change()

      # Everybody who's firing, aim.
      for bot in bots:
        if bot.state in ('attack', 'attack+move'):
          for weapon in bot.weapons:
            weapon.aim = bot.program.cmd_aim(weapon)

      # Everybody who's moving, move.
      for bot in bots:
        s = bot.state 
        if bot.state in ('move', 'attack+move', 'defend+move'):
          bot.dir, bot.speed = bot.program.cmd_move()
          # TODO: move bot
          # TODO: collide, collision damage

      # Resolve combat.
      for bot in bots:
        if bot.state in ('attack', 'attack+move'):
          for weapon in bot.weapons:
            targettype, target, endx, endy = weapon.fire()
            if targettype == 'none':
              pass
            elif targettype == 'obstacle':
              pass
            if targettype == 'enemy':
              # TODO: calculate damage here
              if target.state == 'defend': pass
              elif target.state == 'defend+move': pass
              else: pass
            # TODO: notify bot and enemies in range about shot

    for bot in bots: bot.program.cmd_quit()

  #c=db.cursor()
  #max_price=5
  #c.execute("""SELECT * FROM node""")
  #print(c.fetchall())

