from aiogram.dispatcher.filters.state import StatesGroup, State


# ================================================================================================== MODELS
class TournamentForm(StatesGroup):
    name = State()


class LeagueForm(StatesGroup):
    name = State()
    coefficient = State()
    tournament_index = State()


class TeamForm(StatesGroup):
    name = State()
    rating = State()
    tournament_index = State()
    league_index = State()


# ================================================================================================== SHOW
class ShowTeamsForm(StatesGroup):
	tournament_index = State()
	league_index = State()


class ShowLeaguesForm(StatesGroup):
	tournament_index = State()


class ShowTwoTeamsForm(StatesGroup):
	tournament_index = State()
	league_index = State()
	first_team_index = State()
	second_team_index = State()


class ShowTournTeamsForm(StatesGroup):
    tournament_index = State()


# ================================================================================================== ENTER GAME RESULTS
class EnterGameResultsForm(StatesGroup):
    tournament_index = State()
    league_index = State()
    first_team_index = State()
    second_team_index = State()
    game_result = State()


# ================================================================================================== EDIT
class EditLeagueCoefficientForm(StatesGroup):
    tournament_index = State()
    league_index = State()
    new_coefficient = State()


class EditTeamRatingForm(StatesGroup):
    tournament_index = State()
    league_index = State()
    team_index = State()
    new_rating = State()

# ================================================================================================== DELETE
class DeleteTeamForm(StatesGroup):
    tournament_index = State()
    league_index = State()
    team_index = State()
    confirm = State()


class DeleteLeagueForm(StatesGroup):
    tournament_index = State()
    league_index = State()
    confirm = State()


class DeleteTournamentForm(StatesGroup):
    tournament_index = State()
    confirm = State()