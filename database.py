import yaml
import pprint as debug
import psycopg2


class Database:
    _dbparams = {}
    def __init__(self):
        with open(r'dbparams.yaml') as file:
            Database._dbparams = yaml.load(file, Loader=yaml.FullLoader)

    def connect(self):
        self.connection = psycopg2.connect(dbname=Database._dbparams['DB_NAME'], 
                                  user=Database._dbparams['DB_USER'],
                                  password=Database._dbparams['DB_PASS'],
                                  host=Database._dbparams['DB_HOST'],
                                  port=Database._dbparams['DB_PORT']
                                )
        return self.connection

    def showall(self, table):
            if not self.connection!=0:
                return None
            
            with self.connection.cursor() as cursor:
                try:
                    cursor.execute(f"SELECT * FROM {table}")
                    self.data = cursor.fetchall()
                except:
                    print("ERROR")
                    return None

            return self.data

    def insert(self, table, *values):
        if not self.connection:
            return False
        if not table or not values:
            return False

        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"INSERT INTO {table} values(%s, %s, %s, %s, %s)", (values[0], values[1], values[2], values[3], values[4],))
                self.connection.commit()
            except psycopg2.errors.UniqueViolation:
                print(f"DUBLICATE id {values[0]} already exist")
                return False

        return True

    def delete(self, table, id):
        if not self.connection:
            return False
        if not table or not id:
            return False

        with self.connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table} WHERE id=%s", (id,))
            self.connection.commit()
        return True


    def close_connection(self):
        if self.connection.closed != 0: #IF CONNECTION CLOSED
            return False
        self.connection.close()
        return True  


if __name__=="__main__":
    db = Database()
    db.connect()
    data = db.showall('guilds')
    debug.pprint(data)
    db.insert('guilds', 102, 'Poker', True, 123, 999)
    data = db.showall('guilds')
    debug.pprint(data)
    db.close_connection()