import sqlite3 as sq

class DataBase:
    def __init__(self):
        self.db = sq.connect('data.db')
        self.cursor = self.db.cursor()
    
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS accs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone TEXT,
                        api_id TEXT,
                        api_hash TEXT,
                        state INT);
        ''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        access_hash TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        phone TEXT,
                        where_link TEXT,
                        sending INT);
        ''')
                
    def db_add_acc(self, phone, api_id, api_hash):
        self.cursor.execute(f'INSERT INTO accs (phone, api_id, api_hash, state) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING', (phone, api_id, api_hash, 0))
        self.db.commit()
    
    def db_show_all_accs(self):
        self.cursor.execute('SELECT phone FROM accs')
        all_accs = self.cursor.fetchall()
        self.db.commit()
        return all_accs
    
    def db_change_acc_state(self, phone, state):
        self.cursor.execute(f'UPDATE accs SET state = ? WHERE phone = ?', (state, phone))
        self.db.commit()
        
    def db_get_all_accs(self):
        self.cursor.execute('SELECT * FROM accs WHERE state = ?', (1, ))
        all_accs = self.cursor.fetchall()
        self.db.commit()
        return all_accs    
        
    def db_add_users(self, users):
        self.cursor.executemany(f'INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING', users)
        all_accs = self.cursor.fetchall()
        self.db.commit()
        return all_accs
    
    def db_get_all_users_name(self):
        self.cursor.execute(f'SELECT username FROM users')
        all_name = self.cursor.fetchall()
        all_name = [i[0] for i in all_name]
        self.db.commit()
        return all_name
    
    def db_get_all_users_ids(self):
        self.cursor.execute(f'SELECT id FROM users')
        all_id = self.cursor.fetchall()
        all_id = [i[0] for i in all_id]
        self.db.commit()
        return all_id
    
    def db_get_all_users(self):
        self.cursor.execute(f'SELECT * FROM users')
        all_users = self.cursor.fetchall()
        all_users = [list(i) for i in all_users]
        self.db.commit()
        return all_users
    
    def db_change_user_state(self, name):
        self.cursor.execute(f'UPDATE users SET sending = ? WHERE username = ?', (0, name))
        self.db.commit()