import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.environ.get('DB_NAME', 'library_management')
    
    # Pagination settings
    ITEMS_PER_PAGE = 10
    
    # Book categories
    BOOK_CATEGORIES = [
        'Fiction', 'Non-Fiction', 'Science', 'Technology', 
        'History', 'Biography', 'Children', 'Academic', 
        'Reference', 'Magazine', 'Other'
    ]
    
    # Book status
    BOOK_STATUS = ['Available', 'Borrowed', 'Reserved', 'Lost', 'Damaged']