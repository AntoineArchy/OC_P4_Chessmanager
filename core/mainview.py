from __future__ import annotations

from typing import Dict, List, Any

import questionary


class MainView:
    """
    Vue principale de l'application
    Reçoit les informations à afficher de la part des différents contrôleurs ainsi que les formulaires à remplir.

    [Utilise actuellement questionary pour les formulaires et vérificateurs, pourrait être mis à jour pour
    afficher un gui basique (ex: tkinter) sans modification des autres fichiers utiles au fonctionnement de
    l'application]
    """

    def __init__(self):
        self.title = None
        self.menu_title = None
        self.display_blocks = list()

    def display_title(self) -> None:
        print(self.title)

    def display_menu_title(self) -> None:
        print(self.menu_title)

    def add_to_display(self, display_bloc: str) -> None:
        self.display_blocks.append(display_bloc)

    def add_blocks(self, blocs: List[str]) -> None:
        for display_bloc in blocs:
            self.add_to_display(display_bloc)

    def display_display_bloc(self) -> None:
        for block in self.display_blocks:
            print(block)

    def flip_display(self) -> None:
        """
        "Boucle" principale de l'affichage, le titre et le nom du menu sont conservé, les autres éléments affichés
        sont purgés.
        """
        if self.title is not None:
            self.display_title()

        if self.menu_title is not None:
            self.display_menu_title()

        if self.display_blocks:
            self.display_display_bloc()
            self.display_blocks.clear()

    def get_form_answer(self, form_question: dict, validator: Dict | None = None) -> Dict:
        """
        Usine de formulaire, reçoit un dict {nom_de_variable : texte, ...}
        et un dict (optionnel) {nom_de_variable : validateur, ...},
        retourne un dict {nom_de_variable : input_utilisateur, ...} conforme aux validateurs fournit
        """
        if validator is None:
            validator = dict()

        for var, question in form_question.items():
            form_question[var] = questionary.text(message=question,
                                                  validate=validator.get(var, None))
        form = questionary.form(**form_question)
        answer = form.ask()
        return answer

    def get_user_select(self, message, allowed_input: dict) -> Any:
        """
        "Boucle" principale du traitement des inputs utilisateur,
        reçoit un message à afficher ainsi qu'un dict de {texte_a_afficher : valeur_a_retourner_en_cas_de_selection, ...}
        """
        choices = list(allowed_input)
        user_select = questionary.select(
            message,
            choices=choices).ask()
        return allowed_input.get(user_select)
