import threading

from db import functions_db

exitFlag = 0


class Thread_main_downloader(threading.Thread):
    def __init__(self, threadID, name, chemin_db):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.chemin_db = chemin_db

    def run(self):
        while True:
            non_traite = functions_db.read_db_non_traite(functions_db.get_db_connection(self.chemin_db))
