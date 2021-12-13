import pymysql
import datetime

class MysqlController:
    def __init__(self, host, port, id, pw, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.conn = pymysql.connect(host=host, port=int(port), user=id, password=pw, db=db_name, charset='utf8')
        self.curs = self.conn.cursor()

    def _connection_info(self):
        print("*** CONNECTION INFORMATION ***")
        print(f"*  host : {self.host}")
        print(f"*  port : {self.port}")
        print(f"*  db_name : {self.db_name}")
        print('*'*30)

    # temp function(insertion)
    def insert(self, table_name : str = None, line : dict = None):
        columns = ','.join(line.keys())
        placeholders = ','.join(["%s"]*len(line))
        sql_command = """INSERT INTO %s(%s) VALUES(%s)"""%(table_name, columns, placeholders)
        self.curs.execute(sql_command, tuple(str(val) for val in line.values()))
        self.conn.commit()

    def upsert(self, table_name : str = None, line : dict = None, update : str = None):
        columns = ",".join(line.keys())
        placeholders = ",".join(['%s']*len(line))
        sql_command = f"""INSERT INTO {table_name}({columns}) 
                        VALUES({placeholders})
                        ON DUPLICATE KEY UPDATE {update} = '{line[update]}';
                        """
        try:
            self.curs.execute(sql_command, tuple(str(val) for val in line.values()))
            self.conn.commit()
        except Exception as e:
            print(e)
            print(sql_command)