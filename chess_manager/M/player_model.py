from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict

MAX_STR_LEN = 19


def check_valid_birthday(birthday_input: Any) -> bool | str:
    """ Vérifie si la date entrée par l'utilisateur est bien une date. """
    try:
        bool(datetime.strptime(birthday_input, '%d/%m/%Y'))
        return True
    except ValueError:
        return "Please enter a date in format 'DD/MM/YYYY'"


def check_valid_int(user_int_input: Any):
    """ Vérifie si l'input de l'utilisateur est numérique. """
    try:
        float(user_int_input)
        return True
    except ValueError:
        return False


def check_valid_str(user_str_input: Any) -> bool | str:
    """ Vérifie si l'input de l'utilisateur est un str valide. """
    for char in user_str_input:
        if check_valid_int(char):
            return "Please don't use number"
    if not 0 < len(user_str_input) < MAX_STR_LEN:
        return f"You must enter from 1 to {MAX_STR_LEN} char."
    return True


def check_valid_ine(user_input_ine: Any):
    """ Vérifie si l'INE entré par l'utilisateur est valide. """

    if not len(user_input_ine) == 7:
        return "Please enter INE (2char then 5 int)"

    str_part = user_input_ine[:2]
    int_part = user_input_ine[2:]

    if isinstance(check_valid_str(str_part), str):
        return "Please start by 2 char"
    if not check_valid_int(int_part):
        return "Please end INE by 5 number"
    return True


PLAYER_FORM_VALIDATOR: Dict = {
    "first_name": check_valid_str,
    "last_name": check_valid_str,
    "birthday": check_valid_birthday,
    "ine": check_valid_ine,
}


@dataclass
class PlayerM:
    """Représentation d'un joueur d'échec."""
    first_name: str
    last_name: str
    birthday: str
    ine: str
    already_played_against: List = field(default_factory=list)
    player_id: int = -1

    def has_played_against(self, other_player: PlayerM) -> bool:
        return other_player in self.already_played_against

    def clear_player_pairing(self) -> None:
        self.already_played_against.clear()

    def get_alphab_sort(self) -> str:
        return f"{self.last_name.upper()}{self.first_name.upper()}{self.ine.upper()}"

    def get_save_data(self) -> Dict:
        return {'first_name': self.first_name,
                'last_name': self.last_name,
                'birthday': self.birthday,
                'ine': self.ine,
                'player_id': self.player_id}
