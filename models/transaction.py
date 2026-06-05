from datetime import datetime, timedelta
from database.db import Database
from bson import ObjectId
from models.book import Book
from models.member import Member

class Transaction:
    _collection = None
    
    @classmethod
    def get_collection(cls):
        """Lazy loading of collection"""
        if cls._collection is None:
            if not Database.is_initialized():
                raise Exception("Database not initialized. Please initialize database first.")
            cls._collection = Database.get_collection('transactions')
        return cls._collection
    
    @classmethod
    def issue_book(cls, book_id, member_id, days_allowed=14):
        """Issue a book to a member"""
        book = Book.find_by_id(book_id)
        member = Member.find_by_id(member_id)
        
        if not book or not member:
            return False, "Book or member not found"
        
        if book['available_copies'] <= 0:
            return False, "No copies available"
        
        if member['books_borrowed'] >= member['max_books']:
            return False, f"Member has reached maximum limit of {member['max_books']} books"
        
        # Check for overdue books
        overdue = cls.check_member_overdue(member_id)
        if overdue:
            return False, "Member has overdue books"
        
        # Create transaction
        transaction = {
            'book_id': ObjectId(book_id),
            'member_id': ObjectId(member_id),
            'issue_date': datetime.utcnow(),
            'due_date': datetime.utcnow() + timedelta(days=days_allowed),
            'status': 'Issued',
            'fine': 0,
            'created_at': datetime.utcnow()
        }
        
        result = cls.get_collection().insert_one(transaction)
        
        if result.inserted_id:
            # Update book availability
            Book.update_availability(book_id, -1)
            # Update member books borrowed count
            Member.update_books_borrowed(member_id, 1)
            return True, "Book issued successfully"
        
        return False, "Failed to issue book"
    
    @classmethod
    def return_book(cls, transaction_id, fine_amount=0):
        """Return a book"""
        transaction = cls.get_collection().find_one({'_id': ObjectId(transaction_id)})
        
        if not transaction or transaction['status'] != 'Issued':
            return False, "Invalid transaction or book already returned"
        
        # Calculate fine if any
        return_date = datetime.utcnow()
        fine = 0
        if return_date > transaction['due_date']:
            days_overdue = (return_date - transaction['due_date']).days
            fine = days_overdue * 5  # $5 per day late
        
        fine += fine_amount
        
        # Update transaction
        update_data = {
            'return_date': return_date,
            'status': 'Returned',
            'fine_paid': fine_amount,
            'fine': fine,
            'updated_at': datetime.utcnow()
        }
        
        result = cls.get_collection().update_one(
            {'_id': ObjectId(transaction_id)},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            # Update book availability
            Book.update_availability(transaction['book_id'], 1)
            # Update member books borrowed count
            Member.update_books_borrowed(transaction['member_id'], -1)
            return True, f"Book returned successfully. Fine: ${fine}"
        
        return False, "Failed to return book"
    
    @classmethod
    def check_member_overdue(cls, member_id):
        """Check if member has any overdue books"""
        now = datetime.utcnow()
        overdue = cls.get_collection().find_one({
            'member_id': ObjectId(member_id),
            'status': 'Issued',
            'due_date': {'$lt': now}
        })
        return overdue is not None
    
    @classmethod
    def get_active_by_member(cls, member_id):
        """Get active transactions for a member"""
        transactions = list(cls.get_collection().find({
            'member_id': ObjectId(member_id),
            'status': 'Issued'
        }))
        return transactions
    
    @classmethod
    def get_all(cls, skip=0, limit=10, status=None, search=None):
        """Get all transactions with pagination and filters"""
        query = {}
        if status:
            query['status'] = status
        
        collection = cls.get_collection()
        total = collection.count_documents(query)
        transactions = list(collection.find(query)
                           .sort('issue_date', -1)
                           .skip(skip)
                           .limit(limit))
        
        # Populate book and member details
        for transaction in transactions:
            book = Book.find_by_id(transaction['book_id'])
            member = Member.find_by_id(transaction['member_id'])
            transaction['book_title'] = book['title'] if book else 'Unknown'
            transaction['member_name'] = member['name'] if member else 'Unknown'
            transaction['member_id_display'] = member['member_id'] if member else 'Unknown'
        
        return transactions, total
    
    @classmethod
    def get_statistics(cls):
        """Get transaction statistics"""
        collection = cls.get_collection()
        total_issued = collection.count_documents({'status': 'Issued'})
        total_returned = collection.count_documents({'status': 'Returned'})
        overdue = collection.count_documents({
            'status': 'Issued',
            'due_date': {'$lt': datetime.utcnow()}
        })
        
        # Total fines collected
        pipeline = [
            {'$match': {'status': 'Returned', 'fine_paid': {'$exists': True}}},
            {'$group': {'_id': None, 'total': {'$sum': '$fine_paid'}}}
        ]
        fines = list(collection.aggregate(pipeline))
        total_fines_amount = fines[0]['total'] if fines else 0
        
        return {
            'total_issued': total_issued,
            'total_returned': total_returned,
            'overdue_books': overdue,
            'total_fines': total_fines_amount
        }