import yaml
import pprint as debug
import psycopg2


class Database:
    
    _dbparams = {}

    def __init__(self):
        with open(r'dbparams.yaml') as file:
            Database._dbparams = yaml.load(file, Loader=yaml.FullLoader)

    def connect(self):
        '''
            Sets up the connection with the database\n
            Returns:
            -----------
                \t psycopg2.connection
        '''
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
                                    points INT,
                                    guild_id BIGINT REFERENCES guilds(id) 
                                    ON DELETE CASCADE
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
        table = table.replace(" ", "")
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                self.data = cursor.fetchall()
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
        print(values)
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
                \tpoints: int
            Returns:
            -----------
                \tBoolean
        '''
        if not self.connection!=0:
            return False
        if not table or not member_id or not points:
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
    #db.createTable('TEST')
    #db.dropTable('bottesting')
    #data = db.selectAll('guilds')
    #debug.pprint(data)
    #print(db.getPoints('☢Ƀu₹₦€₹$☢', 420058166651256842))
    #db.setPoints('☢Ƀu₹₦€₹$☢', 729270168030543954, 84)
    #data = db.selectCol('guilds', 'test')
    #debug.pprint(data)
    db.close_connection()