from enum import Enum, auto


class AppInput(Enum):
    """
    Conteneur des différents inputs et actions qui sont appelé par l'utilisateur et les contrôleurs de l'application
    """
    # Match input
    NEW_MATCH = auto()
    LOAD_MATCH = auto()
    MATCH_FLAT_VIEW = auto()
    VIEW_MATCH_LIST = auto()
    BACK_TO_MATCH_LIST = auto()
    SET_MATCH_ACTIV = auto()
    SET_MATCH_WINNER = auto()

    # Turn input
    NEW_TURN = auto()
    LOAD_TURN = auto()
    NEXT_TURN = auto()
    VIEW_TURN_LIST = auto()
    TURN_FULL_vieW = auto()
    BACK_TO_TURN_LIST = auto()
    SET_TURN_ACTIV = auto()
    DISPLAY_TURN_RANKING = auto()

    # PLayer input
    NEW_PLAYER = auto()
    LOAD_PLAYER = auto()
    ADD_PLAYER = auto()
    PLAYER_FULL_VIEW = auto()
    PLAYER_FLAT_VIEW = auto()
    VIEW_PLAYER_LIST = auto()
    NEXT_PLAYER_PAGE = auto()
    PREV_PLAYER_PAGE = auto()

    # Tournament input
    NEW_TOURNAMENT = auto()
    RESUME_TOURNAMENT = auto()
    SET_TOURNAMENT_ACTIV = auto()
    TOURNAMENT_RANKING = auto()
    NEXT_TOURNAMENT_PAGE = auto()
    PREV_TOURNAMENT_PAGE = auto()
    VIEW_TOURNAMENT_LIST = auto()
    BACK_TO_TOURNAMENT_LIST = auto()

    # Main app input
    MAIN_MENU = auto()
    QUIT = auto()

