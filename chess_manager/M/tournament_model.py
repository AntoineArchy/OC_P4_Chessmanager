from __future__ import annotations

import datetime
from dataclasses import dataclass, field
import random
from typing import List, Dict, Any

from chess_manager.M import turn_model

MAX_STR_LEN = 122


def check_valid_int(user_int_input: Any) -> bool:
    """ Vérifie si l'input de l'utilisateur est un int valide. """
    try:
        int(user_int_input)
        return True
    except ValueError:
        return False


def check_valid_str(user_str_input: Any) -> bool | str:
    """ Vérifie si l'input de l'utilisateur est un str valide. """
    if not 0 < len(user_str_input) < MAX_STR_LEN:
        return f"You must enter from 1 to {MAX_STR_LEN} char."
    return True


TOURNAMENT_FORM_VALIDATOR: Dict = {
    'name': check_valid_str,
    'place': check_valid_str,
    'description': check_valid_str,
    'turn_nbr': check_valid_int,
    'player_nbr': check_valid_int
}


def _shuffle_player_list(player_list: List) -> List:
    """Retourne une nouvelle liste mélangée"""
    randomised_list = player_list[:]
    random.shuffle(randomised_list)
    return randomised_list


def _order_player_by_score(full_player_data: List) -> List:
    full_player_data.sort(key=lambda individual_player_data: individual_player_data[1], reverse=True)
    return full_player_data


def _reset_player_pairing(ordered_player_data: List) -> List:
    """Visite chaque joueur de la liste reçue et en reinitialise le compteur d'adversaires"""
    for player_data in ordered_player_data:
        player_data[0].clear_player_pairing()
    return ordered_player_data


def _make_player_pair(ordered_player_data: List) -> List:
    """
    Reçoit une liste de (joueurs, score) et retourne une liste de paire (joueurs, score) classé par score
    décroissant. Si tous les joueurs ont déjà joué les uns contre les autres, les historiques de pairage sont
    réinitialisés
    """
    player_pairs = list()
    working_list = ordered_player_data[:]

    adversary_index = 0
    current_pairing_player = working_list.pop(0)

    while len(working_list) > 0:
        if current_pairing_player[0].has_played_against(working_list[adversary_index][0]):
            adversary_index += 1
            if adversary_index >= len(working_list):
                print("Cannot make more player pair without player playing each other again")
                return _make_player_pair(_reset_player_pairing(ordered_player_data[:]))
            continue
        player_pairs.append((current_pairing_player, working_list.pop(adversary_index)))
        adversary_index = 0

        if len(working_list) < 1:
            break
        current_pairing_player = working_list.pop(0)
    return player_pairs


@dataclass
class TournamentM:
    """Représentation d'un tournoi d'échec"""
    name: str
    place: str
    turn_nbr: int = 4
    description: str = "No description"
    player_nbr: int = 0
    players: List = field(default_factory=list)
    turn_list: List = field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None
    tournament_id: int = -1

    def __post_init__(self) -> None:
        if self.start_date is None:
            self.start_date = datetime.datetime.now().strftime("%d/%m/%y %H:%M")

    def register_turn(self, turn: turn_model.TurnM) -> None:
        self.turn_list.append(turn)

    def get_current_turn_nbr(self) -> int:
        return len(self.turn_list)

    @property
    def is_finished(self) -> bool:
        if self.end_date is not None:
            return True
        if self.get_current_turn_nbr() < self.turn_nbr:
            return False
        return self.turn_list[-1].finished

    def end_tournament(self) -> None:
        if self.end_date is not None:
            return
        self.end_date = datetime.datetime.now().strftime("%d/%m/%y %H:%M")

    def get_next_turn_player_pair(self) -> List:
        if self.get_current_turn_nbr() > 0:
            return _make_player_pair(_order_player_by_score(self.turn_list[-1].get_turn_data()))
        player_list = _shuffle_player_list(self.players)
        player_data = [[player, 0] for player in player_list]
        return _make_player_pair(_order_player_by_score(player_data))

    def from_obj_to_dict(self) -> Dict:
        return {'name': self.name,
                'place': self.place,
                'turn_nbr': int(self.turn_nbr),
                'description': self.description,
                'player_nbr': int(self.player_nbr),
                'players': [player.player_id for player in self.players],
                'turn_list': [turn.turn_id for turn in self.turn_list],
                'start_date': self.start_date,
                'end_date': self.end_date,
                'tournament_id': self.tournament_id,
                }
