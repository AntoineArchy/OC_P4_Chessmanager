import os
from typing import Dict

from tinydb import TinyDB
from data import config

FILES_NAME = [config.PLAYER_DB_NAME, config.TOURNAMENT_DB_NAME, config.TURN_DB_NAME, config.MATCH_DB_NAME]

save_directory = config.SAVE_DIRECTORY
full_save_path = os.path.join(os.getcwd(), save_directory)


def get_file_path_from_name(file_name: str) -> str:
    """
    Construit un path complet à partir du nom de fichier fournit
    """
    return os.path.join(full_save_path, f"{file_name}.json")


# Si le répertoire de sauvegarde n'existe pas, on le créer directement
if not os.path.exists(full_save_path):
    os.mkdir(full_save_path)


class TinyDBLoader:
    def __init__(self):
        """
        Loader principal de l'application, gère la création et la mise à jour des bases de données et de l'indexation
        des objets dans les bases.
        Repose sur TinyDB,peut être remplacer par un autre module reprennant les mêmes noms de méthode sans modifier
        d'autres fichiers de l'application.
        """
        db_dict = {db_name: TinyDB(get_file_path_from_name(db_name), sort_keys=True, indent=4, separators=(',', ': '))
                   for db_name in FILES_NAME}
        self.db_dict = db_dict

    def get_db_handle(self, db_file: str) -> TinyDB:
        """
        Reçoit le nom d'un fichier de base de donnée et retourne un objet TinyDB chargé
        """
        working_database = self.db_dict.get(db_file, None)
        if working_database is None:
            print(f"Something went wrong while loading db {db_file}")
        return working_database

    def get_nbr_db_entry(self, db_name: str) -> int:
        """
        Reçoit le nom d'un fichier de base de donnée et retourne le nombre d'entrée qu'il contient
        """
        working_database = self.get_db_handle(db_name)
        return len(working_database)

    def id_exist_in_db(self, working_db: TinyDB, entry_id: int) -> bool:
        """
        Reçoit un objet de base de donnée et l'id d'une entrée, retourne si l'entrée éxiste ou non en base
        """
        working_database = working_db
        return working_database.contains(doc_id=entry_id)

    def save_player(self, player_data_dict: Dict) -> int:
        working_database = self.get_db_handle(config.PLAYER_DB_NAME)
        doc_id = working_database.insert(player_data_dict)
        return doc_id

    def load_player(self, player_id: int) -> bool | Dict:
        working_database = self.get_db_handle(config.PLAYER_DB_NAME)
        if not self.player_exist(player_id):
            return False
        player_data = working_database.get(doc_id=player_id)
        player_data["player_id"] = player_id
        return player_data

    def player_exist(self, player_id: int) -> bool:
        working_database = self.get_db_handle(config.PLAYER_DB_NAME)
        return self.id_exist_in_db(working_database, player_id)

    def save_tournament(self, tournament_data_dict: Dict) -> int:
        tournament_index = tournament_data_dict.get('tournament_id', -1)

        if tournament_index == -1:
            doc_id = self._insert_tournament(tournament_data_dict)
            tournament_data_dict['tournament_id'] = doc_id

        doc_id = self._update_tournament(tournament_data_dict)
        return doc_id

    def _insert_tournament(self, tournament_dict: Dict) -> int:
        working_database = self.get_db_handle(config.TOURNAMENT_DB_NAME)
        doc_id = working_database.insert(tournament_dict)
        return doc_id

    def _update_tournament(self, tournament_dict: Dict) -> int:
        working_database = self.get_db_handle(config.TOURNAMENT_DB_NAME)
        doc_id = tournament_dict.get('tournament_id')

        working_database.update(tournament_dict, doc_ids=[doc_id])  # , tournament.doc_id == doc_id)
        return doc_id

    def load_tournament_data(self, tournament_id: int) -> Dict | bool:
        working_database = self.get_db_handle(config.TOURNAMENT_DB_NAME)
        if not self.tournament_exist(tournament_id):
            return False
        tournament_data = working_database.get(doc_id=tournament_id)

        return tournament_data

    def tournament_exist(self, tournament_id: int) -> bool:
        working_database = self.get_db_handle(config.TOURNAMENT_DB_NAME)
        return self.id_exist_in_db(working_database, tournament_id)

    def _insert_match(self, match_data: Dict) -> int:
        working_database = self.get_db_handle(config.MATCH_DB_NAME)
        doc_id = working_database.insert(match_data)
        return doc_id

    def _update_match(self, match_data: Dict) -> int:
        working_database = self.get_db_handle(config.MATCH_DB_NAME)
        doc_id = match_data.get('match_id')

        working_database.update(match_data, doc_ids=[doc_id])
        return doc_id

    def save_match(self, match_data: Dict) -> int:
        working_database = self.get_db_handle(config.MATCH_DB_NAME)
        if not self.id_exist_in_db(working_database, match_data.get('match_id', -1)):
            doc_id = self._insert_match(match_data)
            match_data['match_id'] = doc_id

        doc_id = self._update_match(match_data)
        return doc_id

    def load_match(self, match_id: int) -> Dict | bool:
        working_database = self.get_db_handle(config.MATCH_DB_NAME)
        if not self.id_exist_in_db(working_database, match_id):
            return False
        match_data = working_database.get(doc_id=match_id)
        match_data["match_id"] = match_id
        return match_data

    def _insert_turn(self, turn_data: Dict) -> int:
        working_database = self.get_db_handle(config.TURN_DB_NAME)
        doc_id = working_database.insert(turn_data)
        return doc_id

    def _update_turn(self, turn_data: Dict) -> int:
        working_database = self.get_db_handle(config.TURN_DB_NAME)
        doc_id = turn_data.get('turn_id')

        working_database.update(turn_data, doc_ids=[doc_id])  # , tournament.doc_id == doc_id)
        return doc_id

    def load_turn(self, turn_id: int) -> Dict | bool:
        working_database = self.get_db_handle(config.TURN_DB_NAME)
        if not self.id_exist_in_db(working_database, turn_id):
            return False
        turn_data = working_database.get(doc_id=turn_id)
        turn_data["turn_id"] = turn_id
        return turn_data

    def save_turn(self, turn_data: Dict) -> int:
        working_database = self.get_db_handle(config.TURN_DB_NAME)
        if not self.id_exist_in_db(working_database, turn_data.get('turn_id', -1)):
            doc_id = self._insert_turn(turn_data)
            turn_data['turn_id'] = doc_id

        doc_id = self._update_turn(turn_data)
        return doc_id
