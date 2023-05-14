from core import messenger, tinydb_loader, mainview
from chess_manager.C import turn_controller, player_controller, tournament_controller, match_controller

from data.config import AppInput


class ChessManager:
    def __init__(self):
        """
        Classe principale de l'application, initialise le core de l'application et les différents contrôleurs,
        Est également résponsable de la boucle principale de l'application, voir run().
        """
        self.messenger = messenger.Messenger()
        self.main_v = mainview.MainView()
        self.loader = tinydb_loader.TinyDBLoader()

        player_controller.PlayerC(loader=self.loader, main_view=self.main_v, app_messenger=self.messenger)
        tournament_controller.TournamentC(loader=self.loader, main_view=self.main_v, app_messenger=self.messenger)
        turn_controller.TurnC(loader=self.loader, main_view=self.main_v, app_messenger=self.messenger)
        match_controller.MatchC(loader=self.loader, main_view=self.main_v, app_messenger=self.messenger)

        self.main_v.title = "## ChessManager ##"

        self.messenger.register_call_event(AppInput.MAIN_MENU, self.set_to_main_menu, "Go back to main menu")
        self.messenger.register_call_event(AppInput.QUIT, None, "Quit")

        self.set_to_main_menu()

    def set_to_main_menu(self):
        """
        Helper fonction pour le retour au menu principal de l'application.
        """
        self.main_v.menu_title = "## Main menu ##"
        self.messenger.ignore_all()
        self.messenger.accept_multiple_event([
            (AppInput.NEW_PLAYER, None),
            (AppInput.VIEW_PLAYER_LIST, [None]),
            (AppInput.NEW_TOURNAMENT, None),
            (AppInput.VIEW_TOURNAMENT_LIST, None),
            (AppInput.QUIT, None)
        ])

    def register_user_input(self):
        """
        Unique poit d'entrée des actions utilisateur;
        Récupére la liste des événement enregistré, disponible et nommé auprès du messenger de l'application,
        en affiche une représentation sur la vue principale
        retourne l'événement sélectionner par l'utilisateur.
        """
        allowed = self.messenger.get_allowed_event_and_str()

        allowed_list = [(input_str, input) for input_str, input in allowed.items()]

        registered = [allowed for allowed in allowed_list if isinstance(allowed[1], AppInput)]
        unregister = [allowed for allowed in allowed_list if allowed not in registered]

        sorted_registered = sorted(registered, key=lambda individual_app_input: individual_app_input[1].value)

        allowed_as_dict = {input_str: input_event for input_str, input_event in [*unregister, *sorted_registered]}
        user_input = self.main_v.get_user_select("What do you want to do ?", allowed_as_dict)
        return user_input

    def run(self):
        """
        Boucle principale de l'application.
        Tant que l'utilisateur ne choisit pas de quitter l'application :
            Affiche les élément en attente d'affichage sur la vue principale,
            Récupére l'action utilisateurs,
            Exécute l'action
            Recommence
        """
        run = True
        while run:
            self.main_v.flip_display()

            user_input = self.register_user_input()

            if user_input == AppInput.QUIT:
                break
            self.messenger.handle_event(user_input)


if __name__ == "__main__":
    app = ChessManager()
    app.run()