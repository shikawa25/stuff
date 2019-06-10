#! python3
# -*- coding: utf-8 -*-

import discord
import asyncio
import random
import json
import re
import operator
from discord.ext.commands import Bot
from discord.ext import commands

client = Bot(description='Um bot', command_prefix='~', pm_help = False)
paciencia = []
battle_running = []
boss_running = []
battle_survival = {"teste": 0}
survival_running = []
survivors = {"teste": 0}
votes = []
p1_hp = 100
p2_hp = 100
winners = []
losers = []

with open('D:\\heroes.json', 'r') as heroes:
	heroes_dict = json.load(heroes)

with open('D:\\leaderboard.json', 'r') as leaderboard:
	leaderboard_dict = json.load(leaderboard)

with open('D:\\boss.json', 'r') as boss:
	boss_dict = json.load(boss)
	
@client.event
async def on_ready():
	print("tudo certo")

	
@client.command(pass_context=True, aliases=['Choose_emote', 'CHOOSE_EMOTE'])
async def choose_emote(ctx):
	if ctx.message.author.id not in battle_running:
		message_content = ctx.message.content
		author_id = re.findall('(?:\d).*(?:\d)', ctx.message.author.id)
		clean_message = message_content.replace(message_content[:14], "")
		if clean_message.startswith("<:"):
			clean_id = str(author_id[0])
			new_user = {clean_id: clean_message}
			new_in_leaderboard = {clean_id: 0}
			heroes_dict.update(new_user)
			if clean_id not in leaderboard_dict:
				leaderboard_dict.update(new_in_leaderboard)
				with open('D:\\leaderboard.json', 'w') as leaderboard:
								json.dump(leaderboard_dict, leaderboard)
			await client.send_message(ctx.message.channel, "**Emote escolhido com sucesso.**")
			with open('D:\\heroes.json', 'w') as heroes:
								json.dump(heroes_dict, heroes)
		else:
			await client.send_message(ctx.message.channel, "**Isso não é um emote.**")
			return
	else:
		await client.send_message(ctx.message.channel, "**Você está em batalha, parceiro.**")
@client.command(pass_context=True, aliases=['Battle', 'BATTLE'])
async def battle(ctx):
	if len(battle_running) == 0:
		message_content = ctx.message.content
		clean_message = message_content.replace(message_content[:8], "")
		challenger_id = str(ctx.message.author.id)
		if challenger_id not in heroes_dict:
			await client.send_message(ctx.message.channel, "Você não escolheu um emote ainda.")
			return
		challenged_id = re.findall('(?:\d).*(?:\d)', ctx.message.content)
		if str(challenged_id[0]) not in heroes_dict:
			await client.send_message(ctx.message.channel, "Usuário desafiado não escolheu um emote ainda.")
			return
		if str(challenged_id[0]) == challenger_id:
			await client.send_message(ctx.message.channel, "**Você não pode se desafiar, malandrinho. <:hmmno:301493205373943820>**")
			return
		battle_running.append(challenger_id)
		battle_running.append(challenged_id[0])
		battle_log = await client.say("**A batalha começará em breve.**")
		await asyncio.sleep(5)
		p1_hp = 100
		p2_hp = 100
		p1_fatal = 0
		p2_fatal = 0
		healthy = "❤"
		damaged = "💔"
		ded = "🖤"
		log_icon = "#"
		p1_emoji_hp = healthy*3
		p2_emoji_hp = healthy*3
		turn = 0

		await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100")
		while p1_hp and p2_hp > 0:
			damage_list_p1 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p2 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			turn +=1
			if len(votes) ==3:
				battle_running.clear()
				votes.clear()
				print("cancelado")
				break

			await asyncio.sleep(2)

			hit_or_miss = random.choice(damage_list_p1)
			roll_damage_p1 = random.randint(1, 50)


			if hit_or_miss == "hit":
				if p2_fatal ==1:
					roll_damage_p1 / 2 + 1
				p2_hp = p2_hp - roll_damage_p1
				if p2_hp < 0:
					p2_hp = 0
				if p2_hp < 83:
					p2_emoji_hp = healthy*2+damaged
				if p2_hp < 67:
					p2_emoji_hp = healthy*2+ded
				if p2_hp < 51:
					p2_emoji_hp = healthy+damaged+ded
				if p2_hp < 35:
					p2_emoji_hp = healthy+ded*2
				if p2_hp < 19:
					p2_emoji_hp = damaged+ded*2
				if p2_hp == 0:
					p2_emoji_hp = ded*3

				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[challenger_id]+" causou "+str(roll_damage_p1)+" de dano! 💢")
				if p2_hp == 0:
					if p1_hp == 100:
						await client.send_message(ctx.message.channel, "<@"+challenger_id+"> derrotou "+clean_message+" de P-E-R-F-E-C-T. 💯")
						leaderboard_dict[challenger_id] +=5
						leaderboard_dict[str(challenged_id[0])] -=4
					else:
						await client.send_message(ctx.message.channel, "<@"+challenger_id+"> derrotou "+clean_message+".")
						leaderboard_dict[challenger_id] +=3
						leaderboard_dict[str(challenged_id[0])] -=2
					if leaderboard_dict[str(challenged_id[0])] <0:
						leaderboard_dict[str(challenged_id[0])] = 0
					with open('D:\\leaderboard.json', 'w') as leaderboard:
							json.dump(leaderboard_dict, leaderboard)
					battle_running.clear()
					votes.clear()
					break
			if hit_or_miss == "miss":
				await asyncio.sleep(2)
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[challenger_id]+" errou! 🌬")
			if hit_or_miss == "dodged":
				await asyncio.sleep(2)
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(challenged_id[0])]+" se esquivou! 🛡")
			if hit_or_miss == "crit":
				if p2_fatal ==1:
					roll_damage_p1 / 3 + 1
				p2_hp = p2_hp - roll_damage_p1*2
				if p2_hp < 0:
					p2_hp = 0
				if p2_hp < 83:
					p2_emoji_hp = healthy*2+damaged
				if p2_hp < 67:
					p2_emoji_hp = healthy*2+ded
				if p2_hp < 51:
					p2_emoji_hp = healthy+damaged+ded
				if p2_hp < 35:
					p2_emoji_hp = healthy+ded*2
				if p2_hp < 19:
					p2_emoji_hp = damaged+ded*2
				if p2_hp == 0:
					p2_emoji_hp = ded*3
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[challenger_id]+" causou "+str(roll_damage_p1*2)+" de dano **crítico**! 💥")
				if p2_hp == 0:
					if p1_hp == 100:
						await client.send_message(ctx.message.channel, "<@"+challenger_id+"> derrotou "+clean_message+" de P-E-R-F-E-C-T. 💯")
						leaderboard_dict[challenger_id] +=5
						leaderboard_dict[str(challenged_id[0])] -=4
					else:
						await client.send_message(ctx.message.channel, "<@"+challenger_id+"> derrotou "+clean_message+".")
						leaderboard_dict[challenger_id] +=3
						leaderboard_dict[str(challenged_id[0])] -=2
					if leaderboard_dict[str(challenged_id[0])] <0:
						leaderboard_dict[str(challenged_id[0])] = 0
					with open('D:\\leaderboard.json', 'w') as leaderboard:
							json.dump(leaderboard_dict, leaderboard)
					battle_running.clear()
					votes.clear()
					break

			if p1_hp <= 25 and p1_fatal == 0:
				damage_list_p2.append("dodged")
				damage_list_p2.append("dodged")
				damage_list_p2.append("dodged")
				damage_list_p2.append("dodged")
				damage_list_p1.append("crit")

				p1_fatal += 1
			if p2_hp <= 25 and p2_fatal == 0:
				damage_list_p1.append("dodged")
				damage_list_p1.append("dodged")
				damage_list_p1.append("dodged")
				damage_list_p1.append("dodged")
				damage_list_p2.append("crit")
				p2_fatal += 1

			await asyncio.sleep(2)
			hit_or_miss = random.choice(damage_list_p2)
			roll_damage_p2 = random.randint(1, 50)

			if hit_or_miss == "hit":
				if p1_fatal ==1:
					roll_damage_p2 / 2 + 1
				p1_hp = p1_hp - roll_damage_p2
				if p1_hp < 0:
					p1_hp = 0
				if p1_hp < 83:
					p1_emoji_hp = damaged+healthy*2
				if p1_hp < 67:
					p1_emoji_hp = ded+healthy*2
				if p1_hp < 51:
					p1_emoji_hp = ded+damaged+healthy
				if p1_hp < 35:
					p1_emoji_hp = ded*2+healthy
				if p1_hp < 19:
					p1_emoji_hp = ded*2+damaged
				if p1_hp == 0:
					p1_emoji_hp = ded*3
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(challenged_id[0])]+" causou "+str(roll_damage_p2)+" de dano! 💢")
				if p1_hp == 0:
					if p2_hp == 100:
						await client.send_message(ctx.message.channel, clean_message+" derrotou <@"+challenger_id+"> de P-E-R-F-E-C-T. 💯")
						leaderboard_dict[str(challenged_id[0])] +=5
						leaderboard_dict[challenger_id] -=4
					else:
						await client.send_message(ctx.message.channel, clean_message+" derrotou <@"+challenger_id+">.")
						leaderboard_dict[str(challenged_id[0])] +=3
						leaderboard_dict[challenger_id] -=2
					if leaderboard_dict[challenger_id] <0:
						leaderboard_dict[challenger_id] = 0
					with open('D:\\leaderboard.json', 'w') as leaderboard:
							json.dump(leaderboard_dict, leaderboard)
					battle_running.clear()
					votes.clear()
					break
			if hit_or_miss == "miss":
				await asyncio.sleep(2)
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(challenged_id[0])]+" errou! 🌬")
			if hit_or_miss == "dodged":
				await asyncio.sleep(2)
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[challenger_id]+" se esquivou! 🛡")

			if hit_or_miss == "crit":
				if roll_damage_p2 > 25:
					roll_damage_p2 + 15
				if p1_fatal ==1:
					roll_damage_p2 / 3 + 1
				p1_hp = p1_hp - roll_damage_p2*2
				if p1_hp < 0:
					p1_hp = 0
				if p1_hp < 83:
					p1_emoji_hp = damaged+healthy*2
				if p1_hp < 67:
					p1_emoji_hp = ded+healthy*2
				if p1_hp < 51:
					p1_emoji_hp = ded+damaged+healthy
				if p1_hp < 35:
					p1_emoji_hp = ded*2+healthy
				if p1_hp < 19:
					p1_emoji_hp = ded*2+damaged
				if p1_hp == 0:
					p1_emoji_hp = ded*3
				await client.edit_message(battle_log, str(p1_hp)+"/100\n"+p1_emoji_hp+" "+heroes_dict[challenger_id]+" ⚔ "+heroes_dict[str(challenged_id[0])]+" "+p2_emoji_hp+"\n"+"                                                 "+str(p2_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(challenged_id[0])]+" causou "+str(roll_damage_p2*2)+" de dano **crítico**! 💥")
				if p1_hp == 0:
					if p2_hp == 100:
						await client.send_message(ctx.message.channel, clean_message+" derrotou <@"+challenger_id+"> de P-E-R-F-E-C-T. 💯") #clean_message é para pingar mais rápido
						leaderboard_dict[str(challenged_id[0])] +=5
						leaderboard_dict[challenger_id] -=4
					else:
						await client.send_message(ctx.message.channel, clean_message+" derrotou <@"+challenger_id+">.")
						leaderboard_dict[str(challenged_id[0])] +=3
						leaderboard_dict[challenger_id] -=2
					if leaderboard_dict[challenger_id] <0:
						leaderboard_dict[challenger_id] = 0
					with open('D:\\leaderboard.json', 'w') as leaderboard:
							json.dump(leaderboard_dict, leaderboard)
					battle_running.clear()
					votes.clear()
					break
	else:
		await client.send_message(ctx.message.channel, "**Existe uma batalha em andamento.**")

@client.command(pass_context=True, aliases=['Top', 'TOP'])
async def top(ctx):
		ranking = sorted(leaderboard_dict.items(), key=operator.itemgetter(1), reverse=True)
		global_users = [user[0] for user in ranking]
		count = 0
		for user in global_users:
			check_server = discord.Server.get_member(ctx.message.server, user)
			if check_server is None:
				ranking.pop(count)
			else:
				count +=1
		users = [user[0] for user in ranking]
		points = [points[1] for points in ranking]
		while len(users) and len(points) < 10:
			users.append("375420060661055490")
			points.append(0)
		await client.send_message(ctx.message.channel, "```py\nRank | Nome\n\n[1]    "+str(discord.Server.get_member(ctx.message.server, users[0]))+"\n            Pontos: "+str(points[0])+"\n"+
		"[2]    "+str(discord.Server.get_member(ctx.message.server, users[1]))+"\n            Pontos: "+str(points[1])+"\n"+
		"[3]    "+str(discord.Server.get_member(ctx.message.server, users[2]))+"\n            Pontos: "+str(points[2])+"\n"+
		"[4]    "+str(discord.Server.get_member(ctx.message.server, users[3]))+"\n            Pontos: "+str(points[3])+"\n"+
		"[5]    "+str(discord.Server.get_member(ctx.message.server, users[4]))+"\n            Pontos: "+str(points[4])+"\n"+
		"[6]    "+str(discord.Server.get_member(ctx.message.server, users[5]))+"\n            Pontos: "+str(points[5])+"\n"+
		"[7]    "+str(discord.Server.get_member(ctx.message.server, users[6]))+"\n            Pontos: "+str(points[6])+"\n"+
		"[8]    "+str(discord.Server.get_member(ctx.message.server, users[7]))+"\n            Pontos: "+str(points[7])+"\n"+
		"[9]    "+str(discord.Server.get_member(ctx.message.server, users[8]))+"\n            Pontos: "+str(points[8])+"\n"+
		"[10]   "+str(discord.Server.get_member(ctx.message.server, users[9]))+"\n            Pontos: "+str(points[9])+"\n```")

@client.command(pass_context = True)
async def reset_top(ctx):
	if "217793175023124480" in ctx.message.author.id:
		for points in leaderboard_dict:
			leaderboard_dict[points] = 0
		await client.say('**Ranking resetado.**')
	with open('D:\\leaderboard.json', 'w') as leaderboard:
			json.dump(leaderboard_dict, leaderboard)
	if "217793175023124480" not in ctx.message.author.id:
		await client.say('**Comando apenas do meu goshujin-sama.**')

@client.command(pass_context = True)
async def cancel(ctx):
	if len(battle_running) ==2:
		if any(id in ctx.message.author.id for id in battle_running):
			if any(id in ctx.message.author.id for id in votes):
				pass
			else:
				votes.append(ctx.message.author.id)
				print("sucesso")
		if ctx.message.author.id not in battle_running:
			if any(id in ctx.message.author.id for id in votes):
				pass
			else:
				if len(votes) < 1:
					votes.append(ctx.message.author.id)
					print("sucesso voto externo")
	if len(votes) ==3:
		await client.say('**Batalha cancelada com sucesso.**')

@client.command(pass_context=True, aliases=['Survival', 'SURVIVAL'])
async def survival(ctx):
	if len(survival_running) > 0:
		await client.send_message(ctx.message.channel, "**Existe uma sobrevivência em andamento.**")
		return
	if len(battle_survival) < 7:
		surv_player = str(ctx.message.author.id)
		if surv_player not in heroes_dict.keys():
			await client.send_message(ctx.message.channel, "**Você não escolheu um emote ainda.**")
			return
		if surv_player in battle_survival.values():
			await client.send_message(ctx.message.channel, "**Você já está na próxima sobrevivência.**")
			return
		if surv_player in battle_running:
			await client.send_message(ctx.message.channel, "**Você está em batalha, parceiro.**")
			return
		if len(survivors) and len(battle_survival) ==6:
			survivors["p6"] = surv_player
			survivors["p6_hp"] = 100
			survivors["p6_fatal"] = 0
			battle_survival["p6"] = surv_player
			survival_running.append("true")
		if len(survivors) and len(battle_survival) ==5:
			survivors["p5"] = surv_player
			survivors["p5_hp"] = 100
			survivors["p5_fatal"] = 0
			battle_survival["p5"] = surv_player
		if len(survivors) and len(battle_survival) ==4:
			survivors["p4"] = surv_player
			survivors["p4_hp"] = 100
			survivors["p4_fatal"] = 0
			battle_survival["p4"] = surv_player
		if len(survivors) and len(battle_survival) ==3:
			survivors["p3"] = surv_player
			survivors["p3_hp"] = 100
			survivors["p3_fatal"] = 0
			battle_survival["p3"] = surv_player
		if len(survivors) and len(battle_survival) == 2:
			survivors["p2"] = surv_player
			survivors["p2_hp"] = 100
			survivors["p2_fatal"] = 0
			battle_survival["p2"] = surv_player
		if len(survivors) and len(battle_survival) ==1:
			survivors["p1"] = surv_player
			survivors["p1_hp"] = 100
			survivors["p1_fatal"] = 0
			battle_survival["p1"] = surv_player

		p1_roll_survivors = ["p2", "p3", "p4", "p5", "p6"]
		p2_roll_survivors = ["p1", "p3", "p4", "p5", "p6"]
		p3_roll_survivors = ["p2", "p1", "p4", "p5", "p6"]
		p4_roll_survivors = ["p2", "p3", "p1", "p5", "p6"]
		p5_roll_survivors = ["p2", "p3", "p4", "p1", "p6"]
		p6_roll_survivors = ["p2", "p3", "p4", "p5", "p1"]
		announce_surv = await client.say("**Você ocupou a vaga "+str(len(battle_survival)-1)+"/6 na próxima sobrevivência.**")
		print(survivors, battle_survival)
	if len(battle_survival) == 7:
		surv_battle_log = await client.say("**A sobrevivência começará em breve.**")
		winners.clear()
		losers.clear()
		await asyncio.sleep(5)
		p1 = battle_survival["p1"]
		p2 = battle_survival["p2"]
		p3 = battle_survival["p3"]
		p4 = battle_survival["p4"]
		p5 = battle_survival["p5"]
		p6 = battle_survival["p6"]
		healthy = "❤"
		damaged = "💔"
		ded = "🖤"
		p1_emoji_hp = healthy
		p2_emoji_hp = healthy
		p3_emoji_hp = healthy
		p4_emoji_hp = healthy
		p5_emoji_hp = healthy
		p6_emoji_hp = healthy
		log_icon = "#"
		turn = 0
		await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p5_hp"]))

		while len(p1_roll_survivors) or len(p2_roll_survivors) or len(p3_roll_survivors) or len(p4_roll_survivors) or len(p5_roll_survivors) or len(p6_roll_survivors) != 0:
			damage_list_p1 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p2 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p3 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p4 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p5 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			damage_list_p6 = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
			turn +=1
			if len(votes) ==6:
				battle_running.clear()
				votes.clear()
				break

			await asyncio.sleep(2)
##################### P1 TURN
			if survivors["p1_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p1)
				pick_player = random.choice(p1_roll_survivors)


				roll_damage_p1 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p1
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1)+" de dano em "+heroes_dict[str(p2)]+"! 💢")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p1
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1)+" de dano em "+heroes_dict[str(p3)]+"! 💢")
						if survivors["p3_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p1
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1)+" de dano em "+heroes_dict[str(p4)]+"! 💢")
						if survivors["p4_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p1
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1)+" de dano em "+heroes_dict[str(p5)]+"! 💢")
						if survivors["p5_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p1
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1)+" de dano em "+heroes_dict[str(p6)]+"! 💢")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p1_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p1)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p1)] +=10
					winners.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p2":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" se esquivou de "+heroes_dict[str(p1)]+"! 🛡")
					if pick_player == "p3":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" se esquivou de "+heroes_dict[str(p1)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" se esquivou de "+heroes_dict[str(p1)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" se esquivou de "+heroes_dict[str(p1)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" se esquivou de "+heroes_dict[str(p1)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p1*2
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1*2)+" de dano **crítico** em "+heroes_dict[str(p2)]+"! 💥")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p1*2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1*2)+" de dano **crítico** em "+heroes_dict[str(p3)]+"! 💥")
						if survivors["p3_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p1*2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1*2)+" de dano **crítico** em "+heroes_dict[str(p4)]+"! 💥")
						if survivors["p4_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p1*2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1*2)+" de dano **crítico** em "+heroes_dict[str(p5)]+"! 💥")
						if survivors["p5_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p1 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p1*2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" causou "+str(roll_damage_p1*2)+" de dano **crítico** em "+heroes_dict[str(p6)]+"! 💥")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p1)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p1_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p1)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p1)] +=15
					winners.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				await asyncio.sleep(2)

##################### P2 TURN
			if survivors["p2_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p2)
				pick_player = random.choice(p2_roll_survivors)


				roll_damage_p2 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2)+" de dano em "+heroes_dict[str(p1)]+"! 💢")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p1)+">. ❌")
							p2_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2)+" de dano em "+heroes_dict[str(p3)]+"! 💢")
						if survivors["p3_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2)+" de dano em "+heroes_dict[str(p4)]+"! 💢")
						if survivors["p4_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2)+" de dano em "+heroes_dict[str(p5)]+"! 💢")
						if survivors["p5_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2)+" de dano em "+heroes_dict[str(p6)]+"! 💢")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p2_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p2)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p2)] +=15
					losers.append(str(p1))
					winners.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p1":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" se esquivou de "+heroes_dict[str(p2)]+"! 🛡")
					if pick_player == "p3":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" se esquivou de "+heroes_dict[str(p2)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" se esquivou de "+heroes_dict[str(p2)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" se esquivou de "+heroes_dict[str(p2)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" se esquivou de "+heroes_dict[str(p2)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p2*2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2*2)+" de dano **crítico** em "+heroes_dict[str(p1)]+"! 💥")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p1)+">. ❌")
							p2_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p2*2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2*2)+" de dano **crítico** em "+heroes_dict[str(p3)]+"! 💥")
						if survivors["p3_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p2*2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2*2)+" de dano **crítico** em "+heroes_dict[str(p4)]+"! 💥")
						if survivors["p4_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p2*2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2*2)+" de dano **crítico** em "+heroes_dict[str(p5)]+"! 💥")
						if survivors["p5_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p2 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p2*2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" causou "+str(roll_damage_p2*2)+" de dano **crítico** em "+heroes_dict[str(p6)]+"! 💥")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p2)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p2)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)



				if len(p2_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p2)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p2)] +=15
					losers.append(str(p1))
					winners.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break
				await asyncio.sleep(2)

##################### P3 TURN
			if survivors["p3_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p3)
				pick_player = random.choice(p3_roll_survivors)


				roll_damage_p3 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p3
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3)+" de dano em "+heroes_dict[str(p2)]+"! 💢")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p3
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3)+" de dano em "+heroes_dict[str(p1)]+"! 💢")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p1)+">. ❌")
							p3_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p3
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3)+" de dano em "+heroes_dict[str(p4)]+"! 💢")
						if survivors["p4_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p3
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3)+" de dano em "+heroes_dict[str(p5)]+"! 💢")
						if survivors["p5_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p3
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3)+" de dano em "+heroes_dict[str(p6)]+"! 💢")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p3_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p3)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p3)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					winners.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p2":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" se esquivou de "+heroes_dict[str(p3)]+"! 🛡")
					if pick_player == "p1":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" se esquivou de "+heroes_dict[str(p3)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" se esquivou de "+heroes_dict[str(p3)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" se esquivou de "+heroes_dict[str(p3)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" se esquivou de "+heroes_dict[str(p3)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p3*2
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3*2)+" de dano **crítico** em "+heroes_dict[str(p2)]+"! 💥")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p3*2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3*2)+" de dano **crítico** em "+heroes_dict[str(p1)]+"! 💥")
						if survivors["p1_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p1)+">. ❌")
							p3_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p3*2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3*2)+" de dano **crítico** em "+heroes_dict[str(p4)]+"! 💥")
						if survivors["p4_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p3*2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3*2)+" de dano **crítico** em "+heroes_dict[str(p5)]+"! 💥")
						if survivors["p5_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p3 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p3*2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" causou "+str(roll_damage_p3*2)+" de dano **crítico** em "+heroes_dict[str(p6)]+"! 💥")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p3)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p3)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)



				if len(p3_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p3)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p3)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					winners.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break
				await asyncio.sleep(2)

##################### P4 TURN
			if survivors["p4_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p4)
				pick_player = random.choice(p4_roll_survivors)


				roll_damage_p4 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p4
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4)+" de dano em "+heroes_dict[str(p2)]+"! 💢")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p4
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4)+" de dano em "+heroes_dict[str(p3)]+"! 💢")
						if survivors["p3_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p4
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4)+" de dano em "+heroes_dict[str(p1)]+"! 💢")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p1)+">. ❌")
							p4_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p4
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4)+" de dano em "+heroes_dict[str(p5)]+"! 💢")
						if survivors["p5_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p4
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4)+" de dano em "+heroes_dict[str(p6)]+"! 💢")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p4_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p4)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p4)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					winners.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p2":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" se esquivou de "+heroes_dict[str(p4)]+"! 🛡")
					if pick_player == "p3":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" se esquivou de "+heroes_dict[str(p4)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" se esquivou de "+heroes_dict[str(p4)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" se esquivou de "+heroes_dict[str(p4)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" se esquivou de "+heroes_dict[str(p4)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p4*2
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4*2)+" de dano **crítico** em "+heroes_dict[str(p2)]+"! 💥")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p4*2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4*2)+" de dano **crítico** em "+heroes_dict[str(p3)]+"! 💥")
						if survivors["p3_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p4*2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4*2)+" de dano **crítico** em "+heroes_dict[str(p1)]+"! 💥")
						if survivors["p1_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p1)+">. ❌")
							p4_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p4*2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4*2)+" de dano **crítico** em "+heroes_dict[str(p5)]+"! 💥")
						if survivors["p5_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p4 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p4*2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" causou "+str(roll_damage_p4*2)+" de dano **crítico** em "+heroes_dict[str(p6)]+"! 💥")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p4)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p4)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)



				if len(p4_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p4)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p4)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					winners.append(str(p4))
					losers.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break
				await asyncio.sleep(2)

##################### P5 TURN
			if survivors["p5_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p5)
				pick_player = random.choice(p5_roll_survivors)


				roll_damage_p5 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p5
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5)+" de dano em "+heroes_dict[str(p2)]+"! 💢")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p5
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5)+" de dano em "+heroes_dict[str(p3)]+"! 💢")
						if survivors["p3_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p5
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5)+" de dano em "+heroes_dict[str(p4)]+"! 💢")
						if survivors["p4_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p5
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5)+" de dano em "+heroes_dict[str(p1)]+"! 💢")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p1)+">. ❌")
							p5_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p5
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5)+" de dano em "+heroes_dict[str(p6)]+"! 💢")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p1)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p5_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p5)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p5)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					winners.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p2":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" se esquivou de "+heroes_dict[str(p5)]+"! 🛡")
					if pick_player == "p3":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" se esquivou de "+heroes_dict[str(p5)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" se esquivou de "+heroes_dict[str(p5)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" se esquivou de "+heroes_dict[str(p5)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" se esquivou de "+heroes_dict[str(p5)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p5*2
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5*2)+" de dano **crítico** em "+heroes_dict[str(p2)]+"! 💥")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p5*2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5*2)+" de dano **crítico** em "+heroes_dict[str(p3)]+"! 💥")
						if survivors["p3_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p5*2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5*2)+" de dano **crítico** em "+heroes_dict[str(p4)]+"! 💥")
						if survivors["p4_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p5*2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5*2)+" de dano **crítico** em "+heroes_dict[str(p1)]+"! 💥")
						if survivors["p1_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p1)+">. ❌")
							p5_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							p6_roll_survivors.remove("p1")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p6_fatal"] == 1:
							roll_damage_p5 / 2 + 1
						survivors["p6_hp"] = survivors["p6_hp"] - roll_damage_p5*2
						if survivors["p6_hp"] < 0:
							survivors["p6_hp"] = 0
						if survivors["p6_hp"] < 50:
							p6_emoji_hp = damaged
						if survivors["p6_hp"] == 0:
							p6_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" causou "+str(roll_damage_p5*2)+" de dano **crítico** em "+heroes_dict[str(p6)]+"! 💥")
						if survivors["p6_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p5)+"> matou <@"+str(p6)+">. ❌")
							p1_roll_survivors.remove("p6")
							p3_roll_survivors.remove("p6")
							p4_roll_survivors.remove("p6")
							p5_roll_survivors.remove("p6")
							p2_roll_survivors.remove("p6")
							leaderboard_dict[str(p5)] +=3
							leaderboard_dict[str(p6)] -=3
							if leaderboard_dict[str(p6)] <0:
								leaderboard_dict[str(p6)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)



				if len(p5_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p5)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p5)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					winners.append(str(p5))
					losers.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if survivors["p1_hp"] <= 25 and survivors["p1_fatal"] == 0:
					damage_list_p1.append("crit")
					damage_list_p1.append("crit")

					survivors["p1_fatal"] += 1
				if survivors["p2_hp"] <= 25 and survivors["p2_fatal"] == 0:
					damage_list_p2.append("crit")
					damage_list_p2.append("crit")
					survivors["p2_fatal"] += 1
				if survivors["p3_hp"] <= 25 and survivors["p3_fatal"] == 0:
					damage_list_p3.append("crit")
					damage_list_p3.append("crit")
					survivors["p3_fatal"] += 1
				if survivors["p4_hp"] <= 25 and survivors["p4_fatal"] == 0:
					damage_list_p4.append("crit")
					damage_list_p4.append("crit")
					survivors["p4_fatal"] += 1
				if survivors["p5_hp"] <= 25 and survivors["p5_fatal"] == 0:
					damage_list_p5.append("crit")
					damage_list_p5.append("crit")
					survivors["p5_fatal"] += 1
				if survivors["p6_hp"] <= 25 and survivors["p6_fatal"] == 0:
					damage_list_p6.append("crit")
					damage_list_p6.append("crit")
					survivors["p6_fatal"] += 1

				await asyncio.sleep(2)

##################### P6 TURN
			if survivors["p6_hp"] > 0:
				hit_or_miss = random.choice(damage_list_p6)
				pick_player = random.choice(p6_roll_survivors)


				roll_damage_p6 = random.randint(1, 50)

				if hit_or_miss == "hit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p6
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6)+" de dano em "+heroes_dict[str(p2)]+"! 💢")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p6
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6)+" de dano em "+heroes_dict[str(p3)]+"! 💢")
						if survivors["p3_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p6
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6)+" de dano em "+heroes_dict[str(p4)]+"! 💢")
						if survivors["p4_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)

					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p6
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6)+" de dano em "+heroes_dict[str(p5)]+"! 💢")
						if survivors["p5_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p1":
						if survivors["p1_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p6
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6)+" de dano em "+heroes_dict[str(p1)]+"! 💢")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p1)+">. ❌")
							p6_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
				if len(p6_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p6)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p6)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					winners.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break

				if hit_or_miss == "miss":
					await asyncio.sleep(2)
					await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" não acertou nada! 🌬")
				if hit_or_miss == "dodged":
					await asyncio.sleep(2)
					if pick_player == "p2":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p2)]+" se esquivou de "+heroes_dict[str(p6)]+"! 🛡")
					if pick_player == "p3":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p3)]+" se esquivou de "+heroes_dict[str(p6)]+"! 🛡")
					if pick_player == "p4":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p4)]+" se esquivou de "+heroes_dict[str(p6)]+"! 🛡")
					if pick_player == "p5":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p5)]+" se esquivou de "+heroes_dict[str(p6)]+"! 🛡")
					if pick_player == "p6":
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p1)]+" se esquivou de "+heroes_dict[str(p6)]+"! 🛡")

				if hit_or_miss == "crit":
					if pick_player == "p2":
						if survivors["p2_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p2_hp"] = survivors["p2_hp"] - roll_damage_p6*2
						if survivors["p2_hp"] < 0:
							survivors["p2_hp"] = 0
						if survivors["p2_hp"] < 50:
							p2_emoji_hp = damaged
						if survivors["p2_hp"] == 0:
							p2_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6*2)+" de dano **crítico** em "+heroes_dict[str(p2)]+"! 💥")
						if survivors["p2_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p2)+">. ❌")
							p1_roll_survivors.remove("p2")
							p3_roll_survivors.remove("p2")
							p4_roll_survivors.remove("p2")
							p5_roll_survivors.remove("p2")
							p6_roll_survivors.remove("p2")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p2)] -=3
							if leaderboard_dict[str(p2)] <0:
								leaderboard_dict[str(p2)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p3":
						if survivors["p3_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p3_hp"] = survivors["p3_hp"] - roll_damage_p6*2
						if survivors["p3_hp"] < 0:
							survivors["p3_hp"] = 0
						if survivors["p3_hp"] < 50:
							p3_emoji_hp = damaged
						if survivors["p3_hp"] == 0:
							p3_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6*2)+" de dano **crítico** em "+heroes_dict[str(p3)]+"! 💥")
						if survivors["p3_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p3)+">. ❌")
							p1_roll_survivors.remove("p3")
							p2_roll_survivors.remove("p3")
							p4_roll_survivors.remove("p3")
							p5_roll_survivors.remove("p3")
							p6_roll_survivors.remove("p3")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p3)] -=3
							if leaderboard_dict[str(p3)] <0:
								leaderboard_dict[str(p3)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p4":
						if survivors["p4_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p4_hp"] = survivors["p4_hp"] - roll_damage_p6*2
						if survivors["p4_hp"] < 0:
							survivors["p4_hp"] = 0
						if survivors["p4_hp"] < 50:
							p4_emoji_hp = damaged
						if survivors["p4_hp"] == 0:
							p4_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6*2)+" de dano **crítico** em "+heroes_dict[str(p4)]+"! 💥")
						if survivors["p4_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p4)+">. ❌")
							p1_roll_survivors.remove("p4")
							p3_roll_survivors.remove("p4")
							p2_roll_survivors.remove("p4")
							p5_roll_survivors.remove("p4")
							p6_roll_survivors.remove("p4")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p4)] -=3
							if leaderboard_dict[str(p4)] <0:
								leaderboard_dict[str(p4)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p5":
						if survivors["p5_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p5_hp"] = survivors["p5_hp"] - roll_damage_p6*2
						if survivors["p5_hp"] < 0:
							survivors["p5_hp"] = 0
						if survivors["p5_hp"] < 50:
							p5_emoji_hp = damaged
						if survivors["p5_hp"] == 0:
							p5_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6*2)+" de dano **crítico** em "+heroes_dict[str(p5)]+"! 💥")
						if survivors["p5_hp"] == 0:

							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p5)+">. ❌")
							p1_roll_survivors.remove("p5")
							p3_roll_survivors.remove("p5")
							p4_roll_survivors.remove("p5")
							p2_roll_survivors.remove("p5")
							p6_roll_survivors.remove("p5")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p5)] -=3
							if leaderboard_dict[str(p5)] <0:
								leaderboard_dict[str(p5)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)


					if pick_player == "p6":
						if survivors["p1_fatal"] == 1:
							roll_damage_p6 / 2 + 1
						survivors["p1_hp"] = survivors["p1_hp"] - roll_damage_p6*2
						if survivors["p1_hp"] < 0:
							survivors["p1_hp"] = 0
						if survivors["p1_hp"] < 50:
							p1_emoji_hp = damaged
						if survivors["p1_hp"] == 0:
							p1_emoji_hp = ded
						await client.edit_message(surv_battle_log, heroes_dict[str(p1)]+" "+p1_emoji_hp+" "+str(survivors["p1_hp"])+" "+heroes_dict[str(p2)]+" "+p2_emoji_hp+" "+str(survivors["p2_hp"])+" "+heroes_dict[str(p3)]+" "+p3_emoji_hp+" "+str(survivors["p3_hp"])+" \n\n"+heroes_dict[str(p4)]+" "+p4_emoji_hp+" "+str(survivors["p4_hp"])+" "+heroes_dict[str(p5)]+" "+p5_emoji_hp+" "+str(survivors["p5_hp"])+" "+heroes_dict[str(p6)]+" "+p6_emoji_hp+" "+str(survivors["p6_hp"])+"\n\n📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(p6)]+" causou "+str(roll_damage_p6*2)+" de dano **crítico** em "+heroes_dict[str(p1)]+"! 💥")
						if survivors["p1_hp"] == 0:
							await client.send_message(ctx.message.channel, "<@"+str(p6)+"> matou <@"+str(p1)+">. ❌")
							p6_roll_survivors.remove("p1")
							p3_roll_survivors.remove("p1")
							p4_roll_survivors.remove("p1")
							p5_roll_survivors.remove("p1")
							p2_roll_survivors.remove("p1")
							leaderboard_dict[str(p6)] +=3
							leaderboard_dict[str(p1)] -=3
							if leaderboard_dict[str(p1)] <0:
								leaderboard_dict[str(p1)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)



				if len(p6_roll_survivors) ==0:
					await client.send_message(ctx.message.channel, "<@"+str(p6)+"> foi o sobrevivente! Use o comando `~flw menção` para chutar um dos perdedores.")
					leaderboard_dict[str(p6)] +=15
					losers.append(str(p1))
					losers.append(str(p2))
					losers.append(str(p3))
					losers.append(str(p4))
					losers.append(str(p5))
					winners.append(str(p6))
					battle_survival.clear()
					survivors.clear()
					survival_running.clear()
					votes.clear()
					battle_survival["teste"] = 0
					survivors["teste"] = 0
					break


@client.command(pass_context = True)
async def flw(ctx):
	if ctx.message.author.id in winners:
		member_id = re.sub("\D", "", ctx.message.content)
		if member_id in losers:
			await client.kick(discord.Server.get_member(ctx.message.server, member_id))
			winners.clear()
			losers.clear()
			return
		else:
			await client.send_message(ctx.message.channel, "**Este usuário não estava na sobrevivência.**")	
			
@client.command(pass_context=True, aliases=['attle_luck', 'TRY_MY_LUCK'])
async def try_my_luck(ctx):
	if ctx.message.author.id in leaderboard_dict:
		if leaderboard_dict[ctx.message.author.id] >= 30:
			if len(boss_running) == 0:
				player_id = ctx.message.author.id
				player = "<@"+str(ctx.message.author.id)+">"
				if str(ctx.message.author.id) not in heroes_dict:
					await client.send_message(ctx.message.channel, "Você não escolheu um emote ainda.")
					return
				if str(ctx.message.author.id) in boss_running:
					await client.send_message(ctx.message.channel, "**Você está em batalha, parceiro.**")
					return
				boss_running.append(ctx.message.author.id)
				battle_log = await client.say("**A batalha começará em breve.**")
				await asyncio.sleep(5)
				boss_id = boss_dict["bossId"]
				boss_emote = boss_dict["bossEmote"]
				boss_hp = 500
				player_hp = 100
				boss_fatal = 0
				player_fatal = 0
				healthy = "❤"
				damaged = "💔"
				ded = "🖤"
				log_icon = "#"
				boss_emoji_hp = healthy*3
				player_emoji_hp = healthy*3
				turn = 0

				await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+ boss_emote +"⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100")
				while boss_hp and player_hp > 0:
					damage_list_boss = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
					damage_list_player = ["hit", "miss", "hit", "miss", "hit", "miss", "hit", "miss", "miss", "crit", "dodged", "dodged", "hit", "dodged", "hit", "dodged", "hit", "dodged"]
					turn +=1

					await asyncio.sleep(2)

					hit_or_miss = random.choice(damage_list_boss)
					roll_damage_boss = random.randint(1, 50)


					if hit_or_miss == "hit":
						if player_fatal ==1:
							roll_damage_boss / 2 + 1
						player_hp = player_hp - roll_damage_boss
						if player_hp < 0:
							player_hp = 0
						if player_hp < 83:
							player_emoji_hp = healthy*2+damaged
						if player_hp < 67:
							player_emoji_hp = healthy*2+ded
						if player_hp < 51:
							player_emoji_hp = healthy+damaged+ded
						if player_hp < 35:
							player_emoji_hp = healthy+ded*2
						if player_hp < 19:
							player_emoji_hp = damaged+ded*2
						if player_hp == 0:
							player_emoji_hp = ded*3

						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" " +boss_emote+ "⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+boss_emote+ " causou "+str(roll_damage_boss)+" de dano! 💢")
						if player_hp == 0:
							if boss_hp == 500:
								await client.send_message(ctx.message.channel, player+" nem tentou. "+"<@"+boss_id+"> ainda é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] -=15
								leaderboard_dict[str(boss_id)] +=15
							else:
								await client.send_message(ctx.message.channel, player+" falhou. "+"<@"+boss_id+"> ainda é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] -=10
								leaderboard_dict[str(boss_id)] +=10
							if leaderboard_dict[str(ctx.message.author.id)] <0:
								leaderboard_dict[str(ctx.message.author.id)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
							with open('D:\\boss.json', 'w') as boss:
									json.dump(boss_dict, boss)
							boss_running.clear()
							break
					if hit_or_miss == "miss":
						await asyncio.sleep(2)
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+boss_emote+ " errou! 🌬")
					if hit_or_miss == "dodged":
						await asyncio.sleep(2)
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(player_id)]+" se esquivou! 🛡")
					if hit_or_miss == "crit":
						if player_fatal ==1:
							roll_damage_boss / 3 + 1
						player_hp = player_hp - roll_damage_boss*2
						if player_hp < 0:
							player_hp = 0
						if player_hp < 83:
							player_emoji_hp = healthy*2+damaged
						if player_hp < 67:
							player_emoji_hp = healthy*2+ded
						if player_hp < 51:
							player_emoji_hp = healthy+damaged+ded
						if player_hp < 35:
							player_emoji_hp = healthy+ded*2
						if player_hp < 19:
							player_emoji_hp = damaged+ded*2
						if player_hp == 0:
							player_emoji_hp = ded*3
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+boss_emote+ " causou "+str(roll_damage_boss*2)+" de dano **crítico**! 💥")
						if player_hp == 0:
							if boss_hp == 500:
								await client.send_message(ctx.message.channel, player+" nem tentou. "+"<@"+boss_id+"> ainda é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] -=15
								leaderboard_dict[str(boss_id)] +=15
							else:
								await client.send_message(ctx.message.channel, player+" falhou. "+"<@"+boss_id+"> ainda é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] -=10
								leaderboard_dict[str(boss_id)] +=10
							if leaderboard_dict[str(ctx.message.author.id)] <0:
								leaderboard_dict[str(ctx.message.author.id)] = 0
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
							with open('D:\\boss.json', 'w') as boss:
									json.dump(boss_dict, boss)
							boss_running.clear()
							break

					if boss_hp <= 125 and boss_fatal == 0:
						damage_list_player.append("dodged")
						damage_list_player.append("dodged")
						damage_list_player.append("dodged")
						damage_list_player.append("dodged")
						damage_list_boss.append("crit")

						boss_fatal += 1
					if player_hp <= 25 and player_fatal == 0:
						damage_list_boss.append("dodged")
						damage_list_boss.append("dodged")
						damage_list_boss.append("dodged")
						damage_list_boss.append("dodged")
						damage_list_player.append("crit")
						player_fatal += 1

					await asyncio.sleep(2)
					hit_or_miss = random.choice(damage_list_player)
					roll_damage_player = random.randint(1, 75)

					if hit_or_miss == "hit":
						if boss_fatal ==1:
							roll_damage_player / 2 + 1
						boss_hp = boss_hp - roll_damage_player
						if boss_hp < 0:
							boss_hp = 0
						if boss_hp < 415:
							boss_emoji_hp = damaged+healthy*2
						if boss_hp < 335:
							boss_emoji_hp = ded+healthy*2
						if boss_hp < 255:
							boss_emoji_hp = ded+damaged+healthy
						if boss_hp < 175:
							boss_emoji_hp = ded*2+healthy
						if boss_hp < 95:
							boss_emoji_hp = ded*2+damaged
						if boss_hp == 0:
							boss_emoji_hp = ded*3
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(player_id)]+" causou "+str(roll_damage_player)+" de dano! 💢")
						if boss_hp == 0:
							if player_hp == 100:
								await client.send_message(ctx.message.channel, player+" fez o impossível e derrotou o boss de P-E-R-F-E-C-T. Agora ele é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] +=200
								boss_dict["bossId"] = str(ctx.message.author.id)
								boss_dict["bossEmote"] = heroes_dict[str(player_id)]
							else:
								await client.send_message(ctx.message.channel, player+" derrotou o boss. Agora ele é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] +=100
								boss_dict["bossId"] = str(ctx.message.author.id)
								boss_dict["bossEmote"] = heroes_dict[str(player_id)]
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
							with open('D:\\boss.json', 'w') as boss:
									json.dump(boss_dict, boss)
							boss_running.clear()
							votes.clear()
							break
					if hit_or_miss == "miss":
						await asyncio.sleep(2)
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(player_id)]+" errou! 🌬")
					if hit_or_miss == "dodged":
						await asyncio.sleep(2)
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+boss_emote+ " se esquivou! 🛡")

					if hit_or_miss == "crit":
						if roll_damage_player > 25:
							roll_damage_player + 15
						if boss_fatal ==1:
							roll_damage_player / 3 + 1
						boss_hp = boss_hp - roll_damage_player*2
						if boss_hp < 0:
							boss_hp = 0
						if boss_hp < 415:
							boss_emoji_hp = damaged+healthy*2
						if boss_hp < 335:
							boss_emoji_hp = ded+healthy*2
						if boss_hp < 255:
							boss_emoji_hp = ded+damaged+healthy
						if boss_hp < 175:
							boss_emoji_hp = ded*2+healthy
						if boss_hp < 95:
							boss_emoji_hp = ded*2+damaged
						if boss_hp == 0:
							boss_emoji_hp = ded*3
						await client.edit_message(battle_log, str(boss_hp)+"/500\n"+boss_emoji_hp+" "+boss_emote+" ⚔ "+heroes_dict[str(player_id)]+" "+player_emoji_hp+"\n"+"                                                 "+str(player_hp)+"/100"+"\n\n"+"📋 Turno "+str(turn)+" "+log_icon*14+"\n\n"+heroes_dict[str(player_id)]+" causou "+str(roll_damage_player*2)+" de dano **crítico**! 💥")
						if boss_hp == 0:
							if player_hp == 100:
								await client.send_message(ctx.message.channel, player+" fez o impossível e derrotou o boss de P-E-R-F-E-C-T. Agora ele é o boss.") #player é para pingar mais rápido
								leaderboard_dict[str(ctx.message.author.id)] +=200
								boss_dict["bossId"] = str(ctx.message.author.id)
								boss_dict["bossEmote"] = heroes_dict[str(player_id)]
							else:
								await client.send_message(ctx.message.channel, player+" derrotou o boss. Agora ele é o boss.")
								leaderboard_dict[str(ctx.message.author.id)] +=100
								boss_dict["bossId"] = str(ctx.message.author.id)
								boss_dict["bossEmote"] = heroes_dict[str(player_id)]
							with open('D:\\leaderboard.json', 'w') as leaderboard:
									json.dump(leaderboard_dict, leaderboard)
							with open('D:\\boss.json', 'w') as boss:
									json.dump(boss_dict, boss)
							boss_running.clear()
							break
			else:
				await client.send_message(ctx.message.channel, "**Existe uma batalha em andamento.**")

		else:
			await client.send_message(ctx.message.channel, "**É necessário ter no mínimo 30 pontos para desafiar o boss.**")			
			
client.run('')			