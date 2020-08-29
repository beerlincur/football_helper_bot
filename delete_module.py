import json
from check import check_if_lists_empty


async def delete_team_from_json(team_info) -> bool:
    try:
        tournament_index = team_info['tournament_index']
        league_index = team_info['league_index']
        team_index = team_info['team_index']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
                return False

            team_name = data['tournaments'][tournament_index]['leagues'][league_index]['score_top'][team_index]['name']

            del data['tournaments'][tournament_index]['leagues'][league_index]['score_top'][team_index]

            for i, team in enumerate(data['tournaments'][tournament_index]['score_top']):
                if team['name'] == team_name:
                    del data['tournaments'][tournament_index]['score_top'][i]
                    break

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            return True
    except:
        return False


async def delete_league_from_json(league_info) -> bool:
    try:
        tournament_index = league_info['tournament_index']
        league_index = league_info['league_index']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index)

            if is_empty:
                return False

            league_name = data['tournaments'][tournament_index]['leagues'][league_index]['name']

            del data['tournaments'][tournament_index]['leagues'][league_index]

            for i, league in enumerate(data['tournaments'][tournament_index]['leagues']):
                if league['name'] == league_name:
                    del data['tournaments'][tournament_index]['leagues'][i]
                    break

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            return True
    except:
        return False


async def delete_tournament_from_json(tournament_index: int) -> bool:
    try:
        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data)

            if is_empty:
                return False

            del data['tournaments'][tournament_index]

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            return True
    except:
        return False