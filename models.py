from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    @staticmethod
    def create_user(mongo, username, email, password):
        user = User(username=username, email=email, password=password)
        mongo.db.users.insert_one(user.__dict__)
        return user

    @staticmethod
    def find_by_username(mongo, username):
        return mongo.db.users.find_one({"username": username})

    @staticmethod
    def check_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)

class Product:
    def __init__(self, name, price, source):
        self.name = name
        self.price = price
        self.source = source

    @staticmethod
    def add_product(mongo, name, price, source):
        product = Product(name=name, price=price, source=source)
        mongo.db.products.insert_one(product.__dict__)
        return product

    @staticmethod
    def find_all(mongo):
        return list(mongo.db.products.find())