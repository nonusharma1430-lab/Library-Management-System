from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models.book import Book
from config import Config
from bson import ObjectId

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def list_books():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = Config.ITEMS_PER_PAGE
    skip = (page - 1) * per_page
    
    books, total = Book.get_all(skip, per_page, search)
    
    return render_template('books.html', 
                         books=books, 
                         total=total, 
                         page=page,
                         per_page=per_page,
                         search=search,
                         categories=Config.BOOK_CATEGORIES)

@books_bp.route('/add', methods=['POST'])
def add_book():
    try:
        book_data = {
            'title': request.form.get('title'),
            'author': request.form.get('author'),
            'isbn': request.form.get('isbn'),
            'publisher': request.form.get('publisher'),
            'year': int(request.form.get('year')),
            'category': request.form.get('category'),
            'total_copies': int(request.form.get('total_copies', 1)),
            'location': request.form.get('location'),
            'description': request.form.get('description', '')
        }
        
        # Check if ISBN already exists
        existing = Book.find_by_isbn(book_data['isbn'])
        if existing:
            return jsonify({'success': False, 'message': 'ISBN already exists'}), 400
        
        book_id = Book.create(book_data)
        return jsonify({'success': True, 'message': 'Book added successfully', 'book_id': str(book_id)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@books_bp.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if request.method == 'POST':
        try:
            update_data = {
                'title': request.form.get('title'),
                'author': request.form.get('author'),
                'publisher': request.form.get('publisher'),
                'year': int(request.form.get('year')),
                'category': request.form.get('category'),
                'location': request.form.get('location'),
                'description': request.form.get('description', '')
            }
            
            # If total copies changed, adjust available copies
            new_total = int(request.form.get('total_copies'))
            book = Book.find_by_id(book_id)
            if book:
                diff = new_total - book['total_copies']
                update_data['total_copies'] = new_total
                update_data['available_copies'] = book['available_copies'] + diff
            
            Book.update(book_id, update_data)
            return jsonify({'success': True, 'message': 'Book updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    book = Book.find_by_id(book_id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('books.list_books'))
    
    return render_template('edit_book.html', book=book, categories=Config.BOOK_CATEGORIES)

@books_bp.route('/delete/<book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        # Check if book has active transactions
        from models.transaction import Transaction
        active_transactions = Transaction.collection.find_one({
            'book_id': ObjectId(book_id),
            'status': 'Issued'
        })
        
        if active_transactions:
            return jsonify({'success': False, 'message': 'Cannot delete book with active transactions'}), 400
        
        Book.delete(book_id)
        return jsonify({'success': True, 'message': 'Book deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@books_bp.route('/get/<book_id>')
def get_book(book_id):
    book = Book.find_by_id(book_id)
    if book:
        book['_id'] = str(book['_id'])
        return jsonify({'success': True, 'book': book})
    return jsonify({'success': False, 'message': 'Book not found'}), 404