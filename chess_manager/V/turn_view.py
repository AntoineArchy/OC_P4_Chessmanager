from chess_manager.M import turn_model


def turn_object_flat_view(turn: turn_model.TurnM) -> str:
    """
    Reçoit un objet tour et en retourne la représentation
    """
    nbr_of_match = len(turn.match_list)
    finished_match = len([match for match in turn.match_list if match.winner is not None])
    return f"{turn.name}" \
           f"{' (Finished)' if nbr_of_match == finished_match else ' (on going)'}:" \
           f" {finished_match}/{nbr_of_match} matches finished."
