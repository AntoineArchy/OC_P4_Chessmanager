from chess_manager.M import match_model


def see_on_going_match(match: match_model.MatchM) -> str:
    """Reçoit un objet match en cours et en retourne la représentation"""
    return f"{match.player_1.last_name.upper()} {match.player_1.first_name.capitalize()} " \
           f"({match.player_1_score} pts) VS " \
           f"{match.player_2.last_name.upper()} {match.player_2.first_name.capitalize()} " \
           f"({match.player_1_score} pts)" \
           f"{'Still going'}"


def see_finished_match(match: match_model.MatchM) -> str:
    """Reçoit un objet match terminé et en retourne la représentation"""
    return f"{match.player_1.last_name.upper()} {match.player_1.first_name.capitalize()} " \
           f"({match.player_1_score} pts) {'WINNER ' if match.player_1.player_id == match.winner else ''}VS " \
           f"{match.player_2.last_name.upper()} {match.player_2.first_name.capitalize()} " \
           f"({match.player_2_score} pts) {'WINNER' if match.player_2.player_id == match.winner else ''}" \
           f"{'Draw' if not match.winner else ''}"


def see_match_as_line(match: match_model.MatchM) -> str:
    """Reçoit un objet match et en retourne la représentation correspondante au statut du match"""
    if match.winner is None:
        return see_on_going_match(match)
    return see_finished_match(match)
