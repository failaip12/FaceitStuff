from datetime import datetime
from faceit_api.faceit_data import FaceitData
from collections import OrderedDict
import plotly.express as px
import json
import requests

def v1api(player_id, game, page, size):
    api_url='https://api.faceit.com/stats/v1/stats/time/users/'
    api_url += "{}/games/{}?page={}&size={}".format(player_id, game, page, size)
    res = requests.get(api_url)
    if res.status_code == 200:
        return json.loads(res.content.decode('utf-8'))
    else:
        return None

def id_nr_match():
    faceit_data = FaceitData("YourAPIKey")
    player_name=input("Unesite username\n")
    player_id=faceit_data.player_details(nickname=player_name, game="csgo")['player_id']
    nrmatches=int(faceit_data.player_stats(player_id=player_id, game_id="csgo")['lifetime']['Matches'])
    return player_id, nrmatches

def match_list(nrmatches, player_id):
    matches=[]
    if(nrmatches<2000):
        matches=v1api(player_id, 'csgo', '0', '2000')
    else:
        for i in range(int(nrmatches/2000)+1):
            print(i)
            matches+=v1api(player_id, 'csgo', i, '2000')
    return matches

def WRv1():
    hours_and_won_matches={}
    hours_and_all_matches={}
    hours_and_win_rates={}
    player_id,nrmatches= id_nr_match()
    matches=match_list(nrmatches, player_id)
    all_matches=[]
    for i in range(len(matches)):
        try:
            elo_after=int(matches[i]['elo'])
            elo_before=int(matches[i+1]['elo'])
        except:
            continue
        if(elo_after>elo_before):
            all_matches.append(("W", datetime.fromtimestamp(int(str(matches[i]['updated_at'])[0:-3])).hour))
        elif(elo_after<elo_before):
            all_matches.append(("L", datetime.fromtimestamp(int(str(matches[i]['updated_at'])[0:-3])).hour))
    for match in all_matches:
        hours_and_won_matches[match[1]]=0
        hours_and_all_matches[match[1]]=0
    for hour in hours_and_won_matches:
        for match in all_matches:
            if hour==match[1]:
                if match[0]=="W":
                    hours_and_won_matches[hour]+=1
                hours_and_all_matches[hour]+=1
    ordered_hours_and_won_matches = OrderedDict(sorted(hours_and_won_matches.items()))
    ordered_hours_and_all_matches = OrderedDict(sorted(hours_and_all_matches.items()))
    for hour in ordered_hours_and_all_matches:
        hours_and_win_rates[hour]=ordered_hours_and_won_matches[hour]/ordered_hours_and_all_matches[hour]
    hour_list=[]
    WR_list=[]
    all_matches_list=[]
    for hour,match in ordered_hours_and_all_matches.items():
        all_matches_list.append(match)
    for hour,wr in hours_and_win_rates.items():
        hour_list.append(hour)
        WR_list.append(wr)
    fig = px.line_3d(x=hour_list, y=WR_list, z=all_matches_list)
    #fig = px.line(x=hour_list, y=all_matches_list)
    fig.show()

def GraphElo():
    elo_list=[]
    matches_list=[]
    player_id,nrmatches= id_nr_match()
    matches=match_list(nrmatches, player_id)
    i=nrmatches
    for match in matches:
        try:
            elo_list.append(int(match['elo']))
            matches_list.append(i)
            i-=1
        except:
            continue
    fig = px.line(x=matches_list, y=elo_list)
    fig.update_yaxes(range=[0, max(elo_list)])
    fig.show()

def main():
   GraphElo()

if __name__ == "__main__":
    main()
