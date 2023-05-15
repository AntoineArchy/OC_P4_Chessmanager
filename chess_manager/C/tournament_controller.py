from __future__ import annotations

from functools import partial
from typing import Dict, Callable, List, Tuple

from core import messenger, mainview, tinydb_loader
from data import config

from chess_manager.M import tournament_model, player_model, turn_model
from chess_manager.V import tournament_view

DB_NAME = config.TOURNAMENT_DB_NAME


def _get_tournament_display(tournament: tournament_model.TournamentM) -> str:
    tournament_print = tournament_view.tournament_obj_view(tournament)
    return tournament_print


def _get_new_tournament_creation_data(main_view: mainview.MainView) -> Dict:
    form = tournament_view.tournament_creation_form()
    validators = tournament_model.TOURNAMENT_FORM_VALIDATOR
    form_answer = main_view.get_form_answer(form, validators)
    return form_answer


def _order_tournament_by_tournament_id(tournament_list: List) -> List:
    return sorted(tournament_list, key=lambda tournament_obj: tournament_obj.tournament_id, reverse=True)


def _order_tournament_by_status(tournament_list: List) -> List:
    """Reçoit une liste de match non ordonnée, retourne une liste de match en cours puis terminé"""
    unfinished = [tournament for tournament in tournament_list if tournament.end_date is None]
    finished = [tournament for tournament in tournament_list if tournament not in unfinished]

    unfinished = _order_tournament_by_tournament_id(unfinished)
    finished = _order_tournament_by_tournament_id(finished)
    return [*unfinished, *finished]


class TournamentC:
    def __init__(self,
                 loader: tinydb_loader.TinyDBLoader,
                 main_view: mainview.MainView,
                 app_messenger: messenger.Messenger) -> None:

        self.main_view = main_view
        self.loader = loader
        self.app_messenger = app_messenger

        app_messenger.register_call_event(config.AppInput.NEW_TOURNAMENT, self.create_new_tournament,
                                          "Create new tournament")
        app_messenger.register_call_event(config.AppInput.VIEW_TOURNAMENT_LIST, self.show_tournament_selection_list,
                                          "View tournament listing")
        app_messenger.register_call_event(config.AppInput.RESUME_TOURNAMENT, self.start_or_resume_tournament,
                                          "Start / Resume tournament")
        app_messenger.register_call_event(config.AppInput.SET_TOURNAMENT_ACTIV, self.set_tournament_as_active,
                                          "Back to tournament menu")
        app_messenger.register_call_event(config.AppInput.BACK_TO_TOURNAMENT_LIST, self.show_tournament_selection_list,
                                          "Back to tournament list")
        app_messenger.register_call_event(config.AppInput.NEXT_TURN, self.go_to_next_turn,
                                          "Go to next turn")
        app_messenger.register_call_event(config.AppInput.TOURNAMENT_RANKING, self.view_tournament_leaderboard,
                                          "View full tournament ranking")
        app_messenger.register_call_event(config.AppInput.TOURNAMENT_DETAILS, self.view_tournament_details,
                                          "View full tournament details")
        app_messenger.register_call_event(config.AppInput.BACK_TO_TURN_LIST, self.switch_to_turn_control,
                                          "Back to turn list")

    def save_tournament(self, tournament_obj: tournament_model.TournamentM) -> None:
        # EDGE CASE : User can finish the last match and quit the app without generating
        # next turn or checking tournament completion.
        # Checking here allow to properly set the end time.
        if tournament_obj.is_finished and tournament_obj.end_date is None:
            tournament_obj.end_tournament()
        tournament_obj.tournament_id = self.loader.save_tournament(tournament_obj.from_obj_to_dict())

    def display_tournament(self, tournament_obj: tournament_model.TournamentM) -> None:
        self.save_tournament(tournament_obj)
        self.main_view.add_to_display(_get_tournament_display(tournament_obj))


    def get_tournament_controls(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, génère et déclare comme disponible auprès du messenger de l'application les
        différents événements liés à la gestion de cet objet tournoi en fonction de ses différents paramètres
        """
        self.main_view.menu_title = "Tournament management"

        self.app_messenger.ignore_all()

        # Si les joueurs ne sont pas tous renseignés, on permet d'en ajouter au tournoi
        if len(tournament_obj.players) < tournament_obj.player_nbr:
            self.update_available_p_list(tournament_obj)

        # Si on a tous les joueurs, mais que le tournoi n'est pas terminé, on permet à l'utilisateur de le reprendre
        if len(tournament_obj.players) == tournament_obj.player_nbr and not tournament_obj.is_finished:
            self.app_messenger.accept_event(config.AppInput.RESUME_TOURNAMENT, event_arg=[tournament_obj])

        # Si le tournoi est terminé, impossible d'aller au tour suivant
        if tournament_obj.is_finished:
            tournament_obj.end_tournament()
            self.app_messenger.ignore_event(config.AppInput.NEXT_TURN)

        self.app_messenger.accept_event(config.AppInput.PLAYER_FLAT_VIEW)

        # Si on a joué au moins un tour du tournoi, on affiche le podium et autorise l'affichage des 'stats'.
        if tournament_obj.turn_list:
            self.app_messenger.accept_event(config.AppInput.DISPLAY_TURN_RANKING)
            self.app_messenger.send_event(config.AppInput.DISPLAY_TURN_RANKING, [tournament_obj.turn_list[-1], 3])
            self.app_messenger.accept_event(config.AppInput.TOURNAMENT_DETAILS, [tournament_obj])
            self.app_messenger.accept_event(config.AppInput.TOURNAMENT_RANKING, [tournament_obj])
        # Quoi qu'il arrive, on permet la visualisation des joueurs et des fonctions basiques de l'application
        self.app_messenger.accept_event(config.AppInput.VIEW_PLAYER_LIST, [tournament_obj.players])
        self.app_messenger.accept_event(config.AppInput.BACK_TO_TOURNAMENT_LIST)
        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

    def update_available_p_list(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi dont tous les joueurs ne sont pas renseigné et génère les événements permettant
        l'ajout de nouveau joueurs
        """
        new_args = [None, [player.player_id for player in tournament_obj.players],
                    10, 0,
                    partial(self.add_player_to_tournament, tournament_obj=tournament_obj)]

        add_to_this_tournament_func = self.app_messenger.update_event(config.AppInput.ADD_PLAYER,
                                                                      new_func_arg=new_args,
                                                                      make_copy=True)

        self.app_messenger.accept_event(config.AppInput.ADD_PLAYER, call_event=add_to_this_tournament_func)

    def create_new_tournament(self) -> None:
        """
        Permet la création d'un nouvel objet tournoi en fonction des réponses de l'utilisateur au formulaire de
        création de tournoi
        Assigne le tournoi nouvellement créé comme 'actif'.
        """
        self.main_view.menu_title = "## Tournament creation ##"

        tournament_data = _get_new_tournament_creation_data(self.main_view)
        tournament_data['turn_nbr'] = int(tournament_data['turn_nbr'])
        tournament_data['player_nbr'] = int(tournament_data['player_nbr'])
        new_tournament = tournament_model.TournamentM(**tournament_data)
        self.save_tournament(new_tournament)

        self.set_tournament_as_active(new_tournament)

    def add_player_to_tournament(self,
                                 player_obj: player_model.PlayerM,
                                 tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet joueur et un objet tournoi, ajoute le joueur au tournoi si c'est possible, affiche le tournoi,
        affiche le joueur, retourne au menu du tournoi si tous les joueurs sont présents sinon reste sur la page
        d'ajout de joueurs
        """
        self.app_messenger.accept_event(config.AppInput.PLAYER_FLAT_VIEW)

        if len(tournament_obj.players) >= tournament_obj.player_nbr:
            return

        if player_obj not in tournament_obj.players:
            tournament_obj.players.append(player_obj)
        self.display_tournament(tournament_obj)

        player_event = self.app_messenger.send_event(config.AppInput.PLAYER_FLAT_VIEW, [player_obj])
        self.app_messenger.ignore_event(player_event)
        if len(tournament_obj.players) == tournament_obj.player_nbr:
            self.get_tournament_controls(tournament_obj)
        tournament_obj.players.sort(key=lambda individual_player_obj: f"{individual_player_obj.get_alphab_sort()}")
        self.save_tournament(tournament_obj)

    def load_tournament_by_tournament_id(self,
                                         tournament_id: int,
                                         partial_load: bool = False) -> tournament_model.TournamentM:
        """
        Reçoit un tournament_id et le charge partiellement ou non en fonction de l'argument reçu. Si rien n'est
        précisé, le tournoi est entièrement chargé.
        Un tournoi partiellement chargé ne contiens que les IDs des joueurs, matchs et tours.
        Un tournoi complètement chargé est constitué d'objets chargés en mémoire.
        """
        tournament = self.loader.load_tournament_data(tournament_id)
        player_list = list()
        turn_list = list()

        if not partial_load:
            self.app_messenger.accept_event(config.AppInput.LOAD_PLAYER)
            self.app_messenger.accept_event(config.AppInput.LOAD_TURN)
            self.app_messenger.accept_event(config.AppInput.NEW_MATCH)

            for player_id in tournament['players']:
                player_list.append(self.app_messenger.send_event(config.AppInput.LOAD_PLAYER, [player_id]))

            player_dict = {player.player_id: player for player in player_list}
            for turn_id in tournament['turn_list']:
                match_list = list()
                turn_obj = self.app_messenger.send_event(config.AppInput.LOAD_TURN, [turn_id])
                for match in turn_obj.match_list:
                    match_data = self.loader.load_match(match)
                    if not match_data:
                        continue
                    match_data['player_1'] = player_dict[match_data.get('player_1')]
                    match_data['player_2'] = player_dict[match_data.get('player_2')]
                    match_list.append(self.app_messenger.send_event(config.AppInput.NEW_MATCH, [match_data]))
                turn_obj.match_list = match_list
                turn_is_finished = turn_obj.finished
                if turn_is_finished and turn_obj.end_time is None:
                    print(f"Something went wrong while loading {turn_obj.name}")
                turn_list.append(turn_obj)
            tournament['players'] = player_list
            tournament['turn_list'] = turn_list

        tournament_data = {**tournament, 'tournament_id': tournament_id}
        return tournament_model.TournamentM(**tournament_data)

    def add_temp_tournament_selection_event_to_messenger(self,
                                                         tournament_listing: List,
                                                         callback_func: Callable) -> None:
        """
        Reçoit une liste d'objet tournoi, génère des événements pour les afficher sur la vue principale et
        enregistre ces événements auprès du messenger principal de l'application.
        """
        ordered_tournament = _order_tournament_by_status(tournament_listing)

        for tournament in ordered_tournament:
            tournament_str = tournament_view.tournament_object_flat_view(tournament)
            updated_event_call = self.app_messenger.update_event(config.AppInput.SET_TOURNAMENT_ACTIV,
                                                                 new_func=callback_func,
                                                                 new_str=tournament_str,
                                                                 make_copy=True)

            self.app_messenger.accept_event(tournament_str, call_event=updated_event_call, event_arg=[tournament])

    def show_tournament_selection_list(self, from_id: int = 0,
                                       to_id: int | None = None,
                                       excluded_id: List | None = None,
                                       callback_func: Callable or None = None) -> None:
        """
        Permet l'affichage d'une liste de tournoi sur la vue principale et accepte les évènements liés à la
        visualisation d'un tournoi
        Si aucune liste n'est fourni, l'intégralité de la base de donnée est chargée
        """

        self.main_view.menu_title = "## Tournament SELECTION ##"
        self.app_messenger.accept_event(config.AppInput.NEW_MATCH)
        self.app_messenger.accept_event(config.AppInput.LOAD_TURN)
        self.app_messenger.accept_event(config.AppInput.LOAD_PLAYER)

        if excluded_id is None:
            excluded_id = list()

        tournament_listing = list()

        if to_id is None:
            to_id = self.loader.get_nbr_db_entry(DB_NAME)

        for tournament_id_to_display in range(from_id, to_id + 1):
            if tournament_id_to_display in excluded_id:
                continue
            if self.loader.tournament_exist(tournament_id_to_display):
                tournament_listing.append(self.load_tournament_by_tournament_id(tournament_id_to_display,
                                                                                partial_load=True))
        if len(tournament_listing) == 0:
            print("No tournament to show")
            return

        self.app_messenger.ignore_all()
        if callback_func is None:
            callback_func = self.set_tournament_as_active

        self.add_temp_tournament_selection_event_to_messenger(tournament_listing, callback_func)

        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

    def set_tournament_as_active(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournois partiellement chargé, le charge entièrement, l'affiche et en affiche les contrôle
        """
        active_tournament = self.load_tournament_by_tournament_id(tournament_obj.tournament_id)
        self.display_tournament(active_tournament)
        self.get_tournament_controls(active_tournament)

    def start_tournament(self, tournament: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, génère le tour suivant, sauvegarde le tournoi et en affiche les contrôle
        """
        self.get_next_turn(tournament)
        self.save_tournament(tournament)
        self.resume_tournament(tournament)

    def go_to_next_turn(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, clôture le tour précédent, récupère le tour suivant,
        sauvegarde le tournoi.
        Affiche le tournoi et ses contrôles s'il est terminée,
        Affiche les contrôles du tour suivant si le tournoi est toujours en cours
        """
        self.app_messenger.accept_event(config.AppInput.END_TURN)
        self.app_messenger.send_event(config.AppInput.END_TURN, [tournament_obj.turn_list[-1]])
        next_turn = self.get_next_turn(tournament_obj)
        self.save_tournament(tournament_obj)

        if not next_turn or tournament_obj.is_finished:
            tournament_obj.end_tournament()
            self.display_tournament(tournament_obj)
            self.get_tournament_controls(tournament_obj)
            return

        self.app_messenger.send_event(config.AppInput.SET_TURN_ACTIV, [next_turn])

    def get_next_turn(self, tournament: tournament_model.TournamentM) -> turn_model.TurnM | bool:
        """
        Reçoit un object tournoi, retourne le tour qui doit être joué pour progresser le tournoi s'il est disponible,
        sinon retourne False
        """
        if tournament.turn_list and not tournament.turn_list[-1].finished:
            return tournament.turn_list[-1]

        if tournament.is_finished:
            return False

        players_pair_list = tournament.get_next_turn_player_pair()
        if not players_pair_list:
            return False

        self.app_messenger.accept_event(config.AppInput.NEW_TURN)
        self.app_messenger.accept_event(config.AppInput.END_TURN)
        self.app_messenger.accept_event(config.AppInput.NEW_MATCH)

        next_turn = self.app_messenger.send_event(config.AppInput.NEW_TURN,
                                                  [{"name": f'Round{len(tournament.turn_list) + 1}',
                                                    "player_pair": players_pair_list}])

        if tournament.turn_list:
            self.app_messenger.send_event(config.AppInput.END_TURN, [tournament.turn_list[-1]])

        tournament.register_turn(next_turn)
        self.save_tournament(tournament)
        return next_turn

    def switch_to_turn_control(self,
                               tournament: tournament_model.TournamentM,
                               finished: bool = False) -> None:
        """
        Reçoit un tournoi, déclare disponible et met à jour les événement lié au tournoi en cours et affiche les
        contrôles des tours du tournoi
        """
        self.app_messenger.ignore_all()

        self.app_messenger.update_event(config.AppInput.NEXT_TURN, new_func_arg=[tournament])
        self.app_messenger.update_event(config.AppInput.BACK_TO_TURN_LIST, new_func_arg=[tournament])

        self.app_messenger.accept_event(config.AppInput.VIEW_TURN_LIST)
        self.app_messenger.accept_event(config.AppInput.SET_TOURNAMENT_ACTIV, [tournament])
        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

        self.app_messenger.send_event(config.AppInput.VIEW_TURN_LIST, [tournament.turn_list, None, finished])

    def resume_tournament(self, tournament: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, contrôle le statu du dernier tour du tournoi avant d'afficher les contrôles du tournoi
        """
        current_turn = tournament.turn_list[-1]
        if current_turn.finished and not tournament.is_finished:
            self.start_tournament(tournament)
            return
        self.switch_to_turn_control(tournament, tournament.is_finished)

    def start_or_resume_tournament(self, tournament: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, vérifie s'il faut reprendre le tournoi en cours ou commencer ce nouveau tournoi
        """
        if len(tournament.turn_list) == 0:
            self.start_tournament(tournament)
        self.resume_tournament(tournament)

    def view_tournament_leaderboard(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi et affiche le classement complet du tour pour chacun des tours du tournoi
        """
        for turn in tournament_obj.turn_list:
            self.app_messenger.send_event(config.AppInput.DISPLAY_TURN_RANKING, [turn])

    def get_full_tournament_data(self, tournament_obj: tournament_model.TournamentM) -> Tuple[List, int, int]:
        """
        Reçoit un objet tournoi, parse la liste des tours pour obtenir la représentation et l'espace nécessaire à
        l'affichage détaillé d'un tour et ses matchs
        Retourne les informations nécessaires à l'affichage détaillé du tournoi
        """
        tournament_full_data = list()
        match_len = 0
        detail_len = 0
        for turn in tournament_obj.turn_list:
            turn_name, turn_timestamp, turn_detail, turn_match_len, turn_match_detail_lent = \
                self.app_messenger.send_event(
                    config.AppInput.TURN_FULL_VIEW,
                    [turn]
                )

            if turn_match_len > match_len:
                match_len = turn_match_len

            if turn_match_detail_lent > detail_len:
                detail_len = turn_match_detail_lent

            tournament_full_data.append([turn_name, turn_timestamp, turn_detail])
        return tournament_full_data, match_len, detail_len

    def view_tournament_details(self, tournament_obj: tournament_model.TournamentM) -> None:
        """
        Reçoit un objet tournoi, génère l'affichage complet du déroulement du tournoi et l'affiche sur la
        vue principale de l'application.
        """
        self.app_messenger.accept_event(config.AppInput.MATCH_FLAT_VIEW)
        self.app_messenger.accept_event(config.AppInput.TURN_FULL_VIEW)

        tournament_full_data, match_len, detail_len = self.get_full_tournament_data(tournament_obj)
        tournament_display = tournament_view.tournament_object_full_view(tournament_full_data, match_len, detail_len)

        self.display_tournament(tournament_obj)
        self.main_view.add_blocks(tournament_display)
