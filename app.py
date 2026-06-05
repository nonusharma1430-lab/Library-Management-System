import sys
import os
from flask import Flask, render_template

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Import config first
from config import Config
app.config.from_object(Config)

# Initialize database BEFORE importing models and routes
from database.db import Database

print("Initializing database connection...")
if not Database.initialize():
    print("\n" + "="*60)
    print("ERROR: Could not connect to MongoDB!")
    print("="*60)
    print("\nPlease ensure MongoDB is installed and running.")
    print("\nTo start MongoDB on Windows:")
    print("1. Open Services (services.msc)")
    print("2. Find 'MongoDB' service")
    print("3. Right-click and select 'Start'")
    print("\nOr install MongoDB from: https://www.mongodb.com/try/download/community")
    print("\nFor cloud alternative, update MONGO_URI in .env file with MongoDB Atlas URI")
    print("="*60)
    sys.exit(1)

print("✓ Database connected successfully!")

# Now import models and routes (after database is initialized)
from routes.books import books_bp
from routes.members import members_bp
from routes.transactions import transactions_bp

# Register blueprints
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(members_bp, url_prefix='/members')
app.register_blueprint(transactions_bp, url_prefix='/transactions')

@app.route('/')
def index():
    from models.book import Book
    from models.member import Member
    from models.transaction import Transaction
    
    book_stats = Book.get_statistics()
    member_stats = Member.get_statistics()
    transaction_stats = Transaction.get_statistics()
    
    # Get recent books and members
    recent_books, _ = Book.get_all(0, 5)
    recent_members, _ = Member.get_all(0, 5)
    recent_transactions, _ = Transaction.get_all(0, 5)
    
    return render_template('index.html',
                         book_stats=book_stats,
                         member_stats=member_stats,
                         transaction_stats=transaction_stats,
                         recent_books=recent_books,
                         recent_members=recent_members,
                         recent_transactions=recent_transactions)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Library Management System")
    print("="*50)
    print(f"Server starting on http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)