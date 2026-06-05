from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client = None
    db = None
    _initialized = False
    
    @classmethod
    def initialize(cls):
        """Initialize database connection"""
        try:
            cls.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            cls.client.server_info()
            cls.db = cls.client[Config.DB_NAME]
            cls._create_indexes()
            cls._initialized = True
            logger.info(f"Successfully connected to MongoDB database: {Config.DB_NAME}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            cls._initialized = False
            return False
    
    @classmethod
    def _create_indexes(cls):
        """Create indexes for better query performance"""
        if not cls._initialized:
            return
            
        # Books collection indexes
        cls.db.books.create_index([("isbn", 1)], unique=True)
        cls.db.books.create_index([("title", "text"), ("author", "text")])
        
        # Members collection indexes
        cls.db.members.create_index([("member_id", 1)], unique=True)
        cls.db.members.create_index([("email", 1)], unique=True)
        cls.db.members.create_index([("phone", 1)])
        
        # Transactions collection indexes
        cls.db.transactions.create_index([("book_id", 1), ("member_id", 1)])
        cls.db.transactions.create_index([("issue_date", -1)])
        cls.db.transactions.create_index([("status", 1)])
    
    @classmethod
    def get_collection(cls, name):
        """Get collection by name - only after initialization"""
        if not cls._initialized:
            raise Exception("Database not initialized. Call Database.initialize() first.")
        return cls.db[name]
    
    @classmethod
    def is_initialized(cls):
        """Check if database is initialized"""
        return cls._initialized
    
    @classmethod
    def close(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            cls._initialized = False
            logger.info("Database connection closed")