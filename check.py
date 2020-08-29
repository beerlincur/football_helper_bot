def check_is_digit(string: str) -> bool:
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False



async def check_if_lists_empty(data, tournament_index: int = 0, league_index: int = 0) -> bool:
	try:
		if len(data['tournaments']) == 0:
			return True

		if tournament_index:
			
			if len(data['tournaments'][tournament_index]['leagues']) == 0:
				return True

			if league_index:
				if len(data['tournaments'][tournament_index]['leagues'][league_index]['score_top']) == 0:
					return True

		
		return False
	except:
		return True