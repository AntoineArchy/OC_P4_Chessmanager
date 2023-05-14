from __future__ import annotations

from typing import List, Dict, Callable

from core import messenger, tinydb_loader, mainview
from data import config

from chess_manager.M import match_model
from chess_manager.V import match_view

DB_NAME = config.MATCH_DB_NAME


def _get_match_obj_from_match_dict(match_dict: Dict) -> match_model.MatchM:
    return match_model.MatchM(**match_dict)


def _is_match_list_finished(match_list: List) -> bool:
    if len(match_list) == 0:
        return False

    for match in match_list:
        if match.winner is None:
            return False
    return True


def _order_match_by_match_id(match_list: List) -> List:
    return sorted(match_list, key=lambda match_obj: match_obj.match_id, reverse=True)


def _order_match_by_status(match_list: List) -> List:
    """Reçoit une liste de match non ordonnée, retourne une liste de match en cours puis terminé"""
    unfinished = [match for match in match_list if match.winner is None]
    finished = [match for match in match_list if match not in unfinished]

    unfinished = _order_match_by_match_id(unfinished)
    finished = _order_match_by_match_id(finished)
    return [*unfinished, *finished]


class MatchC:
    def __init__(self,
                 loader: tinydb_loader.TinyDBLoader,
                 main_view: mainview.MainView,
                 app_messenger: messenger.Messenger) -> None:

        self.main_view = main_view
        self.loader = loader
        self.app_messenger = app_messenger

        app_messenger.register_call_event(config.AppInput.NEW_MATCH, self.create_new_match_from_match_dict)
        app_messenger.register_call_event(config.AppInput.SET_MATCH_ACTIV, self.set_match_as_active)
        app_messenger.register_call_event(config.AppInput.SET_MATCH_WINNER, self.handle_winner_input)
        app_messenger.register_call_event(config.AppInput.VIEW_MATCH_LIST, self.show_match_selection_list)
        app_messenger.register_call_event(config.AppInput.MATCH_FLAT_VIEW, self.get_match_flat_view)
        app_messenger.register_call_event(config.AppInput.SET_MATCH_DRAW, self.handle_winner_input,
                                          event_str="Set draw")
        app_messenger.register_call_event(config.AppInput.BACK_TO_MATCH_LIST, self.show_match_selection_list,
                                          event_str="Back to match list")

    def _add_match_winning_event_to_messenger(self,
                                              match: match_model.MatchM) -> None:
        """
        Reçoit un match, génère les événements pour déclarer un joueur vainqueur et les déclare valides auprès du
        messenger de l'application
        """
        player_1_flat_view = self.app_messenger.send_event(config.AppInput.PLAYER_FLAT_VIEW, [match.player_1])
        player_2_flat_view = self.app_messenger.send_event(config.AppInput.PLAYER_FLAT_VIEW, [match.player_2])

        winner_1_str = f"Set {player_1_flat_view} as Winner"
        winner_2_str = f"Set {player_2_flat_view} as Winner"

        set_player_1_winner_event = self.app_messenger.update_event(config.AppInput.SET_MATCH_WINNER,
                                                                    new_str=winner_1_str,
                                                                    make_copy=True)
        set_player_2_winner_event = self.app_messenger.update_event(config.AppInput.SET_MATCH_WINNER,
                                                                    new_str=winner_2_str,
                                                                    make_copy=True)

        self.app_messenger.accept_event(winner_1_str, call_event=set_player_1_winner_event, event_arg=[1, match])
        self.app_messenger.accept_event(winner_2_str, call_event=set_player_2_winner_event, event_arg=[2, match])
        self.app_messenger.accept_event(config.AppInput.SET_MATCH_DRAW, event_arg=[0, match])

    def _add_temp_match_selection_event_to_messenger(self,
                                                     match_list: List,
                                                     callback_func: Callable) -> None:
        """
        Reçoit une liste de match, les trie par statu, génère les événements liés à la visualisation des matchs et
        les déclare valides auprès du messenger de l'application
        """
        for match in _order_match_by_status(match_list):
            match_str = self.get_match_flat_view(match)
            updated_event_call = self.app_messenger.update_event(config.AppInput.SET_MATCH_ACTIV,
                                                                 new_func=callback_func,
                                                                 new_str=match_str,
                                                                 make_copy=True)

            self.app_messenger.accept_event(match_str, call_event=updated_event_call, event_arg=[match])

    def _get_match_control(self,
                           match: match_model.MatchM) -> None:
        """
        Reçoit un objet match et déclare au messenger de l'application que les different événements liés à la
        gestion de ce match sont valides
        """
        self.app_messenger.ignore_all()
        self.app_messenger.accept_event(config.AppInput.PLAYER_FLAT_VIEW)
        self.app_messenger.accept_event(config.AppInput.BACK_TO_MATCH_LIST)
        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

        if match.winner is None:
            self._add_match_winning_event_to_messenger(match)

    def _save_match_obj(self,
                        match_obj: match_model.MatchM) -> None:
        match_data = match_obj.get_save_data()
        match_obj.match_id = self.loader.save_match(match_data)

    def create_new_match_from_match_dict(self, match_data):
        new_match = _get_match_obj_from_match_dict(match_data)
        self._save_match_obj(new_match)
        return new_match

    def set_match_as_active(self,
                            match: match_model.MatchM) -> None:
        """ Reçoit un objet match, le sauvegarde, l'affiche sur la vue principale et affiche les contrôles du match """
        self._save_match_obj(match)
        self.main_view.add_to_display(match_view.see_match_as_line(match))
        self._get_match_control(match)

    def handle_winner_input(self,
                            user_winner_input: int,
                            match: match_model.MatchM) -> None:
        """ Indique le résultat du match, le sauvegarde et le rend actif """
        if user_winner_input == 1:
            match.end_match(match.player_1)
        elif user_winner_input == 2:
            match.end_match(match.player_2)
        else:
            match.end_match()

        self._save_match_obj(match)
        self.set_match_as_active(match)

    def show_match_selection_list(self,
                                  match_list: List,
                                  callback_func: Callable or None = None,
                                  tournament_over=False) -> None:
        """
        Reçoit une liste de match, les affiche sur la vue principale et accepte les évènements
        liés à la gestion de matchs au cours d'un tour de tournois.
        """
        self.main_view.menu_title = "## Match SELECTION ##"
        self.app_messenger.ignore_all()

        self.app_messenger.update_event(config.AppInput.BACK_TO_MATCH_LIST,
                                        new_func_arg=[match_list, callback_func, tournament_over])

        self.app_messenger.accept_event(config.AppInput.SET_TURN_ACTIV)
        self.app_messenger.accept_event(config.AppInput.BACK_TO_TURN_LIST)
        self.app_messenger.accept_event(config.AppInput.SET_TOURNAMENT_ACTIV)
        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

        if callback_func is None:
            callback_func = self.set_match_as_active

        self._add_temp_match_selection_event_to_messenger(match_list, callback_func)

        if _is_match_list_finished(match_list):
            self.app_messenger.accept_event(config.AppInput.NEXT_TURN)

    def get_match_flat_view(self, match: match_model.MatchM):
        """Retourne la représentation d'un objet match en une ligne. """
        return match_view.see_match_as_line(match)
