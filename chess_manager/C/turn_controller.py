from __future__ import annotations

from typing import Dict, List, Any, Tuple

from core import tinydb_loader, mainview, messenger
from data.config import AppInput

from chess_manager.M import turn_model
from chess_manager.V import turn_view


def _get_turn_obj_from_turn_dict(turn_dict: Dict) -> turn_model.TurnM:
    return turn_model.TurnM(**turn_dict)


class TurnC:
    def __init__(self,
                 loader: tinydb_loader.TinyDBLoader,
                 main_view: mainview.MainView,
                 app_messenger: messenger.Messenger) -> None:

        self.main_view = main_view
        self.loader = loader
        self.app_messenger = app_messenger

        app_messenger.register_call_event(AppInput.SET_TURN_ACTIV, self.set_turn_as_active)
        app_messenger.register_call_event(AppInput.NEW_TURN, self.create_new_turn_from_turn_dict)
        app_messenger.register_call_event(AppInput.LOAD_TURN, self.load_turn_obj_from_turn_id)
        app_messenger.register_call_event(AppInput.SAVE_TURN, self.save_turn_obj)
        app_messenger.register_call_event(AppInput.END_TURN, self.end_turn_obj)

        app_messenger.register_call_event(AppInput.VIEW_TURN_LIST, self.show_turn_selection_list)
        app_messenger.register_call_event(AppInput.DISPLAY_TURN_RANKING, self.display_turn_ranking)
        app_messenger.register_call_event(AppInput.TURN_FULL_VIEW, self.get_turn_full_data)

    def feed_turn(self, turn: turn_model.TurnM, player_data: List) -> None:
        """
        Reçoit un objet tour ainsi qu'une liste de paire de joueurs, crée autant de match dans le tour que de
        paire sont transmises.
        """
        for player_pair in player_data:
            match_dict = {"player_1": player_pair[0][0],
                          'player_1_score': player_pair[0][1],
                          "player_2": player_pair[1][0],
                          'player_2_score': player_pair[1][1]
                          }
            new_match = self.app_messenger.send_event(AppInput.NEW_MATCH, [match_dict])
            turn.register_match(new_match)

    def create_new_turn_from_turn_dict(self, turn_data: Dict) -> turn_model.TurnM:
        """
        Reçoit les données de création d'un tour, génère le tour complétement, le sauvegarde et le retourne
        """
        player_pair_list = turn_data.pop('player_pair')
        new_turn = _get_turn_obj_from_turn_dict(turn_data)
        self.feed_turn(new_turn, player_pair_list)
        self.save_turn_obj(new_turn)
        return new_turn

    def set_turn_as_active(self, turn: turn_model.TurnM, tournament_finished: bool = False):
        """
        Reçoit un objet tour, le sauvegarde et en affiche la liste de matchs
        """
        self.save_turn_obj(turn)
        self.app_messenger.accept_event(AppInput.VIEW_MATCH_LIST)
        self.app_messenger.send_event(AppInput.VIEW_MATCH_LIST, [turn.match_list, None, tournament_finished])

    def save_turn_obj(self, turn: turn_model.TurnM) -> None:
        turn.turn_id = self.loader.save_turn(turn.get_save_data())

    def load_turn_obj_from_turn_id(self, turn_id: int) -> bool | turn_model.TurnM:
        loaded_turn_data = self.loader.load_turn(turn_id)
        if not loaded_turn_data:
            return False
        loaded_turn_obj = _get_turn_obj_from_turn_dict(loaded_turn_data)
        return loaded_turn_obj

    def end_turn_obj(self, turn: turn_model.TurnM):
        """
        Reçoit un objet tour et le marque comme terminé avant d'en faire une sauvegarde
        """
        turn.end_turn()
        self.save_turn_obj(turn)

    def show_turn_selection_list(self, turn_list: List,
                                 callback_func: Any | None = None,
                                 tournament_finished: bool = False) -> None:
        """
        Reçoit une liste de tour, génère des événements pour les afficher sur la vue principale et rendre les
        tours actif, enregistre ces événements auprès du messenger principal de l'application.
        """
        self.main_view.menu_title = "## Turn SELECTION ##"

        if callback_func is None:
            callback_func = self.set_turn_as_active

        for turn in turn_list:
            turn_str = turn_view.turn_object_flat_view(turn)
            updated_event_call = self.app_messenger.update_event(AppInput.SET_TURN_ACTIV,
                                                                 new_func=callback_func,
                                                                 new_str=turn_str,
                                                                 make_copy=True)

            self.app_messenger.accept_event(turn_str, call_event=updated_event_call,
                                            event_arg=[turn, tournament_finished])

    def get_turn_ranking(self, turn: turn_model.TurnM, nbr_player_to_display: int = -1) -> List:
        """
        Reçoit un objet tour chargé, ordonne les joueurs en fonction de leur score et retourne la représentation
        du classement en fonction du nombre de joueurs à afficher.
        Si aucun nombre n'est précisé l'intégralité des joueurs du tour sont affichés
        """
        to_return = list()
        turn_data = turn.get_turn_data()

        ordered_player = sorted(turn_data, key=lambda turn_player_data: turn_player_data[1], reverse=True)
        if nbr_player_to_display == -1 or nbr_player_to_display > len(ordered_player):
            nbr_player_to_display = len(ordered_player)

        for player_ranking, player_data in enumerate(ordered_player[:nbr_player_to_display]):
            player_flat_view = self.app_messenger.send_event(AppInput.PLAYER_FLAT_VIEW, [player_data[0]])
            ranking_display = f"{player_ranking + 1} : {player_flat_view} -> {player_data[1]} Pts"
            to_return.append(ranking_display)
        return to_return

    def display_turn_ranking(self, turn: turn_model.TurnM, nbr_player_to_display: int = -1) -> None:
        """
        Reçoit un tour et un nombre de places de podium à afficher, génère le classement du tour et affiche le podium
        sur la vue principale.
        Si le nombre de joueurs n'est pas précisé, l'intégralité des joueurs du tour sont affichés
        """
        ranking_display = self.get_turn_ranking(turn, nbr_player_to_display)
        self.main_view.add_to_display(f"{turn.name} ranking :")
        for individual_player_score in ranking_display:
            self.main_view.add_to_display(individual_player_score)

    def get_turn_full_data(self, turn: turn_model.TurnM) -> Tuple:
        """
        Reçoit un objet tour, parse la liste des matchs pour obtenir la représentation et l'espace nécessaire à
        l'affichage détaillé d'un match, retourne les informations nécessaires à l'affichage détaillé du tour
        """
        match_len = 0
        detail_len = 0

        turn_name = f"{turn.name} "
        turn_timestamp = f'{turn.start_time} - {turn.end_time}'
        turn_detail = list()
        for match_index, match in enumerate(turn.match_list):
            match_name = f"-MATCH{match_index + 1}-"  # On ne veut pas de match0
            match_detail = f' {self.app_messenger.send_event(AppInput.MATCH_FLAT_VIEW, [match])}'
            if len(match_name) > match_len:
                match_len = len(match_name)
            if len(match_detail) > detail_len:
                detail_len = len(match_detail)
            turn_detail.append([match_name, match_detail])
        return turn_name, turn_timestamp, turn_detail, match_len, detail_len
