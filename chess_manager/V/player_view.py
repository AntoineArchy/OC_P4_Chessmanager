from typing import Dict

from chess_manager.M import player_model


def player_object_full_view(player: player_model.PlayerM) -> str:
    """Reçoit un objet joueur et en retourne la représentation des informations complète"""
    return f"Player :\n" \
           f"- first name : {player.first_name.capitalize()}\n" \
           f"- last_name : {player.last_name.upper()}\n" \
           f"- birthday : {player.birthday}\n" \
           f"- INE : {player.ine.upper()}"


def see_player_as_line(player: player_model.PlayerM) -> str:
    """
    Reçoit un objet joueur et en retourne une représentation en ligne suffisante pour l'identification du joueur
    dans une liste
    """
    return f"{player.last_name.upper()} {player.first_name.capitalize()} ({player.ine.upper()})"


def player_creation_form() -> Dict:
    """Retourne la liste des questions correspondantes aux variables necessaries à la création d'un nouveau joueur"""
    return {"first_name": "What's your player first name?",
            "last_name": "What's your player last name?",
            "birthday": "What's your player birthday?",
            "ine": "What's your player INE ?", }


def no_existing_player_error() -> str:
    """Affiche une erreur en cas de tentative de chargement de la liste des joueurs si la base de donnée vide"""
    return "It seems like you doesn't have any player to show here"
