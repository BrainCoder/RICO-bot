import discord
import random
from discord.ext import commands
from discord.ext.commands import CommandNotFound, CheckFailure
import json
from datetime import datetime, timedelta
import pickle
import asyncio
import functools
import time
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text
from sqlalchemy.dialects.mysql import insert
from os import listdir
from os.path import isfile, join

def to_dt(t_stamp):
    return datetime.fromtimestamp(t_stamp)

def readFile(fileName):
    with open(fileName, 'r') as myfile:
        return myfile.read()

async def waitThenRun(seconds, fn):
    await asyncio.sleep(seconds)
    await fn()

# Check function to find out if the message came from a permitted channel:
def is_in_channel(channelName):
    def inside_fn(ctx):
        if ctx.channel.id == idData['channels'][channelName]:
            return True
        return False
    return inside_fn

def hasPerms(ctx, requiredLevel):
    for role in idData['streakRoles']:
        for memberRole in member.roles:
            if memberRole.id == idData['streakRoles'][role]:
                return idData['streakRoles'][role]

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
