from typing import Dict

from chess_manager.M import tournament_model


def tournament_creation_form() -> Dict:
    """Retourne la liste des questions correspondantes aux variables necessaries à la création d'un nouveau tournoi"""
    return dict(name="What's your tournament name ?",
                place="Where is your tournament taking place ?",
                description="Enter tournament description",
                turn_nbr="How many turn in this tournament (Press 'A' for Auto)",
                player_nbr="How many players are signed to this tournament ?")


def on_going_tournament_view(tournament_obj: tournament_model.TournamentM) -> str:
    """
    Reçoit un objet tournoi en cours et en retourne la représentation des informations d'identification du tournoi
    """
    return f"Tournament : {tournament_obj.name}\n" \
           f"At : {tournament_obj.place} \n" \
           f"Description : {tournament_obj.description} \n" \
           f"Started {tournament_obj.start_date} - On going \n" \
           f"Actual turn : {tournament_obj.get_current_turn_nbr()} / {tournament_obj.turn_nbr}\n" \
           f"Registered players : {len(tournament_obj.players)} / {tournament_obj.player_nbr}\n"


def finished_tournament_view(tournament_obj: tournament_model.TournamentM) -> str:
    """Reçoit un objet tournoi terminé et en retourne la représentation des informations d'identification du tournoi"""
    return f"Tournament : {tournament_obj.name}\n" \
           f"At : {tournament_obj.place} \n" \
           f"Description : {tournament_obj.description} \n" \
           f"Started {tournament_obj.start_date} - Ended {tournament_obj.end_date}\n" \
           f"Registered players : {len(tournament_obj.players)} / {tournament_obj.player_nbr}\n"


def tournament_obj_view(tournament_obj: tournament_model.TournamentM) -> str:
    """Reçoit un objet tournoi en cours et en retourne la représentation vue adaptée"""
    if tournament_obj.is_finished:
        return finished_tournament_view(tournament_obj)
    return on_going_tournament_view(tournament_obj)


def tournament_object_flat_view(tournament_obj: tournament_model.TournamentM) -> str:
    """
    Reçoit un objet tournoi et en retourne une représentation en ligne suffisante pour l'identification du tournoi
    dans une liste
    """
    return f"{tournament_obj.name} at {tournament_obj.place} : " \
           f"{len(tournament_obj.turn_list)}/{tournament_obj.turn_nbr} turn, " \
           f"Started {tournament_obj.start_date}"


def tournament_object_full_view(tournament_full_data, max_match_name_len, max_match_detail_len):
    """
    Reçoit un dictionnaire des informations complètes d'un objet tournoi et en retourne la représentation
    complète des tours et matchs du tournoi mis en forme
    """

    to_display = list()

    turn_names = [turn[0] for turn in tournament_full_data]
    turn_stamps = [turn[1] for turn in tournament_full_data]
    max_turn_name_len = max(map(len, turn_names))
    max_time_len = max(map(len, turn_stamps))

    separator = f"{'#' * (max_turn_name_len + max_time_len + max_match_name_len + max_match_detail_len + 5)}"
    to_display.append(separator)

    for turn in tournament_full_data:
        turn_entete = f"#{turn[0]}{' ' * (max_turn_name_len - len(turn[0]))}" \
                      f"#{turn[1]}{' ' * (max_time_len - len(turn[1]))}" \
                      f"#{'-' * max_match_name_len}" \
                      f"#{'-' * max_match_detail_len}#"
        to_display.append(turn_entete)
        for match_name, match_flat_view in turn[2]:
            match_display = f"#{'-' * max_turn_name_len}" \
                            f"#{'-' * max_time_len}" \
                            f"#{match_name}{' ' * (max_turn_name_len - len(match_name))}" \
                            f"#{match_flat_view}{' ' * (max_match_detail_len - len(match_flat_view))}#"
            to_display.append(match_display)
        to_display.append(separator)
    return to_display
