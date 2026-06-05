from datetime import datetime
from database.db import Database
from bson import ObjectId

class Member:
    _collection = None
    
    @classmethod
    def get_collection(cls):
        """Lazy loading of collection"""
        if cls._collection is None:
            if not Database.is_initialized():
                raise Exception("Database not initialized. Please initialize database first.")
            cls._collection = Database.get_collection('members')
        return cls._collection
    
    @classmethod
    def create(cls, member_data):
        """Create a new member"""
        member_data['registration_date'] = datetime.utcnow()
        member_data['books_borrowed'] = 0
        member_data['membership_status'] = "Active"
        
        # Generate member ID
        collection = cls.get_collection()
        last_member = collection.find_one(sort=[('member_id', -1)])
        if last_member and 'member_id' in last_member:
            last_id = int(last_member['member_id'][3:])
            new_id = f"LIB{last_id + 1:06d}"
        else:
            new_id = "LIB000001"
        
        member_data['member_id'] = new_id
        result = collection.insert_one(member_data)
        return result.inserted_id, new_id
    
    @classmethod
    def find_by_id(cls, member_id):
        """Find member by ID"""
        try:
            return cls.get_collection().find_one({'_id': ObjectId(member_id)})
        except:
            return None
    
    @classmethod
    def find_by_member_id(cls, member_id):
        """Find member by library member ID"""
        return cls.get_collection().find_one({'member_id': member_id})
    
    @classmethod
    def find_by_email(cls, email):
        """Find member by email"""
        return cls.get_collection().find_one({'email': email})
    
    @classmethod
    def get_all(cls, skip=0, limit=10, search=None):
        """Get all members with pagination and search"""
        query = {}
        if search:
            query = {
                '$or': [
                    {'name': {'$regex': search, '$options': 'i'}},
                    {'email': {'$regex': search, '$options': 'i'}},
                    {'member_id': {'$regex': search, '$options': 'i'}},
                    {'phone': {'$regex': search, '$options': 'i'}}
                ]
            }
        
        collection = cls.get_collection()
        total = collection.count_documents(query)
        members = list(collection.find(query)
                       .sort('registration_date', -1)
                       .skip(skip)
                       .limit(limit))
        
        return members, total
    
    @classmethod
    def update(cls, member_id, update_data):
        """Update member information"""
        update_data['updated_at'] = datetime.utcnow()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(member_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    @classmethod
    def delete(cls, member_id):
        """Delete a member"""
        # Check if member has borrowed books
        from models.transaction import Transaction
        active_transactions = Transaction.get_active_by_member(member_id)
        if active_transactions:
            return False, "Member has active borrowed books"
        
        result = cls.get_collection().delete_one({'_id': ObjectId(member_id)})
        return result.deleted_count > 0, "Member deleted successfully"
    
    @classmethod
    def update_books_borrowed(cls, member_id, change):
        """Update books borrowed count"""
        result = cls.get_collection().update_one(
            {'_id': ObjectId(member_id)},
            {'$inc': {'books_borrowed': change}}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_statistics(cls):
        """Get member statistics"""
        collection = cls.get_collection()
        total_members = collection.count_documents({})
        active_members = collection.count_documents({'membership_status': 'Active'})
        
        pipeline = [
            {'$group': {'_id': None, 'total': {'$sum': '$books_borrowed'}}}
        ]
        borrowed_books = list(collection.aggregate(pipeline))
        total_books_borrowed = borrowed_books[0]['total'] if borrowed_books else 0
        
        return {
            'total_members': total_members,
            'active_members': active_members,
            'total_books_borrowed': total_books_borrowed
        }