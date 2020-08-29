import json
from typing import Dict, Union 
from do import do_sort_teams_by_rating_down
from config import BASE_RATING


async def add_tournament_to_json(tourn_data: Dict[str, Union[str, int]]) -> bool:
    try:
        new_t = {
            "name": tourn_data['name'],
            "leagues": [],
            "score_top": [],
        }

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            
            data["tournaments"].append(new_t)

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
            
            return True
    except:
        return False


async def add_league_to_tournament_json(league_data: Dict[str, Union[str, int]]) -> bool:
    try:
        new_l = {
            "name": league_data['name'],
            "coefficient": league_data['coefficient'],
            "score_top": [],
        }

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            
            tournament_index = league_data['tournament_index']

            data['tournaments'][tournament_index]['leagues'].append(new_l)

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
            
            return True
    except:
        return False


async def add_team_to_tournament_to_league_json(team_data: Dict[str, Union[str, int]]) -> bool:
    try:
        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            
            tournament_index = team_data['tournament_index']
            league_index = team_data['league_index']
            
            team_rating = team_data['rating']
            
            if team_data['rating'] == 0:
                team_rating = BASE_RATING * data['tournaments'][tournament_index]['leagues'][league_index]['coefficient']
            
            new_te = {
                "name": team_data['name'],
                "rating": team_rating,
                "played_games": 0
            }

            data['tournaments'][tournament_index]['score_top'].append(new_te)
            data['tournaments'][tournament_index]['leagues'][league_index]['score_top'].append(new_te)

            sorted_teams_tourn = await do_sort_teams_by_rating_down(data['tournaments'][tournament_index]['score_top'])
            sorted_teams_league = await do_sort_teams_by_rating_down(data['tournaments'][tournament_index]['leagues'][league_index]['score_top'])

            data['tournaments'][tournament_index]['score_top'] = sorted_teams_tourn
            data['tournaments'][tournament_index]['leagues'][league_index]['score_top'] = sorted_teams_league

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
            
            return True
    except:
        return False