import json
from do import do_sort_teams_by_rating_down
from check import check_if_lists_empty


async def edit_team_rating(team_info) -> bool:
    try:
        tournament_index = team_info['tournament_index']
        league_index = team_info['league_index']
        team_index = team_info['team_index']
        new_rating = team_info['new_rating']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
            	return False

            t_name = trmnts[tournament_index]['name']

            data['tournaments'][tournament_index]['leagues'][league_index]['score_top'][team_index]['rating'] = new_rating
            team_name = data['tournaments'][tournament_index]['leagues'][league_index]['score_top'][team_index]['name']

            for i, team in enumerate(data['tournaments'][tournament_index]['score_top']):
            	if team['name'] == team_name:
            		data['tournaments'][tournament_index]['score_top'][i]['rating'] = new_rating
            		break

            sorted_tourn_teams = await do_sort_teams_by_rating_down(data['tournaments'][tournament_index]['score_top'])
            sorted_league_teams = await do_sort_teams_by_rating_down(data['tournaments'][tournament_index]['leagues'][league_index]['score_top'])

            data['tournaments'][tournament_index]['score_top'] = sorted_tourn_teams
            data['tournaments'][tournament_index]['leagues'][league_index]['score_top'] = sorted_league_teams

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            return True
    except:
        return False


async def edit_league_coefficient(league_info) -> bool:
    try:
        tournament_index = league_info['tournament_index']
        league_index = league_info['league_index']
        new_coefficient = league_info['new_coefficient']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
            	return False

            data['tournaments'][tournament_index]['leagues'][league_index]['coefficient'] = new_coefficient

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            return True
    except:
        return False