from __future__ import annotations

from functools import partial
from typing import Callable, List, Dict, Any

from data import config


class Messenger:
    """
    Classe centrale de l'application, le messenger enregistre et transmet les différents événements utilisés par les
    contrôleurs de l'application.
    Les événements enregistrés peuvent ensuite être acceptés (disponible à l'utilisation),
    mis à jour (l'événement enregistré est modifié), ou ignoré (L'événement est toujours enregistré, mais
    n'est plus disponible à l'utilisation).
    Certains événements peuvent être acceptés sans enregistrement, mais ne seront alors plus disponible après le
    prochain appel à Messenger.ignore_all().
    """
    def __init__(self) -> None:
        self.ori_event_dict = dict()
        self.event_str_dict = dict()
        self.in_use_event_dict = dict()
        self.allowed_event = list()

    def register_call_event(self,
                            event: config.AppInput | str,
                            func: Callable or None,
                            event_str: str | None = None,
                            func_args: List | None = None) -> None:
        """Enregistre les événements et leurs noms éventuels. """
        self.ori_event_dict[event] = [func, func_args, None]

        if event_str is not None:
            self.event_str_dict[event_str] = event

    def accept_event(self,
                     event: config.AppInput | str,
                     event_arg: List | None = None,
                     call_event: List | bool = False) -> None:
        """Accepte les événements et les rend disponibles à l'utilisation. """
        self.allowed_event.append(event)

        if not call_event:
            call_event = self.ori_event_dict.get(event)

        self.in_use_event_dict[event] = call_event
        if event_arg is not None:
            self.in_use_event_dict[event][2] = event_arg

    def accept_multiple_event(self,
                              events_and_args_list: List) -> None:
        """Helper fonction pour l'acceptation de plusieurs événements"""

        for event, args in events_and_args_list:
            self.accept_event(event, args)

    def ignore_event(self,
                     event: config.AppInput | str) -> None:
        """
        Retire un événement de la liste des événements disponibles, sans distinction entre les événements enregistrés
        ou anonymes
        """
        if event not in self.allowed_event:
            return
        self.allowed_event.remove(event)

    def ignore_all(self, keep: List | None = None) -> None:
        """
        Reset la liste des événements disponibles, si une liste d'événements est précisée ceux-ci restent disponible
        """
        if keep is None:
            self.allowed_event.clear()
            self.in_use_event_dict.clear()
            return
        [self.ignore_event(to_ignore_event) for to_ignore_event in self.allowed_event if to_ignore_event not in keep]

    def get_allowed_event_and_str(self) -> Dict:
        """ Retourne un dict de type {nom_de_levenement : evenement, ...} pour tout événement disponible étant nommé"""
        return {event_str: event for event_str, event in self.event_str_dict.items() if
                (event in self.allowed_event or event_str in self.allowed_event)}

    def update_event(self,
                     event: config.AppInput | str,
                     new_func: None or Callable = None,
                     new_func_arg: List | None = None,
                     new_str: str | None = None,
                     make_copy: bool = False) -> List | None:
        """ Reçoit l'app_input d'un événement enregistré et en modifie la fonction, ses arguments ou le nom. """
        if event not in self.ori_event_dict:
            return

        to_update_event = self.ori_event_dict.get(event)[:]

        if new_func is not None:
            to_update_event[0] = new_func

        if new_func_arg is not None:
            to_update_event[1] = new_func_arg

        if new_str is not None:
            self.event_str_dict[new_str] = new_str

        if not make_copy:
            # Si l'utilisateur met à jour un événement sans demander une copie, on met à jour
            # l'enregistrement d'origine
            self.ori_event_dict[event] = to_update_event
        return to_update_event

    def generate_event_call(self,
                            event: config.AppInput or str) -> bool | Callable:
        """
        Reçoit l'app_input d'un événement disponible et construit une fonction à partir des différents éléments
        associés à cet app_input
        """
        if event not in self.allowed_event or event not in self.in_use_event_dict:
            print("SOMETHING WENT WRONG", event in self.in_use_event_dict, event, self.in_use_event_dict)
            return False

        event_data = self.in_use_event_dict[event]
        func = event_data[0]
        func_args = list()
        if event_data[1] is not None:
            func_args.extend(event_data[1])
        if event_data[2] is not None:
            func_args.extend(event_data[2])
        if func_args:
            func = partial(func, *func_args)
        return func

    def handle_event(self,
                     event: config.AppInput | str) -> None:
        """Reçoit l'app_input d'un événement disponible, génère la fonction correspondante et l'exécute"""
        event_call = self.generate_event_call(event)
        if not event_call:
            return
        event_call()

    def send_event(self,
                   event: config.AppInput,
                   event_args: List | None = None) -> Any:
        """
        Reçoit l'app_input d'un événement disponible, génère la fonction correspondante et retourne
        l'output de la fonction
        """
        to_return_event = self.generate_event_call(event)
        if not to_return_event:
            return
        return to_return_event(*event_args)
