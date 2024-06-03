import mysql.connector
import logging

logger = logging.getLogger(__name__)

class MySQLRepository:
    def __init__(self, config):
        logger.info(f"__init__:")
        logger.debug(f"{self}, {config}")

        self.config = config
        self.connection = None

    def connect(self):
        logger.info(f"in connect:")
        logger.debug(f"{self}")

        self.connection = mysql.connector.connect(**self.config)

    def disconnect(self):
        logger.info(f"in disconnect:")
        logger.debug(f"{self}")

        if self.connection:
            logger.debug(f"closing the connnection...")
            self.connection.close()
            logger.debug(f"connnection closed")

    def execute_query(self, query):
        logger.info(f"in execute_query:")
        logger.debug(f"{self} {query}")
        try:
            # cursor = self.connection.cursor(dictionary=True) #result in json
            # cursor.execute(query)
            # result = cursor.fetchall()
            # cursor.close()

            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            cols = [i[0] for i in cursor.description]
            cursor.close()
            result = {
                'rows': rows,
                'cols': cols
            }

            return result
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return None
