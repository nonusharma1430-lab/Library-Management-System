from datetime import datetime
from database.db import Database
from bson import ObjectId

class Book:
    _collection = None
    
    @classmethod
    def get_collection(cls):
        """Lazy loading of collection"""
        if cls._collection is None:
            if not Database.is_initialized():
                raise Exception("Database not initialized. Please initialize database first.")
            cls._collection = Database.get_collection('books')
        return cls._collection
    
    @classmethod
    def create(cls, book_data):
        """Create a new book"""
        book_data['created_at'] = datetime.utcnow()
        book_data['updated_at'] = datetime.utcnow()
        book_data['available_copies'] = book_data.get('total_copies', 1)
        result = cls.get_collection().insert_one(book_data)
        return result.inserted_id
    
    @classmethod
    def find_by_id(cls, book_id):
        """Find book by ID"""
        try:
            return cls.get_collection().find_one({'_id': ObjectId(book_id)})
        except:
            return None
    
    @classmethod
    def find_by_isbn(cls, isbn):
        """Find book by ISBN"""
        return cls.get_collection().find_one({'isbn': isbn})
    
    @classmethod
    def get_all(cls, skip=0, limit=10, search=None):
        """Get all books with pagination and search"""
        query = {}
        if search:
            query = {
                '$or': [
                    {'title': {'$regex': search, '$options': 'i'}},
                    {'author': {'$regex': search, '$options': 'i'}},
                    {'isbn': {'$regex': search, '$options': 'i'}}
                ]
            }
        
        collection = cls.get_collection()
        total = collection.count_documents(query)
        books = list(collection.find(query)
                     .sort('created_at', -1)
                     .skip(skip)
                     .limit(limit))
        
        return books, total
    
    @classmethod
    def update(cls, book_id, update_data):
        """Update book information"""
        update_data['updated_at'] = datetime.utcnow()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(book_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, book_id):
        """Delete a book"""
        result = cls.get_collection().delete_one({'_id': ObjectId(book_id)})
        return result.deleted_count > 0
    
    @classmethod
    def update_availability(cls, book_id, change):
        """Update available copies (change can be +1 or -1)"""
        result = cls.get_collection().update_one(
            {'_id': ObjectId(book_id)},
            {'$inc': {'available_copies': change}}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_statistics(cls):
        """Get book statistics"""
        collection = cls.get_collection()
        total_books = collection.count_documents({})
        available_books = collection.count_documents({'available_copies': {'$gt': 0}})
        
        pipeline = [
            {'$group': {
                '_id': None,
                'total': {'$sum': {'$subtract': ['$total_copies', '$available_copies']}}
            }}
        ]
        borrowed_books = list(collection.aggregate(pipeline))
        borrowed_total = borrowed_books[0]['total'] if borrowed_books else 0
        
        return {
            'total_books': total_books,
            'available_books': available_books,
            'borrowed_books': borrowed_total
        }