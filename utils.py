import json
from datetime import datetime, timedelta
import asyncio

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text
from sqlalchemy.dialects.mysql import insert
from os import listdir
from os.path import isfile, join
import settings
def to_dt(t_stamp):
    return datetime.fromtimestamp(t_stamp)

def readFile(fileName):
    with open(fileName, 'r') as myfile:
        return myfile.read()

async def waitThenRun(seconds, fn):
    await asyncio.sleep(seconds)
    await fn()

# Main Streak
def is_in_channel():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["streaks"]:
            return True
        return False
    return inside_fn

# Complaints Channel
def is_in_channel2():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["complaints"]:
            return True
        return False
    return inside_fn

def is_in_channel3():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["checklist"]:
            return True
        return False
    return inside_fn


"""
def hasPerms(ctx, requiredLevel):
    for role in idData['streakRoles']:
        for memberRole in member.roles:
            if memberRole.id == idData['streakRoles'][role]:
                return idData['streakRoles'][role]
"""

#SQLite3 database setup
engine = create_engine('sqlite:///main.db', echo = True)
conn = engine.connect()
meta = MetaData()
userdata = Table(
   'userdata', meta,
   Column('id', Integer, primary_key = True),
   Column('last_relapse', Integer),
   Column('usertype', Integer),
   Column('past_streaks', Text),
   Column('points', Integer),
)

idData = {}
idpath = "./ids/"
fileNames = [f for f in listdir(idpath) if isfile(join(idpath, f))]
for name in fileNames:
    data = json.loads(readFile(idpath+name))
    idData[data['serverId']] = data
