from app.service.services import UserService, ProductService
from app.database.repositories import UserRepository, ProductRepository
from config.settings import DATABASE_CONFIG
import logging

logger = logging.getLogger(__name__)

# Initialize repositories with database configuration
user_repository = UserRepository(DATABASE_CONFIG)
product_repository = ProductRepository(DATABASE_CONFIG)

# Initialize services with repositories
user_service = UserService(user_repository)
product_service = ProductService(product_repository)

# Example usage
if __name__ == "__main__":
    # Get user by ID
    user_id = 1
    user = user_service.get_user_by_id(user_id)
    print(f"User: {user}")

    # Get product by ID
    product_id = 1
    product = product_service.get_product_by_id(product_id)
    print(f"Product: {product}")
