from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✓ MongoDB is running and accessible!")
    print("  You can now run the Library Management System")
    client.close()
except Exception as e:
    print(f"✗ Cannot connect to MongoDB: {e}")
    print("\nSolutions:")
    print("1. Install MongoDB from: https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB service: net start MongoDB")
    print("3. Or use MongoDB Atlas cloud database")