from __future__ import annotations

from dataclasses import dataclass, field
import datetime
from typing import Dict, List

from chess_manager.M import match_model


@dataclass
class TurnM:
    """Représentation d'un tour de tournois d'échec."""
    name: str
    start_time: str | None = None
    end_time: str | None = None
    match_list: list = field(default_factory=list)
    turn_id: int = -1

    def __post_init__(self) -> None:
        if self.start_time is None:
            self.start_time = datetime.datetime.now().strftime("%d/%m/%y %H:%M")

    def get_save_data(self) -> Dict:
        return {'name': self.name,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'match_list': [match.match_id for match in self.match_list],
                'turn_id': self.turn_id,
                }

    def register_match(self,
                       match: match_model.MatchM) -> None:
        self.match_list.append(match)

    def get_turn_data(self) -> List:
        """Itère la liste des matchs pour en récupéré les informations"""
        turn_data = list()
        for match in self.match_list:
            turn_data.extend(match.get_match_data())
        return turn_data

    def end_turn(self) -> None:
        self.end_time = datetime.datetime.now().strftime("%d/%m/%y %H:%M")

    @property
    def finished(self) -> bool:
        if len(self.match_list) == 0:
            return False
        for match in self.match_list:
            if match.winner is None:
                return False
        if self.end_time is None:
            self.end_turn()
        return True
