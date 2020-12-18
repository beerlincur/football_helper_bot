import json
from typing import Tuple, Union, Dict
from check import check_if_lists_empty


async def do_parse_game_results(game_result: str) -> Tuple[float, float]:
    try:
        first, second = list(map(int, game_result.split()))
        
        return (0.5 if first == 0 else first, 0.5 if second == 0 else second)
    except:
        return (-1, -1)


async def do_enter_game_results_to_league(two_teams_info) -> Union[Dict[str, Union[float, str]], bool]:
    try:
        tournament_index = two_teams_info['tournament_index']
        league_index = two_teams_info['league_index']
        first_team_index = two_teams_info['first_team_index']
        second_team_index = two_teams_info['second_team_index']
        game_result = two_teams_info['game_result']

        first_scored, second_scored = await do_parse_game_results(game_result)

        if first_scored == -1:
            return False

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            try:
                is_empty = await check_if_lists_empty(data, tournament_index, league_index)

                if is_empty:
                    return False

                fisrt_team = data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][first_team_index]

                second_team =  data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][second_team_index]

                league_coefficient = data["tournaments"][tournament_index]['leagues'][league_index]['coefficient']

                f_cur_rating = round((fisrt_team['rating'] / fisrt_team['played_games']) if fisrt_team['played_games'] != 0 else fisrt_team['rating'], 2)
                s_cur_rating = round((second_team['rating'] / second_team['played_games']) if second_team['played_games'] != 0 else second_team['rating'], 2)
                
                # print("f_c_r", f_cur_rating)
                # print("==============")
                # print("s_c_r", s_cur_rating)
                # print("==============")
                
                f_t_r = round( ( ( ( ( (first_scored + second_scored) / second_scored ) + first_scored ) + (s_cur_rating / 2.0) ) * league_coefficient ), 2)
                
                # print("==============")
                # print("f_t_r", f_t_r)
                # print("==============")

                s_t_r = round( ( ( ( ( (second_scored + first_scored) / first_scored ) + second_scored ) + (f_cur_rating / 2.0) ) * league_coefficient ), 2)

                # print("s_t_r", s_t_r)
                # print("==============")

                data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][first_team_index]['played_games'] += 1
                data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][second_team_index]['played_games'] += 1

                data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][first_team_index]['rating'] += f_t_r

                data["tournaments"][tournament_index]['leagues'][league_index]['score_top'][second_team_index]['rating'] += s_t_r

                file.seek(0)
                file.write(json.dumps(data, ensure_ascii=False, indent=4))
                file.truncate()

                to_return = {
                    "tournament_index": tournament_index,
                    "name_f": fisrt_team['name'],
                    "name_s": second_team['name'],
                    "to_sum_f": f_t_r,
                    "to_sum_s": s_t_r,
                }
                
                return to_return
            except:
                return False
    except:
        return False


async def do_enter_game_results_to_tourn(changes) -> bool:
    try:
        tournament_index = changes['tournament_index']
        first_team_n = changes['name_f']
        second_team_n = changes['name_s']
        to_sum_f = changes['to_sum_f']
        to_sum_s = changes['to_sum_s']

        with open("tournaments.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            try:
                is_empty = await check_if_lists_empty(data, tournament_index)

                if is_empty:
                    return False

                for i, team in enumerate(data['tournaments'][tournament_index]['score_top']):
                    if team['name'] == first_team_n:
                        data['tournaments'][tournament_index]['score_top'][i]['played_games'] += 1

                        data['tournaments'][tournament_index]['score_top'][i]['rating'] += to_sum_f

                        continue

                    if team['name'] == second_team_n:
                        data['tournaments'][tournament_index]['score_top'][i]['played_games'] += 1

                        data['tournaments'][tournament_index]['score_top'][i]['rating'] += to_sum_s

                        continue

                file.seek(0)
                file.write(json.dumps(data, ensure_ascii=False, indent=4))
                file.truncate()

                return True
            except:
                return False
    except:
        return False


async def do_sort_teams_by_rating_down(teams_list):
    try:
        size = len(teams_list)
        maximum = 0

        for i in range(0, size - 1):
            maximum = i

            for j in range(i + 1, size):
                f_c_r = round(teams_list[j]['rating'] / teams_list[j]['played_games'] if teams_list[j]['played_games'] != 0 else teams_list[j]['rating'], 2)
                s_c_r = round(teams_list[maximum]['rating'] / teams_list[maximum]['played_games'] if teams_list[maximum]['played_games'] != 0 else teams_list[maximum]['rating'], 2)
                if f_c_r > s_c_r:
                    maximum = j

            teams_list[i], teams_list[maximum] = teams_list[maximum], teams_list[i]

        return teams_list 
    except:
        return False


async def do_open_for_sort(tournament_index: int, league_index: int) -> bool:
    try:
        with open("tournaments.json", "r+", encoding="utf-8") as file:
                data = json.load(file)
                try:
                    is_empty = await check_if_lists_empty(data, tournament_index, league_index)

                    if is_empty:
                        return False

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
    except:
        return False