from enum import IntEnum, unique, auto
from utils import *

@unique
class Perm(IntEnum):
    MUTED = auto()
    GUEST = auto()
    MEMBER = auto()
    SMOD = auto()
    MOD = auto()
    HMOD = auto()
    ADMIN = auto()

banDict = {}

async def hourly():
    while True:
        await asyncio.sleep(60*60)
        for key in banDict:
            if banDict[key] > 0:
                banDict[key] -= 1
            else:
                del banDict[key]


# To prevent mass bans
#@commands.event
async def on_member_ban(guild, user):
    if (datetime.today() - user.joined_at).days < 3:
        return
    ban_initiator = None
    limits = [10*x**2 for x in range(1,5)] + [None]
    for fetchAttempt in limits:
        print(fetchAttempt)
        await asyncio.sleep(1)
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=fetchAttempt):
            if entry.target == user:
                ban_initiator = entry.user
                if ban_initiator.id not in list(banDict.keys()):
                    banDict[ban_initiator.id] = 1
                else:
                    banDict[ban_initiator.id] += 1
                print(f'{ban_initiator.name}#{ban_initiator.discriminator} banned someone')
                break
    if ban_initiator is None:
        pass
    if banDict[ban_initiator.id] > 10:
        roleObj = guild.get_role(combinedDict['Moderator'])
        await ban_initiator.remove_roles(roleObj)


@commands.command()
async def clear(ctx,amount=5):
    await ctx.channel.purge(limit=amount)
    print (f'Bot cleared {amount} messages')

@commands.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await ctx.channel.send("This command hasn't been coded yet")
#    await member.kick(reason=reason)
#    await ctx.channel.purge (limit=1)
#    print (f'{member} was kicked from the server')

@commands.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await ctx.channel.send("This command hasn't been coded yet")
#    await member.ban(reason=reason)
#    await ctx.channel.purge (limit=1)
#    print (f'{member} was banned from the server')


@commands.command()
async def lynch(ctx, member : discord.Member):
    await ctx.channel.send("This command hasn't been coded yet")


async def getMemberLevel(member):
    memberLevel = None
    if(member.roles.has(otherRoles.get('Admin'))):
        memberLevel = Perm.ADMIN
    elif(member.roles.has(otherRoles.get('Manager'))):
        memberLevel = Perm.HMOD
    elif(member.roles.has(otherRoles.get('Moderator'))):
        memberLevel = Perm.MOD
    elif(member.roles.has(otherRoles.get('Honorable'))):
        memberLevel = Perm.SMOD
    elif(member.roles.has(otherRoles.get('Member'))):
        memberLevel = Perm.MEMBER
    else:
        memberLevel = Perm.GUEST
    return memberLevel;






#
#       if(appliedMember !== undefined && member.joinedTimestamp < appliedMember.joinedTimestamp){
#         for(lynchVoted in lynchDict){
#           if(member.id in lynchDict[lynchVoted]){
#             console.log(`Can't vote to lynch of ${appliedMember.displayName} by ${member.displayName} because already voted before.`);
#             return;
#           }
#         }
#         if(appliedMember.id in lynchDict && !lynchDict[appliedMember.id].includes(member.id)){
#           lynchDict[appliedMember.id].push(member.id);
#           console.log(`Pushed lynch order ${lynchDict[appliedMember.id].length} of ${appliedMember.displayName} by ${member.displayName}.`);
#         }else if(!(appliedMember.id in lynchDict)){
#           lynchDict[appliedMember.id] = [member.id];
#           console.log(`Pushed lynch order 1 of ${appliedMember.displayName} by ${member.displayName}.`);
#         }else{
#           return;
#         }
#         message.channel.send(`Vote to lynch ${appliedMember.displayName} by ${member.displayName} accepted.`);
#         if(lynchDict[appliedMember.id].length >= 3){
#           names = "";
#           for (idN of lynchDict[appliedMember.id]){
#             let lynchingMember = await message.guild.fetchMember(idN).catch(err => console.log(err.toString()));
#             if (lynchingMember !== undefined){
#               lynchingMember.addRole(otherRoles.get('Spoiled'))
#               .catch(error => console.log(error));
#               await lynchingMember.removeRole(otherRoles.get('Member'))
#               .then(function(){
#                 console.log(`Removed ${lynchingMember.displayName}'s Member role.`);
#                 names += lynchingMember.displayName + " ";
#               })
#               .catch(error => console.log(error));
#             }
#           }
#           //delete lynchDict[appliedMember.id];
#           appliedMember.addRole(otherRoles.get('Muted'))
#           .then(function(){
#             console.log(`Added Muted role to ${appliedMember.username} through lynching.`);
#             message.channel.send(`${appliedMember.displayName} was muted, and ${names} temporarily paid their member role for it.`);
#             message.guild.channels.get(channelIDs.get('log')).send(`${appliedMember.displayName} was lynched, and ${names} temporarily paid their member role for it.`);
#           })
#           .catch(error => console.log(error));
#         }
#       }else if(appliedMember !== undefined && member.joinedTimestamp >= appliedMember.joinedTimestamp){
#         console.log(`Can't vote to lynch of ${appliedMember.displayName} by ${member.displayName} because of younger/older rule.`);
#       }
#     }
#     break;
#   }
# }
#         // FAILSAFE, DO NOT REMOVE!
#         if(proxyFlag){
#           return;
#         }
#
#         if(memberLevel == Perm.ADMIN){
#           if (cmd === "bulkdelete" && Number.isInteger(parseInt(args[0])) && args[0] > 0 && args[0] < 31 && args.length === 1) {
#             message.channel.bulkDelete(parseInt(args[0]) + 1)
#             .then(messages => console.log(`${member.toString()} bulk deleted ${messages.size} messages`))
#             .catch(console.error);
#           }
#           if (cmd === "msg"){
#               let content = message.content;
#               content = content.substr(content.indexOf(args[1]));
#               message.guild.channels.get(args[0]).send(content)
#               .catch(console.error);
#           }
#         }else if(memberLevel == Perm.HMOD || memberLevel == Perm.MOD){
#           if (cmd === "bulkdelete" && Number.isInteger(parseInt(args[0])) && args[0] > 0 && args[0] < 11 && args.length === 1) {
#             message.channel.bulkDelete(parseInt(args[0]) + 1)
#             .then(messages => console.log(`${member.toString()} bulk deleted ${messages.size} messages`))
#             .catch(console.error);
# 	       }
#         }
#         if(member.roles.has(otherRoles.get('Admin')) || member.roles.has(otherRoles.get('Facilitator'))){
#           console.log(cmd);
#           if(cmd == 'monthlyturn'){
#             console.log("MonthlyTurn executed by " + message.author.toString());
#             message.guild.channels.get('557201575270154241').send(`${message.author.toString()} started the next monthly challenge.`);
#             message.delete();
#             guild = await message.guild.fetchMembers();
#             for (var member of guild.members.values()) {
#               /**
#               if (member.roles.has(otherRoles.get('Monthlychallengewinner'))){
#                 await member.removeRole(otherRoles.get('Monthlychallengewinner'))
#                 .then(function(){
#                   console.log(`Removed Monthlychallengewinner role.`);
#                 })
#                 .catch(error => console.log(error));
#               }
#               **/
#               if (member.roles.has(otherRoles.get('Monthlychallengeparticipant'))){
#                 await member.removeRole(otherRoles.get('Monthlychallengeparticipant'))
#                 .then(function(){
#                   console.log(`Removed Monthlychallengeparticipant role.`);
#                 })
#                 .catch(error => console.log(error));
#                 member.addRole(otherRoles.get('Monthlychallengewinner'))
#                 .then(function(){
#                   console.log(`Added Monthlychallengewinner role.`);
#                 })
#                 .catch(error => console.log(error));
#               }
#
#               if (member.roles.has(additionalRoles.get('Monthlychallenge'))){
#                 await member.removeRole(additionalRoles.get('Monthlychallenge'))
#                 .then(function(){
#                   console.log(`Removed Monthlychallenge role.`);
#                 })
#                 .catch(error => console.log(error));
#                 member.addRole(otherRoles.get('Monthlychallengeparticipant'))
#                 .then(function(){
#                   console.log(`Added Monthlychallengeparticipant role.`);
#                 })
#                 .catch(error => console.log(error));
#               }
#
#             }
#           }
#         }
#         if(member.roles.has(otherRoles.get('Moderator')) || member.roles.has(otherRoles.get('Honorable'))){
#           var user_id;
#           var queryDict;
#           switch (cmd){
#
#             case 'c':
# 	    if(args.length < 2){
#               return;
#             }
#
#             await mute(args, message);
#             break;
#             case 'unmute':
#             await unmute(args, message);
#             break;
#         case 'r':
#         case 'reply':
#             if(message.channel.id === channelIDs.get('complaints-mod')){
#                 appliedMember = await getMentionedMember(message);
#                 if(appliedMember == undefined){
#                     message.channel.send('User not found.');
#                     return;
#                 }
#                 let content = message.content;
#                 content = content.substr(content.indexOf(args[1]));
#                 try {
#                   appliedMember.user.send(content);
#                   message.react('✅');
#                 }
#                 catch (e) {
#                   message.channel.send(e.stack);
#                 }
#
#             }
#         break;
# 	    case 's':
#             case 'strike':
#             if(args.length < 2){
#               return;
#             }
#             appliedMember = await getMentionedMember(message);
#             if(appliedMember === undefined){
#               return;
#             }
#             let content = message.content;
#             content = content.substr(content.indexOf(args[1]));
#             user_id = appliedMember.id;
#             queryString = `INSERT INTO streak (user_id, strikes) VALUES (${user_id}, ARRAY[$1])
#             ON CONFLICT (user_id) DO UPDATE SET strikes = streak.strikes || EXCLUDED.strikes;`;
#             //queryDict = {text:queryString, values:[(content+ ' -' + message.author.username)]};
#             let ct = new Date();
#             let dateString = ct.getUTCDate() +"/"+ (ct.getUTCMonth()+1) +"/"+ ct.getUTCFullYear() + " " + ct.getUTCHours() + ":" + ct.getUTCMinutes() + ":" + ct.getUTCSeconds();
#             let result = await query(queryString, [(content+ ' -' + message.author.username + ', ' + dateString)]);
#             message.guild.channels.get(channelIDs.get('log')).send(`${message.author.username} gave ${appliedMember.user.toString()} a strike with the reason:\n${content}`);
#             await mute([0], message);
#             break;
#             case 'removestrike':
#             if(args.length === 0){
#               return;
#             }
#             appliedMember = await getMentionedMember(message);
#             if(appliedMember === undefined){
#               return;
#             }
#
#             user_id = appliedMember.id;
#             if(args.length > 1 && !isNaN(args[1]) && parseInt(args[1]) >= 1){
#               queryString = `UPDATE streak SET strikes = strikes[1:array_upper(strikes, 1) - 1] WHERE user_id = '${user_id}';`;
#               return;
#             }else{
#               queryString = `UPDATE streak SET strikes = strikes[1:array_upper(strikes, 1) - 1] WHERE user_id = '${user_id}';`;
#             }
#             queryResult = await query(queryString);
#             message.guild.channels.get(channelIDs.get('log')).send(`${message.author.username} removed a strike of ${appliedMember.user.toString()}.`);
#             case 'getstrikes':
#             if(args.length === 0){
#               return;
#             }
#             appliedMember = await getMentionedMember(message);
#             if(appliedMember === undefined){
#               return;
#             }
#             user_id = appliedMember.id;
#             queryString = `SELECT strikes FROM streak WHERE user_id = '${user_id}';`;
#             queryResult = await query(queryString);
#             if(queryResult.rowCount !== null && queryResult.rowCount !== 0 && queryResult.rows[0]['strikes'] !== null && queryResult.rows[0]['strikes'].length !== 0){
#               let strikes = queryResult.rows[0]['strikes'];
#               let strikeString = `Strikes of ${appliedMember.user.username}:\n`
#               for(let [i, strike] of strikes.entries()){
#                 strikeString += `${i+1}. ${strike}\n`
#               }
#               message.guild.channels.get(channelIDs.get('strike-board')).send(strikeString);
#             }else{
#               message.guild.channels.get(channelIDs.get('strike-board')).send(`There are no strikes saved for ${appliedMember.user.toString()}.`);
#             }
#
#             //message.guild.channels.get('557201575270154241').send(`${message.author.username} gave ${appliedMember.user.username} a strike for:\n${content}`);
#             break;
#             case 'member':
# 		if(cmd === "member"){
#                 if(args.length !== 0){
#               appliedMember = await getMentionedMember(message);
#               if(appliedMember !== undefined){
#                 if (appliedMember.roles.has(otherRoles.get('Member'))){
#                   appliedMember.removeRole(otherRoles.get('Member'))
#                   .then(function(){
#                     console.log(`Removed Member's role.`);
#                   })
#                   .catch(error => console.log(error));
#
#                 }else{
#                   appliedMember.addRole(otherRoles.get('Member'))
#                   .then(function(){
#                     console.log(`Added Member's role.`);
#                   })
#                   .catch(error => console.log(error));
#                 }
#               }
#             }
#             }
#             break;
# 	    case 'unmember':
#             if(args.length !== 0){
#               appliedMember = await getMentionedMember(message);
#               if(appliedMember !== undefined){
#                 if (appliedMember.roles.has(otherRoles.get('Spoiled'))){
#                   appliedMember.removeRole(otherRoles.get('Spoiled'))
#                   .then(function(){
#                     console.log(`Removed Spoiled's role.`);
#                   })
#                   .catch(error => console.log(error));
#                 }else{
#                   appliedMember.addRole(otherRoles.get('Spoiled'))
#                   .then(function(){
#                     console.log(`Added Spoiled's role.`);
#                   })
#                   .catch(error => console.log(error));
# 		  if (appliedMember.roles.has(otherRoles.get('Member'))){
#                     appliedMember.removeRole(otherRoles.get('Member'))
#                     .then(function(){
#                       console.log(`Removed Member's role.`);
#                     })
#                     .catch(error => console.log(error));
#
#                   }
#
#                 }
#               }
#             }
#             break;
#
#             case 'underage':
#             if(args.length !== 0){
#               appliedMember = await getMentionedMember(message);
#               if(appliedMember !== undefined){
#                 if (appliedMember.roles.has(otherRoles.get('underage'))){
#                   appliedMember.removeRole(otherRoles.get('underage'))
#                   .then(function(){
#                     console.log(`Removed Underage's role.`);
#                   })
#                   .catch(error => console.log(error));
#                 }else{
#                   appliedMember.addRole(otherRoles.get('underage'))
#                   .then(function(){
#                     console.log(`Added Underage's role.`);
#                   })
#                   .catch(error => console.log(error));
#                 }
#               }
#             }
#             break;
#             case 'joinedat':
#             if(args.length !== 0){
#               appliedMember = await getMentionedMember(message);
#               if(appliedMember !== undefined){
# 	        let ja = appliedMember.joinedAt;
# 		let dateString = ja.getUTCDate() +"/"+ (ja.getUTCMonth()+1) +"/"+ ja.getUTCFullYear() + "  " + ja.getUTCHours() + ":" + ja.getUTCMinutes() + ":" + ja.getUTCSeconds();
#                 message.channel.send(`${appliedMember.displayName} joined at ${dateString}`);
#               }
#             }
#             break;
#           }
#         }
#
#       }
#       if(message.channel.id === channelIDs.get('subconscious-explanation')){ // ||  message.channel.id === channelIDs.get('roles')){
#         message.delete().catch();
#       }
#       if(message.channel.id == '519456910496235520' && message.content.length > 10 && message.content.length <= 255 + 4){
#         var lastIndex = message.content.lastIndexOf("!add");
#         if(lastIndex !== -1){
#           let content = message.content.substr(0, lastIndex);
#         }
#       }
#     }
#
#     client.on('guildMemberAdd', async function(member) {
#       let guideToStr = member.guild.channels.get('519455164894019584');
#       let streakGuideToStr = member.guild.channels.get('519627611836776490');
#       let streakToStr = member.guild.channels.get('519458736260120587');
#       //member.addRole(otherRoles.get('New member'))
#       //.then(function(){
#       //  console.log(`Added New member's role.`);
#       //})
#       //.catch(error => console.log(error));
#       let user_id = member.id;
#       queryString = `SELECT * FROM streak WHERE user_id = '${user_id}';`;
#       queryResult = await query(queryString);
#       if(queryResult === null || queryResult.rowCount === null ||  queryResult.rowCount === 0){
#         member.guild.channels.get('519455122602983424').send(member.toString() + ` welcome! Please go to ${guideToStr} to see a short explanation of what this server is about, and to ${streakGuideToStr} to see the commands you can use to assign yourself the appropriate roles in ${streakToStr}.`);
#       }else{
#         if(queryResult.rows[0]['muted'] === true){
#           member.addRole(otherRoles.get('Muted'));
#         }
#         if(queryResult.rows[0]['starting_date'] !== null){
#           let days = moment().diff(moment(queryResult.rows[0]['starting_date']), 'days');
#           await updateStreakRole(member, days);
#         }
#         member.guild.channels.get('519455122602983424').send(member.toString() + ` welcome back!`);
#         //await updateStatistics(member.guild)
#       }
#     });
