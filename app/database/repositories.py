from .mysql import MySQLRepository
import logging

logger = logging.getLogger(__name__)


class CaseRepository:
    def __init__(self, config):
        logger.info(f"__init__:")
        logger.debug(f"{self}, {config}")
        
        self.repository = MySQLRepository(config)

    def execute(self, query):
        logger.info(f"in execute:")
        logger.debug(f"{self}, {query}")
        # print(query)

        self.repository.connect()
        result = self.repository.execute_query(query)
        self.repository.disconnect()
        return result if result else None




# Samples
class UserRepository:
    def __init__(self, config):
        self.repository = MySQLRepository(config)

    def get_user_by_id(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        self.repository.connect()
        result = self.repository.execute_query(query)
        self.repository.disconnect()
        return result[0] if result else None

class ProductRepository:
    def __init__(self, config):
        self.repository = MySQLRepository(config)

    def get_product_by_id(self, product_id):
        query = f"SELECT * FROM products WHERE id = {product_id}"
        self.repository.connect()
        result = self.repository.execute_query(query)
        self.repository.disconnect()
        return result[0] if result else None

