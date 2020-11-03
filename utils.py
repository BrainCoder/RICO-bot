import json
import asyncio
import settings

from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, TEXT, DATETIME, TINYINT
from os import listdir
from os.path import isfile, join

global engine
global conn
global meta
global userdata
global mod_event
global mod_event_type

def init():
    global engine
    global conn
    global meta
    global userdata
    global mod_event
    global mod_event_type
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
        Column('lynch_count', INTEGER, nullable=False, default=0),
        Column('successful_lynch_count', INTEGER, nullable=False, default=0),
        Column('lynch_expiration_time', BIGINT)
    )

    mod_event_type = Table(
        'mod_event_type', meta,
        Column("mod_type_id", INTEGER, primary_key=True, nullable=False, autoincrement=True),
        Column("mod_action_type", TEXT, nullable=False)
    )

    mod_event = Table(
        'mod_event', meta,
        Column('event_id', BIGINT, primary_key=True, nullable=False, autoincrement=True),
        Column('recipient_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('event_type', INTEGER, ForeignKey("mod_event_type.mod_type_id"), nullable=False),
        Column('reason', TEXT),
        Column('event_time', DATETIME, nullable=False),
        Column('issuer_id', BIGINT, ForeignKey("userdata.id"), nullable=False),
        Column('historical', TINYINT, nullable=False, default=0)
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

# Checklist Channel
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
