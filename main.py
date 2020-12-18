#|------------------------ IMPORTS -------------------|
import os
import re
from time import sleep
import logging
import asyncio

from random import randint as ri
from time import gmtime, strftime
from aiogram.types.message import ContentTypes
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import MAIN_KEYBOARD, MAIN_CANCEL, TOKEN, ADMINS_IDS, PROXIE_URL, PROXIE_AUTH, ADD_KEYBOARD, SHOW_KEYBOARD, EDIT_KEYBOARD, DELETE_KEYBOARD

from states import TournamentForm, LeagueForm, TeamForm, ShowTeamsForm, ShowLeaguesForm, ShowTwoTeamsForm, \
	EnterGameResultsForm, ShowTournTeamsForm, EditLeagueCoefficientForm, EditTeamRatingForm, DeleteTeamForm, DeleteLeagueForm, DeleteTournamentForm

from add import add_tournament_to_json, add_league_to_tournament_json, add_team_to_tournament_to_league_json

from do import do_enter_game_results_to_league, do_enter_game_results_to_tourn, do_open_for_sort

from get import get_tournaments_string, get_leagues_string, get_teams_string, get_two_teams_string, get_tourn_teams_string, \
	get_league, get_team, get_tournament

from check import check_is_digit

from edit import edit_league_coefficient, edit_team_rating

from delete_module import delete_team_from_json, delete_league_from_json, delete_tournament_from_json 


#|---------------------- CODE ------------------------|

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

storage = MemoryStorage()

#bot = Bot(token=TOKEN, proxy=PROXIE_URL, proxy_auth=PROXIE_AUTH)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage, loop=loop)


# ================================================================================================== СТАРТ
@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    start_text = """
Здравствуйте, я футбольный помощник!
    """
    await message.answer(start_text, reply_markup=MAIN_KEYBOARD)


# ================================================================================================== МЕНЮ
@dp.message_handler(lambda message: message.text.lower() == "добавление")
async def adding_button_menu(message: types.Message):
    await message.answer("Выберите, что добавить:", reply_markup=ADD_KEYBOARD)


@dp.message_handler(lambda message: message.text.lower() == "просмотр")
async def show_button_menu(message: types.Message):
    await message.answer("Выберите, что просмотреть:", reply_markup=SHOW_KEYBOARD)


@dp.message_handler(lambda message: message.text.lower() == "изменение")
async def edit_button_menu(message: types.Message):
    await message.answer("Выберите, что изменить:", reply_markup=EDIT_KEYBOARD)


@dp.message_handler(lambda message: message.text.lower() == "удаление")
async def delete_button_menu(message: types.Message):
    await message.answer("Выберите, что удалить:", reply_markup=DELETE_KEYBOARD)


@dp.message_handler(lambda message: message.text.lower() == "назад на главную")
async def back_button_menu(message: types.Message):
    await message.answer("Вы в главном меню:", reply_markup=MAIN_KEYBOARD)


# ================================================================================================== КОЛЛБЕКИ ВСЯКИЕ
@dp.callback_query_handler(lambda callback_query: True, state="*")
async def callbacks_handler(callback_query: types.CallbackQuery, state: FSMContext):

    if callback_query.data == "main_cancel":
        
        if state:
            await state.reset_state(with_data=False)
            await callback_query.message.answer("Вы отменили действие.", reply_markup=MAIN_KEYBOARD)

# ================================================================================================== ДОБАВИТЬ ТУРНИР
@dp.message_handler(lambda message: message.text.lower() == "добавить турнир")
async def add_tournament_handler(message: types.Message):
    if message.chat.id in ADMINS_IDS:
        await message.answer("Введите название турнира:", reply_markup=MAIN_CANCEL)
        await TournamentForm.name.set()
    else:
        return


@dp.message_handler(state=TournamentForm.name)
async def add_tournament_tourn_name(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text:
			await state.update_data(name=message.text)
			tournament_info = await state.get_data()
			is_added = await add_tournament_to_json(tournament_info)
			if is_added:
				await message.answer("Турнир был успешно добавлен! Теперь Вы можете добавить лиги!", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
			else:
				await message.answer("При добавлении турнира произошла ошибка", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите название турнира!", reply_markup=MAIN_CANCEL)
			await TournamentForm.name.set()
	else:
		return


# ================================================================================================== ДОБАВИТЬ ЛИГУ
@dp.message_handler(lambda message: message.text.lower() == "добавить лигу")
async def add_league_handler(message: types.Message):
    if message.chat.id in ADMINS_IDS:
        await message.answer("Введите название лиги:", reply_markup=MAIN_CANCEL)
        await LeagueForm.name.set()
    else:
        return


@dp.message_handler(state=LeagueForm.name)
async def add_league_league_name(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS_IDS:
        await state.update_data(name=message.text)
        await message.answer("Теперь введите коэффициент силы для этой лиги:", reply_markup=MAIN_CANCEL)
        await LeagueForm.coefficient.set()
    else:
        return


@dp.message_handler(state=LeagueForm.coefficient)
async def add_league_league_coefficient(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if check_is_digit(message.text):
			trmnts = await get_tournaments_string()
			if trmnts:
				await state.update_data(coefficient=float(message.text))
				await message.answer(trmnts)
				await message.answer("Выберите турнир для добавления лиги:\n(введите только цифру - номер турнира из списка)", reply_markup=MAIN_CANCEL)
				await LeagueForm.tournament_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число!", reply_markup=MAIN_CANCEL)
			await LeagueForm.coefficient.set()
	else:
		return


@dp.message_handler(state=LeagueForm.tournament_index)
async def add_league_tourn_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text)-1))
			league_info = await state.get_data()
			is_added = await add_league_to_tournament_json(league_info)
			if is_added:
				await message.answer("Лига была успешно добавлена! Теперь Вы можете добавить команды!", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
			else:
				await message.answer("При добавлении лиги произошла ошибка", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await LeagueForm.tournament_index.set()
	else:
		return


# ================================================================================================== ДОБАВИТЬ КОМАНДУ
@dp.message_handler(lambda message: message.text.lower() == "добавить команду")
async def add_team_handler(message: types.Message):
    if message.chat.id in ADMINS_IDS:
        await message.answer("Введите название команды:", reply_markup=MAIN_CANCEL)
        await TeamForm.name.set()
    else:
        return


@dp.message_handler(state=TeamForm.name)
async def add_team_team_name(message: types.Message, state: FSMContext):
    if message.chat.id in ADMINS_IDS:
        await state.update_data(name=message.text)
        await message.answer("Теперь введите рейтинг команды (если его нет, введите 0):", reply_markup=MAIN_CANCEL)
        await TeamForm.rating.set()
    else:
        return


@dp.message_handler(state=TeamForm.rating)
async def add_team_team_rating(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if check_is_digit(message.text):
			trmnts = await get_tournaments_string()
			if trmnts:
				await state.update_data(rating=float(message.text))
				await message.answer(trmnts)
				await message.answer("Выберите турнир для добавления команды:\n(введите только цифру - номер турнира из списка)", reply_markup=MAIN_CANCEL)
				await TeamForm.tournament_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число!", reply_markup=MAIN_CANCEL)
			await TeamForm.rating.set()
	else:
		return


@dp.message_handler(state=TeamForm.tournament_index)
async def add_team_tourn_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			leagues = await get_leagues_string(int(message.text) - 1)
			if leagues:
				await state.update_data(tournament_index=(int(message.text) - 1))
				await message.answer(leagues)
				await message.answer("Выберите лигу для добавления команды:\n(введите только цифру - номер лиги из списка)", reply_markup=MAIN_CANCEL)
				await TeamForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await TeamForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=TeamForm.league_index)
async def add_team_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			team_info = await state.get_data()
			is_added = await add_team_to_tournament_to_league_json(team_info)
			if is_added:
				await message.answer("Команда была успешно добавлена!", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо лиги под выбранным номером не существует,\nлибо произошла ошибка", reply_markup=MAIN_KEYBOARD)
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await TeamForm.league_index.set()
	else:
		return


# ================================================================================================== ПРОСМОТР
@dp.message_handler(lambda message: message.text.lower() == "турниры")
async def show_tournaments(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "лиги турнира")
async def show_leagues(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await ShowLeaguesForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=ShowLeaguesForm.tournament_index)
async def show_leagues_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await ShowLeaguesForm.tournament_index.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "команды лиги")
async def show_league_teams(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await ShowTeamsForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=ShowTeamsForm.tournament_index)
async def show_league_teams_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await ShowTeamsForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await ShowTeamsForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=ShowTeamsForm.league_index)
async def show_league_teams_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await ShowTeamsForm.league_index.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "команды турнира")
async def show_tourn_teams(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await ShowTournTeamsForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=ShowTournTeamsForm.tournament_index)
async def show_tourn_teams_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			tourn_teams_string = await get_tourn_teams_string(int(message.text) - 1)
			if tourn_teams_string:
				await message.answer(tourn_teams_string)
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await ShowTournTeamsForm.tournament_index.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "просмотреть пару команд")
async def show_two_teams(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await ShowTwoTeamsForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=ShowTwoTeamsForm.tournament_index)
async def show_two_teams_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await ShowTwoTeamsForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await ShowTwoTeamsForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=ShowTwoTeamsForm.league_index)
async def show_two_teams_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер первой команды для просмотра:", reply_markup=MAIN_CANCEL)
				await ShowTwoTeamsForm.first_team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await ShowTwoTeamsForm.league_index.set()
	else:
		return


@dp.message_handler(state=ShowTwoTeamsForm.first_team_index)
async def show_two_teams_first_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(first_team_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер второй команды для просмотра:", reply_markup=MAIN_CANCEL)
				await ShowTwoTeamsForm.second_team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер первой команды из списка!", reply_markup=MAIN_CANCEL)
			await ShowTwoTeamsForm.first_team_index.set()
	else:
		return


@dp.message_handler(state=ShowTwoTeamsForm.second_team_index)
async def show_two_teams_second_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(second_team_index=(int(message.text) - 1))
			two_teams_info = await state.get_data()
			two_teams_string = await get_two_teams_string(two_teams_info)
			if two_teams_string:
				await message.answer(two_teams_string)
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер второй команды из списка!", reply_markup=MAIN_CANCEL)
			await ShowTwoTeamsForm.second_team_index.set()
	else:
		return

# ================================================================================================== ИЗМЕНЕНИЕ
@dp.message_handler(lambda message: message.text.lower() == "изменить коэффициент силы лиги")
async def edit_league_coefficient_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await EditLeagueCoefficientForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=EditLeagueCoefficientForm.tournament_index)
async def edit_league_coefficient_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await EditLeagueCoefficientForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await EditLeagueCoefficientForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=EditLeagueCoefficientForm.league_index)
async def edit_league_coefficient_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			league_info = await state.get_data()
			league_string = await get_league(league_info)
			if league_string:
				await message.answer("Информация о лиге перед изменением коэффициента:")
				await message.answer(league_string)
				await message.answer("Теперь введите новый коэффициент силы для этой лиги:", reply_markup=MAIN_CANCEL)
				await EditLeagueCoefficientForm.new_coefficient.set()
			else:
				await message.answer("Либо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await EditLeagueCoefficientForm.league_index.set()
	else:
		return


@dp.message_handler(state=EditLeagueCoefficientForm.new_coefficient)
async def edit_league_coefficient_new_coefficient(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if check_is_digit(message.text):
			await state.update_data(new_coefficient=float(message.text))
			league_data = await state.get_data()
			is_changed = await edit_league_coefficient(league_data)
			if is_changed:
				await message.answer("Коэффициент силы лиги был успешно изменен!")
				await state.reset_state(with_data=False)
			else:
				await message.answer("При изменении коэффициента силы лиги произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - новый коэффициент силы лиги!", reply_markup=MAIN_CANCEL)
			await EditLeagueCoefficientForm.new_coefficient.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "изменить рейтинг команды")
async def edit_team_rating_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await EditTeamRatingForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=EditTeamRatingForm.tournament_index)
async def edit_team_rating_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await EditTeamRatingForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await EditTeamRatingForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=EditTeamRatingForm.league_index)
async def edit_team_rating_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер команды для изменения рейтинга:", reply_markup=MAIN_CANCEL)
				await EditTeamRatingForm.team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await EditTeamRatingForm.league_index.set()
	else:
		return


@dp.message_handler(state=EditTeamRatingForm.team_index)
async def edit_team_rating_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(team_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			team_string = await get_team(teams_info)
			if team_string:
				await message.answer(team_string)
				await message.answer("Теперь введите новый рейтинг для команды:", reply_markup=MAIN_CANCEL)
				await EditTeamRatingForm.new_rating.set()
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер необходимой команды из списка!", reply_markup=MAIN_CANCEL)
			await EditTeamRatingForm.team_index.set()
	else:
		return


@dp.message_handler(state=EditTeamRatingForm.new_rating)
async def edit_team_rating_new_rating(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if check_is_digit(message.text):
			await state.update_data(new_rating=float(message.text))
			team_info = await state.get_data()
			is_changed = await edit_team_rating(team_info)
			if is_changed:
				await message.answer("Рейтинг выбранной команды был успешно изменен!")
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - новый рейтинг для выбранной команды!", reply_markup=MAIN_CANCEL)
			await EditTeamRatingForm.new_rating.set()
	else:
		return

# ================================================================================================== УДАЛЕНИЕ
@dp.message_handler(lambda message: message.text.lower() == "удалить команду")
async def delete_team_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await DeleteTeamForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=DeleteTeamForm.tournament_index)
async def delete_team_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await DeleteTeamForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!")
			await DeleteTeamForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=DeleteTeamForm.league_index)
async def delete_team_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер команды для удаления:", reply_markup=MAIN_CANCEL)
				await DeleteTeamForm.team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await DeleteTeamForm.league_index.set()
	else:
		return


@dp.message_handler(state=DeleteTeamForm.team_index)
async def delete_team_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(team_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			team_string = await get_team(teams_info)
			if team_string:
				await message.answer(team_string)
				await message.answer("Введите 'Да', чтобы подтвердить удаление команды:", reply_markup=MAIN_CANCEL)
				await DeleteTeamForm.confirm.set()
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер необходимой команды из списка!", reply_markup=MAIN_CANCEL)
			await DeleteTeamForm.team_index.set()
	else:
		return


@dp.message_handler(state=DeleteTeamForm.confirm)
async def delete_team_confirmation(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.lower() == 'да':
			await state.update_data(confirm=message.text)
			team_info = await state.get_data()
			is_deleted = await delete_team_from_json(team_info)
			if is_deleted:
				await message.answer("Команда была успешно удалена!")
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите 'Да', для подтверждения удаления, либо нажмите кнопку отмены!", reply_markup=MAIN_CANCEL)
			await DeleteTeamForm.confirm.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "удалить лигу")
async def delete_league_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await DeleteLeagueForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=DeleteLeagueForm.tournament_index)
async def delete_league_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await DeleteLeagueForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!")
			await DeleteLeagueForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=DeleteLeagueForm.league_index)
async def delete_league_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			league_info = await state.get_data()
			league_string = await get_league(league_info)
			if league_string:
				await message.answer(league_string)
				await message.answer("Введите 'Да', чтобы подтвердить удаление лиги:", reply_markup=MAIN_CANCEL)
				await DeleteLeagueForm.confirm.set()
			else:
				await message.answer("Либо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await DeleteLeagueForm.league_index.set()
	else:
		return


@dp.message_handler(state=DeleteLeagueForm.confirm)
async def delete_league_confirmation(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.lower() == 'да':
			await state.update_data(confirm=message.text)
			league_info = await state.get_data()
			is_deleted = await delete_league_from_json(league_info)
			if is_deleted:
				await message.answer("Лига была успешно удалена!")
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите 'Да', для подтверждения удаления, либо нажмите кнопку отмены!", reply_markup=MAIN_CANCEL)
			await DeleteLeagueForm.confirm.set()
	else:
		return


@dp.message_handler(lambda message: message.text.lower() == "удалить турнир")
async def delete_tournament_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await DeleteTournamentForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=DeleteTournamentForm.tournament_index)
async def delete_tournament_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			tournament_string = await get_tournament((int(message.text) - 1))
			if tournament_string:
				await message.answer(tournament_string)
				await message.answer("Введите 'Да', чтобы подтвердить удаление турнира:", reply_markup=MAIN_CANCEL)
				await DeleteTournamentForm.confirm.set()
			else:
				await message.answer("Либо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!")
			await DeleteTournamentForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=DeleteTournamentForm.confirm)
async def delete_tournament_confirmation(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.lower() == 'да':
			await state.update_data(confirm=message.text)
			tournament_info = await state.get_data()
			is_deleted = await delete_tournament_from_json(tournament_info['tournament_index'])
			if is_deleted:
				await message.answer("Турнир была успешно удалена!")
				await state.reset_state(with_data=False)
			else:
				await message.answer("Либо турнира под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите 'Да', для подтверждения удаления, либо нажмите кнопку отмены!", reply_markup=MAIN_CANCEL)
			await DeleteTournamentForm.confirm.set()
	else:
		return
# ================================================================================================== ВВОД РЕЗУЛЬТАТОВ ИГРЫ
@dp.message_handler(lambda message: message.text.lower() == "ввести результаты игры")
async def enter_game_results_handler(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		tournaments_string = await get_tournaments_string()
		if tournaments_string:
			await message.answer(tournaments_string)
			await message.answer("Выберите номер турнира из списка:", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.tournament_index.set()
		else:
			await message.answer("Либо Вы еще не добавили ни одного турнира, либо произошла ошибка.")
			await state.reset_state(with_data=False)
	else:
		return


@dp.message_handler(state=EnterGameResultsForm.tournament_index)
async def enter_game_results_tournament_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(tournament_index=(int(message.text) - 1))
			leagues_string = await get_leagues_string((int(message.text) - 1))
			if leagues_string:
				await message.answer(leagues_string)
				await message.answer("Выберите номер лиги из списка:", reply_markup=MAIN_CANCEL)
				await EnterGameResultsForm.league_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной лиги в этот турнир,\nлибо турнира под выбранным номером не существует,\nлибо произошла ошибка.")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер турнира из списка!", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.tournament_index.set()
	else:
		return


@dp.message_handler(state=EnterGameResultsForm.league_index)
async def show_two_teams_league_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(league_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер первой команды для ввода результатов:", reply_markup=MAIN_CANCEL)
				await EnterGameResultsForm.first_team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер лиги из списка!", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.league_index.set()
	else:
		return


@dp.message_handler(state=EnterGameResultsForm.first_team_index)
async def show_two_teams_first_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(first_team_index=(int(message.text) - 1))
			teams_info = await state.get_data()
			teams_string = await get_teams_string(teams_info)
			if teams_string:
				await message.answer(teams_string)
				await message.answer("Выберите номер второй команды для ввода результатов:", reply_markup=MAIN_CANCEL)
				await EnterGameResultsForm.second_team_index.set()
			else:
				await message.answer("Либо Вы еще не добавили ни одной команды в эту лигу,\nлибо лиги под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер первой необходимой команды из списка!", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.first_team_index.set()
	else:
		return


@dp.message_handler(state=EnterGameResultsForm.second_team_index)
async def show_two_teams_second_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text.isdigit():
			await state.update_data(second_team_index=(int(message.text) - 1))
			two_teams_info = await state.get_data()
			two_teams_string = await get_two_teams_string(two_teams_info)
			if two_teams_string:
				await message.answer("Информация о командах перед вводом результатов:")
				await message.answer(two_teams_string)
				await message.answer("Теперь введите счет игры в формате *забитые первой командой*пробел*забитые второй командой*, например, 6 3 (обратите внимание, между числами должнен быть пробел)", reply_markup=MAIN_CANCEL)
				await EnterGameResultsForm.game_result.set()
			else:
				await message.answer("Либо команды под выбранным номером не существует,\nлибо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите число - номер второй необходимой команды из списка!", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.second_team_index.set()
	else:
		return


@dp.message_handler(state=EnterGameResultsForm.game_result)
async def show_two_teams_second_team_index(message: types.Message, state: FSMContext):
	if message.chat.id in ADMINS_IDS:
		if message.text:
			await state.update_data(game_result=message.text)
			two_teams_info = await state.get_data()
			changes_to_league = await do_enter_game_results_to_league(two_teams_info)
			changes_to_tourn = await do_enter_game_results_to_tourn(changes_to_league)

			if changes_to_league and changes_to_tourn:
				two_teams_string = await get_two_teams_string(two_teams_info)
				if two_teams_string:
					await message.answer("Информация о командах после ввода результатов игры:")
					await message.answer(two_teams_string)
					await do_open_for_sort(two_teams_info['tournament_index'], two_teams_info['league_index'])
					await state.reset_state(with_data=False)
				else:
					await message.answer("Либо команды под выбранным номером не существует, либо произошла ошибка")
					await state.reset_state(with_data=False)
			else:
				await message.answer("Либо команды под выбранным номером не существует, либо произошла ошибка")
				await state.reset_state(with_data=False)
		else:
			await message.answer("Введите счет игры в формате *забитые первой командой*пробел*забитые второй командой*, например, 6 3 (обратите внимание, между числами должнен быть пробел)!", reply_markup=MAIN_CANCEL)
			await EnterGameResultsForm.game_result.set()
	else:
		return
# ================================================================================================== ЗАПУСК
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)