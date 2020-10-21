import json
import asyncio
import settings

from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT
from os import listdir
from os.path import isfile, join

global engine
global conn
global meta
global userdata

def init():
    global engine
    global conn
    global meta
    global userdata
    engine = create_engine(settings.config["databaseUrl"], echo=True)
    conn = engine.connect()
    meta = MetaData()
    userdata = Table(
        'userdata', meta,
        Column('id', BIGINT, primary_key=True, nullable=False),
        Column('last_relapse', BIGINT),
        Column('usertype', INTEGER),
        Column('past_streaks', TEXT),
        Column('points', BIGINT),
    )
    meta.create_all(engine)

def to_dt(t_stamp):
    return datetime.fromtimestamp(t_stamp)


def readFile(fileName):
    with open(fileName, 'r') as myfile:
        return myfile.read()


async def waitThenRun(seconds, fn):
    await asyncio.sleep(seconds)
    await fn()


# Main Streak
def is_in_streak_channel():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["streaks"]:
            return True
        return False
    return inside_fn


# Complaints Channel
def is_in_complaint_channel():
    def inside_fn(ctx):
        #channelName = 760244981838512158
        if ctx.channel.id == settings.config["channels"]["complaints"]:
            return True
        return False
    return inside_fn


def is_in_checklist_channel():
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

idData = {}
idpath = "./ids/"
fileNames = [f for f in listdir(idpath) if isfile(join(idpath, f))]
for name in fileNames:
    data = json.loads(readFile(idpath+name))
    idData[data['serverId']] = data
