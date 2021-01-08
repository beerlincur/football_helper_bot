import json
from typing import Union
from check import check_if_lists_empty


async def get_tournaments_string() -> Union[str, bool]:
    with open("tournaments.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        trmnts = data["tournaments"]
        try:
            is_empty = await check_if_lists_empty(data)

            if is_empty:
                return False

            result = "Турниры:\n\n"

            for i, t in enumerate(trmnts):
                name = t["name"]
                amount_of_leagues = len(t['leagues'])
                amount_of_teams = len(t['score_top'])

                result += f"{i+1}. {name}\nКол-во команд: {amount_of_teams}  Кол-во лиг: {amount_of_leagues}\n\n"
            
            return result
        except:
            return False


async def get_leagues_string(tournament_index: int) -> Union[str, bool]:
    with open("tournaments.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        trmnts = data["tournaments"]

        try:
            is_empty = await check_if_lists_empty(data, tournament_index)

            if is_empty:
                return False

            t_name = trmnts[tournament_index]['name']
            result = f"Лиги турнира {t_name}:\n\n"

            for j, l in enumerate(trmnts[tournament_index]['leagues']):
                name = l['name']
                amount_of_teams = len(l['score_top'])
                coefficient = l['coefficient']
                result += f"{j+1}. {name}\nКоэф. силы: {coefficient}  Кол-во команд: {amount_of_teams}\n\n"
            
            return result
        except:
            return False


async def get_teams_string(teams_info) -> Union[str, bool]:
    try:
        tournament_index = teams_info['tournament_index']
        league_index = teams_info['league_index']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
                return False

            t_name = trmnts[tournament_index]['name']
            l_name = trmnts[tournament_index]['leagues'][league_index]['name']
            l_coefficient = trmnts[tournament_index]['leagues'][league_index]['coefficient']

            result = f"Команды турнира {t_name}, лиги {l_name} (коэффициент силы - {l_coefficient}):\n\n"

            for k, team in enumerate(trmnts[tournament_index]['leagues'][league_index]['score_top']):
                team_name = team['name']
                team_rating = round(team['rating'] / team['played_games'] if team['played_games'] != 0 else team['rating'], 2)
                team_played_games = team['played_games']

                result += f"{k+1}. {team_name}\nРейтинг: {team_rating} ({team_played_games})\n\n"

            return result
    except:
        return False


async def get_tourn_teams_string(tournament_index: int) -> str:
    try:
        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index)

            if is_empty:
                return False

            t_name = trmnts[tournament_index]['name']

            result = f"Команды турнира {t_name}:\n\n"

            for k, team in enumerate(trmnts[tournament_index]['score_top']):
                team_name = team['name']
                team_rating = round(team['rating'] / team['played_games'] if team['played_games'] != 0 else team['rating'], 2)
                team_played_games = team['played_games']

                result += f"{k+1}. {team_name}\nРейтинг: {team_rating} ({team_played_games})\n\n"

            return result
    except:
        return False


async def get_two_teams_string(two_teams_info) -> Union[str, bool]:
    try:
        tournament_index = two_teams_info['tournament_index']
        league_index = two_teams_info['league_index']
        first_team_index = two_teams_info['first_team_index']
        second_team_index = two_teams_info['second_team_index']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            
            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
                return False

            first_team = data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][first_team_index]

            second_team =  data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][second_team_index]

            first_handicap = 0
            second_handicap = 0

            f_c_r = round(first_team['rating'] / first_team['played_games'] if first_team['played_games'] != 0 else first_team['rating'], 2)
            s_c_r = round(second_team['rating'] / second_team['played_games'] if second_team['played_games'] != 0 else second_team['rating'], 2)

            if f_c_r > s_c_r:
                second_handicap = int(f_c_r - s_c_r)
                
            elif f_c_r < s_c_r:
                first_handicap = int(s_c_r - f_c_r)

            tournament_name = data["tournaments"][tournament_index]['name']
            league_name = data["tournaments"][tournament_index]['leagues'][league_index]['name']
            l_coefficient = data["tournaments"][tournament_index]['leagues'][league_index]['coefficient']

            result = f"Команды турнира {tournament_name}, лиги {league_name} (коэффициент силы - {l_coefficient})\n\n"

            f_t_name = first_team['name']
            f_t_played_games = first_team['played_games']

            result += f"1. {f_t_name}\nРейтинг: {f_c_r} ({f_t_played_games}) Гандикап: {first_handicap}\n\n"

            s_t_name = second_team['name']
            s_t_played_games = second_team['played_games']

            result += f"2. {s_t_name}\nРейтинг: {s_c_r} ({s_t_played_games})  Гандикап: {second_handicap}\n\n"

            return result
    except:
        return False


async def get_tournament(tournament_index: int) -> Union[str, bool]:
    try:
        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data)

            if is_empty:
                return False

            t_name = trmnts[tournament_index]['name']
            amount_of_teams = len(trmnts[tournament_index]['score_top'])
            amount_of_leagues = len(trmnts[tournament_index]['leagues'])

            result = f"Турнир {t_name}]\nКол-во команд: {amount_of_teams}  Кол-во лиг: {amount_of_leagues}"

            return result
    except:
        return False


async def get_league(league_info) -> Union[str, bool]:
    try:
        tournament_index = league_info['tournament_index']
        league_index = league_info['league_index']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            trmnts = data["tournaments"]

            is_empty = await check_if_lists_empty(data, tournament_index, league_index)

            if is_empty:
                return False

            t_name = trmnts[tournament_index]['name']
            l_name = trmnts[tournament_index]['leagues'][league_index]['name']
            l_coefficient = trmnts[tournament_index]['leagues'][league_index]['coefficient']
            amount_of_teams = len(trmnts[tournament_index]['leagues'][league_index]['score_top'])

            result = f"Лига {l_name} (коэффициент силы - {l_coefficient}), турнира {t_name}\nКол-во команд: {amount_of_teams}"

            return result
    except:
        return False


async def get_team(team_info) -> Union[str, bool]:
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

            t_name = trmnts[tournament_index]['name']
            l_name = trmnts[tournament_index]['leagues'][league_index]['name']
            l_coefficient = trmnts[tournament_index]['leagues'][league_index]['coefficient']
            team_name = trmnts[tournament_index]['leagues'][league_index]['score_top'][team_index]['name']

            rating_t = trmnts[tournament_index]['leagues'][league_index]['score_top'][team_index]['rating']
            played_t = trmnts[tournament_index]['leagues'][league_index]['score_top'][team_index]['played_games']
            team_rating = round(rating_t / played_t if played_t != 0 else rating_t, 2)

            result = f"Команда {team_name} Рейтинг: {team_rating} ({played_t})\nИз лиги {l_name} (коэффициент силы - {l_coefficient}), турнира {t_name}"

            return result
    except:
        return False