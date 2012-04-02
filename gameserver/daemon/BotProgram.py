#/usr/bin/python

import os
import threading
import subprocess
from Log import log
from time import sleep

SLEEP_TIME = 0.01
MAX_EXECUTION_TIME = 3.00
languages = {
  'javascript': './jsbot'
}

class BotProgramException(Exception):

  def __init__(self, message):
    Exception.__init__(self)
    self.message = message

  def print_cmd_error(self, cmd):
    log('Error: ' + self.message + ' in command: ' + cmd)

class BotProgram(threading.Thread):

  def __init__(self, command, botpath):
    self.input = None
    self.error = None
    self.program = None
    self.command = command
    self.botpath = botpath
    self.program = subprocess.Popen(
      [self.command, self.botpath],
      bufsize=256,
      close_fds=True,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE
    )
    threading.Thread.__init__(self)

  def send(self, command):
    if self.program.poll() != None:
      raise BotProgramException("Cannot send to crashed program: " + command)
    self.input = None
    self.program.stdin.write(command + "\n")
    self.program.stdin.flush()
    if command == 'quit':
      self.__kill()
      return 'ok'
    else:
      timeout = 0.0
      while (True):
        if self.input:
          return self.input
        elif self.error:
          raise BotProgramException(self.error)
        elif timeout > MAX_EXECUTION_TIME:
          self.program.kill()
          self.__kill()
          raise BotProgramException("Timeout waiting for command: " + command)
        sleep(SLEEP_TIME)
        timeout += SLEEP_TIME

  def __kill(self):
    try: self.program.kill()
    except (OSError): pass

  def run(self):
    while self.program.poll() == None:
      try:
        self.input = self.program.stdout.readline().strip()
      except:
        self.error = self.program.stderr.readline().strip()
    log("bot exit")

  def write_cmd(self, c, printcmd = False):
    try:
      r = self.send(c)
      if printcmd: log(c)
      return r == 'ok'
    except BotProgramException as e:
      e.print_cmd_error(c)
      return False

  def read_cmd(self, c, dflt, printcmd = True):
    try:
      r = self.send(c)
      if printcmd: log(c + ': ' + str(r))
      return r
    except BotProgramException as e:
      e.print_cmd_error(c)
      return dflt

  def cmd_quit(self):
    try:
      self.send('quit')
      return True
    except BotProgramException as e:
      e.print_cmd_error(cmd)
      return False

  def cmd_init(self, id, w, h, d):
    return self.write_cmd(
      'init %d %d %d %d' %
      (id, w, h, d)
    )

  def cmd_time(self, t):
    return self.write_cmd(
      'time %d' %
      (t,)
    )

  def cmd_obstacle(self, o):
    return self.write_cmd(
      'obstacle %d %d %d %d' %
      (o.id, o.x, o.y, o.r)
    )

  def cmd_obstacle_in_range(self, obstacle, inrange):
    return self.write_cmd(
      'obstacle-in-range %d %d' %
      (obstacle.id, 1 if inrange else 0)
    )

  def cmd_weapon(self, w):
    return self.write_cmd(
      'weapon %d %f %f' %
      (w.id, w.power, w.aim)
    )

  def cmd_enemy(self, e, inrange):
    return self.write_cmd(
      'enemy %d %d %d %f %f %f %d' %
      (e.id, e.x, e.y, e.energy, e.condition, e.speed, 1 if inrange else 0),
      printcmd = True
    )

  def cmd_enemy_weapon(self, e, w):
    return self.write_cmd(
      'enemy-weapon %d %d %f %f' %
      (e.id, w.id, w.power, w.aim)
    )

  def cmd_bot(self, b):
    return self.write_cmd(
      'bot %d %d %d %f %f %f %d' %
      (b.id, b.x, b.y, b.energy, b.condition, b.speed, b.id),
      printcmd = True
    )

  def cmd_state_change(self):
    return self.read_cmd('state-change', 'stop')

  def cmd_aim(self, w):
    return float(self.read_cmd('aim %d' % w.id, 0.0))

  def cmd_move(self):
    rval = self.read_cmd('move', 'n 1.0').split(' ')
    return (rval[0], float(rval[1]))

def open(botpath, language):
  program = BotProgram(languages[language], botpath)
  program.start()
  return program

