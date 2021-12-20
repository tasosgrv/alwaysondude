import yaml
import pprint as debug
import psycopg2
import os
import datetime



class Database:
    
    _DATABASE_URL = ''
    _HEROKU = False
    _dbparams = {}

    def __init__(self):
        if Database._HEROKU:
            Database._DATABASE_URL = os.environ['DATABASE_URL']
        else:
            with open(r'data/dbparams.yaml') as file:
                Database._dbparams = yaml.load(file, Loader=yaml.FullLoader)

    def connect(self):
        '''
            Sets up the connection with the database\n
            Returns:
            -----------
                \t psycopg2.connection
        '''
        if Database._HEROKU: 
            self.connection = psycopg2.connect(Database._DATABASE_URL, sslmode='require')
        else:
            self.connection = psycopg2.connect(dbname=Database._dbparams['DB_NAME'], 
                                  user=Database._dbparams['DB_USER'],
                                  password=Database._dbparams['DB_PASS'],
                                  host=Database._dbparams['DB_HOST'],
                                  port=Database._dbparams['DB_PORT']
                                )
        return self.connection

    def createTable(self, table):
        '''
            Creates a new table with a given name\n
            Parameters:
            -----------
                \ttable: String\n
            Return:
            ----------- 
                \tBoolean
        '''
        if not self.connection!=0:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table} (
                                    id BIGINT PRIMARY KEY,
                                    name VARCHAR(32) NOT NULL,
                                    discriminator INT NOT NULL,
                                    bot BOOLEAN NOT NULL,
                                    nick VARCHAR(32),  
                                    chunked BOOLEAN NOT NULL,
                                    points REAL,
                                    guild_id BIGINT REFERENCES guilds(id) 
                                    ON DELETE CASCADE,
                                    dailyreward timestamp
                                )
                               ''')
                self.connection.commit()
            except:
                print("ERROR on table creation")
                return None

        return True

    def dropTable(self, table):
        '''
            Deletes a table with a given name if exists\n
            Parameters: 
            -----------
            table: String\n
            Return: 
            -----------
            Boolean
        '''
        if not self.connection!=0:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"DROP TABLE {table}")
                self.connection.commit()
            except:
                print("ERROR on table creation")
                return None

        return True

    def selectAll(self, table):
        '''
            Returns all the elements of specific table\n
            Parameters:\n
            -----------
                \ttable: String\n
            Return:\n
            -----------
                \tA List of tuples or None 
        '''
        if not self.connection!=0:
            return None
        if not table:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                self.data = cursor.fetchall()
            except:
                print("ERROR")
                return None

        return self.data


    def getLeaderboard(self, table, limit, offset=None):
        '''
            Returns a leaderboard for points\n
            Parameters:\n
            -----------
                \ttable: String\n
                \tlimit: int\n
            Return:\n
            -----------
                \tA List of tuples or None 
        '''
        if not self.connection!=0:
            return None
        if not table or not limit:
            return None
        if offset is None:
            offset=0
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT name,points FROM {table} WHERE bot is False ORDER BY points DESC LIMIT {limit} OFFSET {offset*limit}")
                self.data = cursor.fetchall()
            except:
                print("ERROR")
                return None

        return self.data

    def getCirculatingSupply(self, table):
        '''
            Returns the circuleting supply (the points of the users except bots) of points in a certain guild\n
            Parameters:
            -----------
                \table: String\n
            Return:
            -----------
                \tint or None 
        '''
        if not self.connection!=0:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT SUM(points) FROM {table} WHERE bot is False;")
                self.data = cursor.fetchone()[0]
            except:
                print("ERROR")
                return None

        return self.data

    def getTotalSupply(self, table):
        '''
            Returns the total supply of points in a certain guild\n
            Parameters:
            -----------
                \table: String\n
            Return:
            -----------
                \tint or None 
        '''
        if not self.connection!=0:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT SUM(points) FROM {table};")
                self.data = cursor.fetchone()[0]
            except:
                print("ERROR")
                return None

        return self.data
    
    def insert(self, table, *values):
        '''
            Gets a list of values and inserts them into a specified table\n
            Parameters:
            -----------
                \ttable: String\n
                \tvalues: List\n
            Return:
            -----------
                \tBoolean
        '''
        if not self.connection:
            return False
        if not table or not values:
            return False
        table = table.replace(" ", "")
        query = "INSERT INTO "+table+" values("+"%s,"*(len(values)-1)+"%s) ON CONFLICT DO NOTHING"
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query, values)
                self.connection.commit()
            except psycopg2.errors.UniqueViolation:
                print(f"DUBLICATE id {values[0]} already exist")
                return False
            except psycopg2.errors.SyntaxError:
                print(f"INSERT has more expressions than table {table}")
                return False
        return True

    def getPoints(self, table, member_id):
        '''
            Returns the points of a certain member\n
            Parameters:
            -----------
                \tmember_id: int\n
            Return:
            -----------
                \tint or None 
        '''
        if not self.connection!=0:
            return None
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT points FROM {table} WHERE id='%s'", (member_id,))
                self.data = cursor.fetchone()[0]
            except:
                print("ERROR")
                return None

        return self.data

    def setPoints(self, table, member_id, points):
        '''
            Sets the points of a certain member into the database\n
            Parameters:
            -----------
                \ttable: String\n
                \tmember_id: int\n
                \tpoints: float
            Returns:
            -----------
                \tBoolean
        '''
        if not self.connection!=0:
            return False
        if not table or not member_id:
            return False
        if points<0:
            return False 
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"UPDATE {table} SET points='%s' WHERE id='%s'", (points, member_id,))
                self.connection.commit()
            except:
                print("ERROR on update")
                return False

        return True

    def transferPoints(self, table, sender_id, points, receiver_id):
        '''
            Transfers points from a user to another user in the same guild (table) \n
            Parameters:
            -----------
                \ttable: String\n
                \tsender_id: int\n
                \tpoints: float\n
                \treceiver_id
            Returns:
            -----------
                \tBoolean
        '''
        if not self.connection!=0:
            return False
        if not table or not sender_id or not receiver_id:
            return False
        if points<0:
            return False
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT points FROM {table} WHERE id='%s'", (sender_id,))
                sender_new = cursor.fetchone()[0] - points
                cursor.execute(f"UPDATE {table} SET points='%s' WHERE id='%s'", (sender_new, sender_id,))
                
                cursor.execute(f"SELECT points FROM {table} WHERE id='%s'", (receiver_id,))
                receiver_new = cursor.fetchone()[0] + points
                cursor.execute(f"UPDATE {table} SET points='%s' WHERE id='%s'", (receiver_new, receiver_id,))
                self.connection.commit()
            except Exception as e:
                print(e)
                return False

        return True

        


    def betPlaced(self, table, member_id, bet_amount, game, win):
        '''
            Place a new bet from a user into database, increases the bet counter column and adds the bet amount to the total wagered:
            -----------
                \ttable: String\n
                \tmember_id: int\n
                \tbet_amount: float
            Returns:
            -----------
                \tBoolean
        '''

        if not self.connection!=0:
            return False
        if not table or not game or not member_id:
            return False
        if bet_amount<0:
            return False
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT {game},wagered,winnings FROM {table} WHERE id='%s'", (member_id,))
                player_game, player_wagered, player_winnings = cursor.fetchone()
                player_game+=1
                player_wagered+=bet_amount
                player_winnings+=win
                cursor.execute(f"UPDATE {table} SET {game}='%s', wagered='%s', winnings='%s' WHERE id='%s'", (player_game, player_wagered, player_winnings, member_id,))
                self.connection.commit()
            except Exception as e:
                print(e)
                return False

        return True



    def delete(self, table, id):
        '''
            Deletes a row from a specified table\n
            Parameters:
            -----------
                \ttable: String\n
                \tid: int\n
            Return:
            -----------
                \tBoolean
        '''
        if not self.connection:
            return False
        if not table or not id:
            return False
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table} WHERE id=%s", (id,))
            self.connection.commit()
        return True


    def setDailyRewardTime(self, table, member_id, time):
        '''
            Sets the time of the claimed daily reward for a certain member into the database\n
            Parameters:
            -----------
                \ttable: String\n
                \tmember_id: int\n
                \time: datetime
            Returns:
            -----------
                \tBoolean
        '''
        if not self.connection:
            return False
        if not table or not member_id:
            return False
        if not time:
            return False 
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"UPDATE {table} SET dailyreward=%s WHERE id='%s'", (time, member_id,))
                self.connection.commit()
            except Exception as e:
                print(f"ERROR on setDailyRewardTime: {e}")
                return False

        return True

    def getDailyRewardTime(self, table, member_id):
        '''
            Returns the datetime of the last clamed daily reward of a certain member\n
            Parameters:
            -----------
                \tmember_id: int\n
            Return:
            -----------
                \tdatetime or None 
        '''
        if not self.connection:
            return None
        if not table or not member_id:
            return False
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT dailyreward FROM {table} WHERE id='%s'", (member_id,))
                self.data = cursor.fetchone()[0]
            except Exception as e:
                print(f"ERROR on getDailyRewardTime: {e}")
                return None

        return self.data


    def close_connection(self):
        '''
        Closes the connection with the database\n
        Return:
        -----------
            \tBoolean
        '''
        if self.connection.closed != 0: #IF CONNECTION CLOSED
            return False
        self.connection.close()
        return True  


if __name__=="__main__":
    db = Database()
    db.connect()

    
    db.setDailyRewardTime("☢Ƀu₹₦€₹$☢", 786033389751762944, datetime.datetime.now())
    t = db.getDailyRewardTime("☢Ƀu₹₦€₹$☢", 786033389751762944)
    print(t)
    #print(db.getLeaderboard('☢Ƀu₹₦€₹$☢', 10))
    #print(db.betPlaced('☢Ƀu₹₦€₹$☢',420058166651256842 , 1, "coinflip", 2))
    #db.createTable('TEST')
    #db.dropTable('bottesting')
    #data = db.selectAll('guilds')
    #debug.pprint(data)
    #print(db.getPoints('☢Ƀu₹₦€₹$☢', 420058166651256842))
    #db.setPoints('☢Ƀu₹₦€₹$☢', 729270168030543954, 84)
    #data = db.selectCol('guilds', 'test')
    #debug.pprint(data)
    db.close_connection()