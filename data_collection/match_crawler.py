import sys
from RiotApiCalls import *
from championsRequest import *
from databaseQuries import *
import mysql.connector
import json
from config import *
import time
import requests
import traceback
import random

def Normalise(stri):
    stri = str(stri)
    stri = stri.replace('[', '').replace(']', '').replace("'", '').replace('(', '').replace(')', '').replace(",", '')
    return stri

config = {
    'user': 'league_user',
    'password': 'mysql',
    'host': 'localhost',
    'port': 3306,
    'database': 'LeagueStats',
    'buffered': True,
    'auth_plugin': 'mysql_native_password'
}

connection = mysql.connector.connect(**config)
cursor = connection.cursor(buffered=True)

RegionStart = "asia"
Region = "SG2"

def crawl_pipeline(start_match_id):
    match_queue = [start_match_id]
    processed_matches = set()

    while match_queue:
        MatchId = match_queue.pop(0)
        
        if MatchId in processed_matches:
            continue

        try:
            print(f"\n--- Processing Match: {MatchId} ---")
            
            MatchData_req = requests.get(
                "https://sea.api.riotgames.com/lol/match/v5/matches/" + MatchId + "?api_key=" + api_key
            )
            
            if MatchData_req.status_code == 429:
                print("Rate limit hit! Sleeping for 30s...")
                time.sleep(30)
                match_queue.append(MatchId)
                continue
                
            MatchData = MatchData_req.json()
            info = MatchData.get('info')
            
            if not info:
                # เพิ่ม Print ตรงนี้ เพื่อดูว่า Riot API ด่าเราว่าอะไร
                print(f"ดึงข้อมูลไม่สำเร็จ API ตอบกลับมาว่า: {MatchData}")
                
                # ถ้านี่เป็นแมตช์สุดท้ายในคิวแล้วมันพัง ให้หยุดโปรแกรม
                if len(match_queue) == 0:
                    print("คิวว่างเปล่า โปรแกรมหยุดทำงาน กรุณาเปลี่ยน Match ID ตั้งต้นใหม่")
                continue

            Patch = info['gameVersion']
            
            # --- กรองเฉพาะ Patch 16.4 และ 16.5 ---
            valid_patches = ("16.4", "16.04", "16.5", "16.05",'16.6','16.06')
            if not Patch.startswith(valid_patches):
                print(f"Skipping match (Wrong Patch): {Patch}")
                save_match = False
            else:
                save_match = True

            if save_match:
                cursor.execute("SELECT `MatchFk` FROM `TeamMatchTbl` WHERE `MatchFk` = (%s)", (str(MatchId),))
                matchCheck = cursor.fetchone()

                if matchCheck == None:
                    print(f"Match is Patch {Patch}. Fetching 10-min Timeline...")
                    
                    timeline_url = f"https://sea.api.riotgames.com/lol/match/v5/matches/{MatchId}/timeline?api_key={api_key}"
                    timeline_req = requests.get(timeline_url)
                    
                    if timeline_req.status_code == 429:
                        print("Rate limit hit on Timeline! Sleeping for 30s...")
                        time.sleep(30)
                        match_queue.append(MatchId)
                        continue
                        
                    timeline_data = timeline_req.json()
                    frames = timeline_data.get('info', {}).get('frames', [])

                    # หากเกมจบก่อน 10 นาที (Remake) ให้ข้าม
                    if len(frames) <= 10:
                        print("Game ended before 10 minutes. Skipping save.")
                        processed_matches.add(MatchId)
                        continue

                    # ==========================================
                    # 1. คำนวณ Events ทั้งหมดในช่วง 10 นาทีแรก
                    # ==========================================
                    p_kda = {str(i): {'k': 0, 'd': 0, 'a': 0, 'dragon': 0, 'baron': 0} for i in range(1, 11)}
                    team_obj = {
                        100: {'baron': 0, 'dragon': 0, 'herald': 0, 'tower': 0, 'kills': 0},
                        200: {'baron': 0, 'dragon': 0, 'herald': 0, 'tower': 0, 'kills': 0}
                    }

                    for f_idx in range(11): # นาทีที่ 0 ถึง 10
                        for event in frames[f_idx].get('events', []):
                            e_type = event.get('type')
                            
                            if e_type == 'CHAMPION_KILL':
                                killer = str(event.get('killerId', 0))
                                victim = str(event.get('victimId', 0))
                                
                                if killer in p_kda: p_kda[killer]['k'] += 1
                                if victim in p_kda: p_kda[victim]['d'] += 1
                                
                                # นับ Team Kills
                                killer_team = 100 if int(killer) <= 5 else 200
                                team_obj[killer_team]['kills'] += 1
                                
                                for assist_id in event.get('assistingParticipantIds', []):
                                    a_id = str(assist_id)
                                    if a_id in p_kda: p_kda[a_id]['a'] += 1
                                    
                            elif e_type == 'ELITE_MONSTER_KILL':
                                killer_team = event.get('killerTeamId')
                                killer_id = str(event.get('killerId', 0))
                                if not killer_team and event.get('killerId', 0) > 0:
                                    killer_team = 100 if int(killer_id) <= 5 else 200
                                    
                                m_type = event.get('monsterType')
                                if m_type == 'DRAGON':
                                    if killer_team in team_obj: team_obj[killer_team]['dragon'] += 1
                                    if killer_id in p_kda: p_kda[killer_id]['dragon'] += 1
                                elif m_type == 'RIFTHERALD' or m_type == 'HORDE': # เก็บ Voidgrubs รวมในช่อง Herald
                                    if killer_team in team_obj: team_obj[killer_team]['herald'] += 1
                                elif m_type == 'BARON_NASHOR':
                                    if killer_team in team_obj: team_obj[killer_team]['baron'] += 1
                                    
                            elif e_type == 'BUILDING_KILL':
                                # ถ้าตึกถูกทำลาย แปลว่าอีกทีมเป็นคนได้ (ถ้า TeamId ตึกคือ 100 แปลว่าทีม 200 ได้ TowerKill)
                                building_team = event.get('teamId')
                                killer_team = 200 if building_team == 100 else 100
                                if event.get('buildingType') == 'TOWER_BUILDING':
                                    team_obj[killer_team]['tower'] += 1

                    # ==========================================
                    # 2. จัดเตรียมข้อมูลทีม (TeamMatchTbl)
                    # ==========================================
                    ii = 0
                    champList = []
                    while ii < 10:
                        champion = info['participants'][ii]['championName']
                        cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (champion,))
                        Champion = cursor.fetchone()
                        Champion = Normalise(Champion)
                        Champion = int(Champion) if (Champion != "" and Champion != "None") else 0
                        champList.append(Champion)
                        ii += 1

                    # บันทึก MatchTbl หลักก่อน
                    GameType = info['gameMode']
                    GameDuration = info['gameDuration']
                    RankId = 1
                    cursor.execute("INSERT IGNORE INTO `MatchTbl`(`MatchId`, `Patch`,  `QueueType`, `RankFk`,`GameDuration`) VALUES (%s ,%s , %s , %s, %s)", 
                                   (MatchId, Normalise(Patch), Normalise(GameType), int(RankId), int(GameDuration)))
                    connection.commit()

                    # Insert ข้อมูลทีมตอน 10 นาทีลงตารางเดิม!
                    cursor.execute("""INSERT INTO `TeamMatchTbl`(`MatchFk`, `B1Champ`, `B2Champ`, `B3Champ`, `B4Champ`, `B5Champ`, `R1Champ`, `R2Champ`, `R3Champ`, `R4Champ`, `R5Champ`, 
                                   `BlueBaronKills`, `BlueRiftHeraldKills`, `BlueDragonKills`, `BlueTowerKills`, `BlueKills`, 
                                   `RedBaronKills`, `RedRiftHeraldKills`, `RedDragonKills`, `RedTowerKills`, `RedKills`, `RedWin`, `BlueWin`) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                   (MatchId, champList[0], champList[1], champList[2], champList[3], champList[4], 
                                    champList[5], champList[6], champList[7], champList[8], champList[9], 
                                    team_obj[100]['baron'], team_obj[100]['herald'], team_obj[100]['dragon'], team_obj[100]['tower'], team_obj[100]['kills'], 
                                    team_obj[200]['baron'], team_obj[200]['herald'], team_obj[200]['dragon'], team_obj[200]['tower'], team_obj[200]['kills'], 
                                    int(info['teams'][1]['win']), int(info['teams'][0]['win'])))

                    # ==========================================
                    # 3. จัดเตรียมข้อมูลผู้เล่น (MatchStatsTbl) - ยัดสถิติ 10 นาทีลงช่องเดิม
                    # ==========================================
                    for i in range(10):
                        p = info['participants'][i]
                        participantId = str(p['participantId'])
                        summonerName = p['summonerName']

                        cursor.execute("INSERT IGNORE INTO `SummonerUserTbl`(`SummonerName`) VALUES (%s )", (summonerName,))
                        cursor.execute("SELECT `SummonerID` FROM `SummonerUserTbl` WHERE `SummonerName` = (%s)", (summonerName ,))
                        SummonerID = cursor.fetchone()
                        SummonerID = int(Normalise(SummonerID))

                        Champion = champList[i]
                        cursor.execute("INSERT INTO `SummonerMatchTbl`(`SummonerFk`, `MatchFk`, `ChampionFk`) VALUES (%s , %s , %s)", (SummonerID, MatchId, Champion))
                        SummMatchId = cursor.lastrowid

                        # ---- สกัดสถิติ 10 นาที จาก Frame ----
                        frame_10 = frames[10]['participantFrames'].get(participantId, {})
                        dmg_stats = frame_10.get('damageStats', {})
                        
                        # ยัดลงตัวแปรเดิมที่คุณเคยตั้งไว้
                        cs = frame_10.get('minionsKilled', 0) + frame_10.get('jungleMinionsKilled', 0)
                        dmgDealt = dmg_stats.get('totalDamageDoneToChampions', 0)
                        dmgTaken = dmg_stats.get('totalDamageTaken', 0)
                        goldEarned = frame_10.get('totalGold', 0)
                        TurretDmgDealt = 0 # 10 นาทีแรกข้ามไปก่อน หรือใส่ 0 ไว้
                        
                        kills = p_kda[participantId]['k']
                        deaths = p_kda[participantId]['d']
                        assists = p_kda[participantId]['a']
                        dragonKills = p_kda[participantId]['dragon']
                        baronKills = p_kda[participantId]['baron']

                        # ข้อมูลพื้นฐานที่คงเดิม
                        win = p['win']
                        Role = p['lane']
                        spell1 = p['summoner1Id']
                        spell2 = p['summoner2Id']
                        masteryPoints = 0
                        visionScore = p.get('visionScore', 0) # ใช้ Vision ทั้งเกมเป็นตัวอ้างอิง
                        
                        support_champs = [412, 350, 117, 235, 497, 111, 99, 267, 43, 53, 555, 25, 1, 22, 16, 89, 101, 12, 143, 40, 147, 37, 26, 888, 50, 432, 32, 63, 74, 201, 29, 161, 44, 526, 57, 518]
                        if int(Champion) in support_champs and Role == "BOTTOM" and cs < 75:
                            Role = "SUPPORT"

                        Item1, Item2, Item3, Item4, Item5, Item6 = p['item0'], p['item1'], p['item2'], p['item3'], p['item4'], p['item5']

                        PK1 = p['perks']['styles'][0]['selections'][0]['perk']
                        PK2 = p['perks']['styles'][0]['selections'][1]['perk']
                        PK3 = p['perks']['styles'][0]['selections'][2]['perk']
                        PK4 = p['perks']['styles'][0]['selections'][3]['perk']
                        SK1 = p['perks']['styles'][1]['selections'][0]['perk']
                        SK2 = p['perks']['styles'][1]['selections'][1]['perk']
                        
                        EmemyLane = "None"
                        for opp in info['participants']:
                            if opp['lane'] == Role and opp['teamId'] != p['teamId']:
                                EmemyLane = opp['championName']
                                break

                        cursor.execute("SELECT `ChampionId` FROM `ChampionTbl` WHERE `ChampionName` = (%s)", (EmemyLane, ))
                        Enemy = cursor.fetchone()
                        Enemy = Normalise(Enemy)
                        Enemy = int(Enemy) if (Enemy != "" and Enemy != "None") else 0

                        # Insert โดยใช้ตารางเดิม โครงสร้างเดิม 100%
                        query = """INSERT INTO `MatchStatsTbl`
                        (`SummonerMatchFk`, `MinionsKilled`, `DmgDealt`, `DmgTaken`, `TurretDmgDealt`,
                        `TotalGold`, `Lane`, `Win`, `item1`, `item2`, `item3`, `item4`, `item5`, `item6`,
                        `kills`, `deaths`, `assists`, `PrimaryKeyStone`, `PrimarySlot1`, `PrimarySlot2`,
                        `PrimarySlot3`, `SecondarySlot1`, `SecondarySlot2`, `SummonerSpell1`,
                        `SummonerSpell2`, `CurrentMasteryPoints`, `EnemyChampionFk`, `DragonKills`, `BaronKills`, `visionScore`)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                        
                        values = (SummMatchId, cs, dmgDealt, dmgTaken, TurretDmgDealt, goldEarned, Role, win,
                            Item1, Item2, Item3, Item4, Item5, Item6, kills, deaths, assists, PK1, PK2,
                            PK3, PK4, SK1, SK2, spell1, spell2, masteryPoints, Enemy, dragonKills, baronKills, visionScore)

                        cursor.execute(query, values)

                    connection.commit()
                    print(f"Successfully saved 10-MIN DATA to Database! (Patch 16.04/16.05)")
                    
                else:
                    print("Match already in DB. Moving on...")

            # --- หาแมตช์ใหม่ต่อไป ---
            selected_puuids = random.sample(MatchData['metadata']['participants'], 2)
            for puuid in selected_puuids:
                list_url = f"https://sea.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5&api_key={api_key}"
                new_matches = requests.get(list_url).json()
                if isinstance(new_matches, list):
                    for m in new_matches:
                        if m not in processed_matches:
                            match_queue.append(m)
                time.sleep(1.5)
                
            processed_matches.add(MatchId)
            print(f"Queue remaining: {len(match_queue)}")

        except Exception as e:
            print(f"Error in Pipeline: {e}")
            traceback.print_exc()
            time.sleep(5)

if __name__ == "__main__":
    crawl_pipeline("SG2_139856327")