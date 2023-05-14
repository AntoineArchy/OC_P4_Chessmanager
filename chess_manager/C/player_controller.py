from __future__ import annotations

from typing import List, Dict, Callable, Any
from data import config

from core import messenger, tinydb_loader, mainview
from chess_manager.M import player_model
from chess_manager.V import player_view

DB_NAME = config.PLAYER_DB_NAME


def get_flat_player_view(player_obj: player_model.PlayerM) -> str:
    return player_view.see_player_as_line(player_obj)


def _get_player_display(player: player_model.PlayerM) -> str:
    existing_player_display = player_view.player_object_full_view(player)
    return existing_player_display


def get_new_player_creation_data(master_view: mainview.MainView) -> Dict:
    form = player_view.player_creation_form()
    validator = player_model.PLAYER_FORM_VALIDATOR
    form_answer = master_view.get_form_answer(form, validator)
    return form_answer


def get_player_obj_from_player_dict(player_dict: Dict) -> player_model.PlayerM:
    return player_model.PlayerM(**player_dict)


class PlayerC:
    def __init__(self,
                 loader: tinydb_loader.TinyDBLoader,
                 main_view: mainview.MainView,
                 app_messenger: messenger.Messenger) -> None:

        self.main_view = main_view
        self.loader = loader
        self.app_messenger = app_messenger

        # Déclaration des paires événement/méthode
        app_messenger.register_call_event(config.AppInput.NEW_PLAYER, self.create_new_player_from_form,
                                          "Create new player", )
        app_messenger.register_call_event(config.AppInput.VIEW_PLAYER_LIST, self.show_player_selection_list,
                                          "View player listing")
        app_messenger.register_call_event(config.AppInput.ADD_PLAYER, self.show_player_selection_list,
                                          "Add player")
        app_messenger.register_call_event(config.AppInput.NEXT_PLAYER_PAGE, self.show_player_selection_list,
                                          "See next player page")
        app_messenger.register_call_event(config.AppInput.PREV_PLAYER_PAGE, self.show_player_selection_list,
                                          "See previous player page")

        app_messenger.register_call_event(config.AppInput.LOAD_PLAYER, self.load_player_obj_from_player_id)
        app_messenger.register_call_event(config.AppInput.PLAYER_FULL_VIEW, self._display_player)
        app_messenger.register_call_event(config.AppInput.PLAYER_FLAT_VIEW, get_flat_player_view)

    def _create_new_player_from_dict(self,
                                     player_creation_data: Dict) -> player_model.PlayerM:
        """Reçoit un dictionnaire de donnée et retourne un objet joueur """
        player_id = self.loader.save_player(player_creation_data)
        new_player = get_player_obj_from_player_dict({**player_creation_data, **{'player_id': player_id}})
        return new_player

    def create_new_player_from_form(self) -> player_model.PlayerM:
        """
        Créer un nouveau joueur à partir des réponses fournit par l'utilisateur au formulaire
        de création de joueurs
        """
        self.main_view.menu_title = "## Player creation ##"

        player_data = get_new_player_creation_data(self.main_view)
        new_player = self._create_new_player_from_dict(player_data)

        self.main_view.add_to_display(_get_player_display(new_player))
        return new_player

    def _load_player_data_from_player_id(self,
                                         player_id: int) -> Dict:
        """ Reçoit l'id d'un joueur et en charge les information depuis la base de donnée"""
        player_data = self.loader.load_player(player_id)
        return player_data

    def load_player_obj_from_player_id(self, player_id: int) -> player_model.PlayerM | bool:
        """Reçoit l'id d'un joueur et retourne un objet joueur si l'id existe, 'False' s'il n'existe pas."""
        # EDGE CASE, We could want to "load" an already loaded player from a cached tournament.
        if isinstance(player_id, player_model.PlayerM):
            return player_id

        loaded_player_data = self._load_player_data_from_player_id(player_id)
        if not loaded_player_data:
            return False
        loaded_player_obj = get_player_obj_from_player_dict(loaded_player_data)
        return loaded_player_obj

    def _load_players_obj_list_from_player_id_list(self,
                                                   player_id_list) -> List:
        """Reçoit une list de player_id et retourne une liste d'objets joueurs correspondants"""
        player_obj_list = list()
        for player_id in player_id_list:
            player_obj = self.load_player_obj_from_player_id(player_id)
            if not player_obj:
                continue
            player_obj_list.append(player_obj)
        return player_obj_list

    def _add_temp_player_display_event_to_messenger(self,
                                                    player_obj_list: List,
                                                    callback_func: Callable) -> None:
        """
        Reçoit une liste d'objet joueur, génère des événements pour les afficher sur la vue principale et
        enregistre ces événements auprès du messenger principal de l'application.
        """
        for player in player_obj_list:
            player_str = player_view.see_player_as_line(player)
            updated_event_call = self.app_messenger.update_event(config.AppInput.PLAYER_FULL_VIEW,
                                                                 new_func=callback_func,
                                                                 new_func_arg=[player], new_str=player_str,
                                                                 make_copy=True)
            self.app_messenger.accept_event(player_str, call_event=updated_event_call)

    def _display_player(self,
                        player: player_model.PlayerM) -> None:
        """
        Reçoit un objet joueur et l'affiche sur la vue principale avant d'accepter les événements lié à la
        visualisation de joueur
        """
        self.main_view.add_to_display(_get_player_display(player))
        self.app_messenger.ignore_all()
        self.app_messenger.accept_event(config.AppInput.VIEW_PLAYER_LIST)
        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

    def load_and_order_player_alphab(self,
                                     list_of_player_id=None) -> List:
        """
        Retourne une liste de joueurs triés par ordre alphabétique, si aucune liste n'est fournie
        en entrée, charge l'intégralité de la base de donnée
        """
        if list_of_player_id is None:
            list_of_player_id = [player_id for player_id in range(1, self.loader.get_nbr_db_entry(DB_NAME) + 1)]
        player_list = list()

        for player_id in list_of_player_id:
            player_obj = self.load_player_obj_from_player_id(player_id)
            if not player_obj:
                continue
            player_list.append(player_obj)

        return sorted(player_list,
                      key=lambda individual_player_obj: individual_player_obj.get_alphab_sort())

    # def display_player_alphab(self, player_id_list=None):
    #     sorted_player_list = self.load_and_order_player_alphab(player_id_list)
    #     self.show_player_selection_list(sorted_player_list)

    def show_player_selection_list(self,
                                   list_of_player_to_display: List | None = None,
                                   player_exclude_from_display: List | None = None,
                                   nbr_of_display_by_page: int = config.NBR_OF_PLAYER_TO_DISPLAY_BY_PAGE,
                                   actual_page: int = 0,
                                   callback_func: Any | None = None):
        """
        Permet l'affichage d'une liste de joueurs sur la vue principale et accepte les évènements liés à la
        visualisation des joueurs
        Si aucune liste n'est fourni, l'intégralité de la base ed donnée est chargée,
        """
        self.main_view.menu_title = "## Player SELECTION ##"
        self.app_messenger.ignore_all()

        if actual_page != 0:
            self.app_messenger.accept_event(config.AppInput.PREV_PLAYER_PAGE,
                                            [list_of_player_to_display,
                                             player_exclude_from_display,
                                             nbr_of_display_by_page,
                                             actual_page - 1,
                                             callback_func])

        self.app_messenger.accept_event(config.AppInput.NEXT_PLAYER_PAGE,
                                        [list_of_player_to_display,
                                         player_exclude_from_display,
                                         nbr_of_display_by_page,
                                         actual_page + 1,
                                         callback_func])

        self.app_messenger.accept_event(config.AppInput.MAIN_MENU)
        self.app_messenger.accept_event(config.AppInput.QUIT)

        nbr_of_display_by_page = min(nbr_of_display_by_page, self.loader.get_nbr_db_entry(DB_NAME))

        if player_exclude_from_display is None:
            player_exclude_from_display = list()

        if list_of_player_to_display is None:
            display_from = 1 + actual_page * nbr_of_display_by_page
            display_to = display_from + nbr_of_display_by_page + len(player_exclude_from_display)
            player_alphab = self.load_and_order_player_alphab()
            list_of_player_to_display = player_alphab[display_from:display_to]

        for excluded in player_exclude_from_display:
            if excluded in list_of_player_to_display:
                list_of_player_to_display.remove(excluded)

        if len(list_of_player_to_display) > nbr_of_display_by_page:
            list_of_player_to_display = list_of_player_to_display[:nbr_of_display_by_page]

        player_listing = self.load_and_order_player_alphab(list_of_player_to_display)

        if len(player_listing) == 0:
            self.main_view.add_to_display(player_view.no_existing_player_error())
            self.app_messenger.ignore_event(config.AppInput.NEXT_PLAYER_PAGE)
            return

        if len(player_listing) < nbr_of_display_by_page:
            self.app_messenger.ignore_event(config.AppInput.NEXT_PLAYER_PAGE)

        if callback_func is None:
            callback_func = self._display_player

        self._add_temp_player_display_event_to_messenger(player_listing, callback_func)
