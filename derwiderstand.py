import discord
import json
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

db = json.load(open('db.json','r'))

def commit():
    json.dump(db, open('db.json','w'))
    
@bot.command()
async def register(ctx, arg):
    if arg not in db['players']:
        db['players'][arg] = {'name': arg, 'score': 0, 'wins': 0, 'losses': 0}
        commit()
        await ctx.send('added new player: %s' % arg)
    else:
        await ctx.send('player % already exists' % arg)

@bot.command()
async def showscore(ctx):
    sort = sorted(db['players'], key=lambda x: -db['players'][x]['score'])
    await ctx.send('current standings:\n[points // win rate]\n-------------\n'+'\n'.join('%s. %s\n[%s // %.2f'%(n+1,i,db['players'][i]['score'],100.0*db['players'][i]['wins']/(0.0000000000000000000000000001+db['players'][i]['wins']+db['players'][i]['losses']))+'%]\n-------------' for n,i in enumerate(sort)))
    
@bot.command()
async def newgame(ctx, *args):

    
    

    reactions = {"\u0035\u20E3":5, "\u0036\u20E3":6,"\u0037\u20E3":7,"\u0038\u20E3":8,"\u0039\u20E3":9, u"\U0001F51F":10}
    roles = {'✅':'resistance', '❌':'spy', u"\U0001F1F7":'rogue', u"\U0001F1F2":'merlin'}
    base_roles = ['resistance', 'spy']


    
    msg = await ctx.send('choose number of players')
    for i in reactions:

        await msg.add_reaction(i)

    def check_author(msg,usr):
        if usr==ctx.author:
            return 1
        return 0
    answer, user = await bot.wait_for('reaction_add', check=check_author)

    player_count = reactions[answer.emoji]
    await ctx.send('beep boop beep\nselect participants & roles')


    for player in db['players']:
        if args and player not in args:
            continue
        res = await ctx.send('-------------\n'+player)
        
        for i in roles:
            await res.add_reaction(i)

    msgs = {}
    current_players = set()
    while len(current_players) < player_count:
        answer, user = await bot.wait_for('reaction_add', check=check_author)
        player = answer.message.content.split('\n')[-1]
        if roles[answer.emoji] not in base_roles:
            continue
        if player not in current_players:
            current_players.add(player)
        print(current_players)
        msgs[player] = answer.message

    final_roles = {}
    for i in msgs:
        player_roles = [roles[j.emoji] for j in msgs[i].reactions if j.count > 1]
        if player_roles:
            final_roles[i] = player_roles

    msg = await ctx.send('select winning team to finalize results')#\n(rogue+resistance=rogue resistance win, merlin+spy=spies win by guessing merlin, etc.. press the spy/resistance button last as it finalizes the choice)
    for i in roles:

        await msg.add_reaction(i)

    while 1:
        answer, user = await bot.wait_for('reaction_add', check=check_author)
        if roles[answer.emoji] in base_roles:
            final_result = [roles[j.emoji] for j in answer.message.reactions if j.count > 1]
            break
    game = {'players':final_roles, 'result': final_result}
    print(game)
    db['games'].append(game)
    winners = []
    
    if 'rogue' in final_result:
        if 'spy' in final_result:
            for i in final_roles:
                if 'rogue' in final_roles[i] and 'spy' in final_roles[i]:
                    db['players'][i]['score'] += 1
                    winners.append(i)
        elif 'resistance' in final_result:
            for i in final_roles:
                if 'rogue' in final_roles[i] and 'resistance' in final_roles[i]:
                    db['players'][i]['score'] += 1
                    winners.append(i)
    elif 'resistance' in final_result:
        for i in final_roles:
                if 'resistance' in final_roles[i]:
                    if 'rogue' in final_roles[i]:
                        db['players'][i]['score'] += 0.5
                    else:
                        db['players'][i]['score'] += 1
                    winners.append(i)
    elif 'spy' in final_result:
        for i in final_roles:
                if 'spy' in final_roles[i]:
                    db['players'][i]['score'] += 1
                    winners.append(i)

    losers = [i for i in final_roles if i not in winners]

    #lists needed for rating calc later..
    for i in winners:
        db['players'][i]['wins'] += 1
    for i in losers:
        db['players'][i]['losses'] += 1
    
    await ctx.send('winners: %s\nlosers: %s' % (', '.join(['[%s]'%i for i in winners]), ', '.join(['[%s]'%i for i in losers])))


    
    commit()
    
    
    
    

    
    
    


bot.run('NjAxNDA3MDQ4OTEwODk3MTcw.XTC_Sw.70GIMRagYdWQdHRuyCKCG4eh66w')
