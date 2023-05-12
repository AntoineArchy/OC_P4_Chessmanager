from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Dict

from chess_manager.M import player_model


@dataclass
class MatchM:
    """Représentation d'un match entre deux joueurs."""
    player_1: player_model.PlayerM
    player_1_score: int
    player_2: player_model.PlayerM
    player_2_score: int
    winner: bool or None = None
    match_id: int = -1

    def __post_init__(self) -> None:
        self.player_1.already_played_against.append(self.player_2)
        self.player_2.already_played_against.append(self.player_1)

    def get_match_data(self) -> Tuple:
        """Retourne des tuples (joueur, score) pour être stocké dans un objet 'tour'."""
        return [self.player_1, self.player_1_score], [self.player_2, self.player_2_score]

    def end_match(self,
                  winner: player_model.PlayerM | None = None) -> None:
        """Met à jour les scores des joueurs en fonction du résultat du match"""
        if winner is None:
            self.player_1_score += .5
            self.player_2_score += .5
            self.winner = False
            return
        if winner is self.player_1:
            self.player_1_score += 1
        elif winner is self.player_2:
            self.player_2_score += 1
        else:
            raise ValueError

        self.winner = winner.player_id

    def get_save_data(self) -> Dict:
        return {"player_1": self.player_1.player_id,
                "player_1_score": self.player_1_score,
                "player_2": self.player_2.player_id,
                "player_2_score": self.player_2_score,
                "winner": self.winner,
                "match_id": self.match_id}
