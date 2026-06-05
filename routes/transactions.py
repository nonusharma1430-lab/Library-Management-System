from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.transaction import Transaction
from models.book import Book
from models.member import Member
from config import Config
from bson import ObjectId
from datetime import datetime  # Add this import

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
def list_transactions():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    per_page = Config.ITEMS_PER_PAGE
    skip = (page - 1) * per_page
    
    transactions, total = Transaction.get_all(skip, per_page, status)
    
    # Add current datetime to template context
    now = datetime.utcnow()
    
    return render_template('transactions.html', 
                         transactions=transactions, 
                         total=total, 
                         page=page,
                         per_page=per_page,
                         status=status,
                         now=now)  # Pass now to template

@transactions_bp.route('/issue', methods=['POST'])
def issue_book():
    try:
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')
        days_allowed = int(request.form.get('days_allowed', 14))
        
        success, message = Transaction.issue_book(book_id, member_id, days_allowed)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@transactions_bp.route('/return', methods=['POST'])
def return_book():
    try:
        transaction_id = request.form.get('transaction_id')
        fine_amount = float(request.form.get('fine_amount', 0))
        
        success, message = Transaction.return_book(transaction_id, fine_amount)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@transactions_bp.route('/search-book', methods=['GET'])
def search_book():
    search = request.args.get('q', '')
    if not search:
        return jsonify([])
    
    books, _ = Book.get_all(0, 10, search)
    available_books = [b for b in books if b['available_copies'] > 0]
    
    for book in available_books:
        book['_id'] = str(book['_id'])
    
    return jsonify(available_books)

@transactions_bp.route('/search-member', methods=['GET'])
def search_member():
    search = request.args.get('q', '')
    if not search:
        return jsonify([])
    
    members, _ = Member.get_all(0, 10, search)
    
    for member in members:
        member['_id'] = str(member['_id'])
    
    return jsonify(members)

@transactions_bp.route('/member-transactions/<member_id>')
def member_transactions(member_id):
    active_transactions = Transaction.get_active_by_member(member_id)
    for transaction in active_transactions:
        book = Book.find_by_id(transaction['book_id'])
        transaction['book_title'] = book['title'] if book else 'Unknown'
        transaction['days_left'] = (transaction['due_date'] - datetime.utcnow()).days
        transaction['_id'] = str(transaction['_id'])
        transaction['book_id'] = str(transaction['book_id'])
    
    return jsonify({'success': True, 'transactions': active_transactions})

@transactions_bp.route('/reports')
def reports():
    book_stats = Book.get_statistics()
    member_stats = Member.get_statistics()
    transaction_stats = Transaction.get_statistics()
    
    # Get recent transactions
    recent_transactions, _ = Transaction.get_all(0, 10)
    
    return render_template('reports.html',
                         book_stats=book_stats,
                         member_stats=member_stats,
                         transaction_stats=transaction_stats,
                         recent_transactions=recent_transactions)