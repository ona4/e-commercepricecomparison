from flask import Blueprint, jsonify
from flask_pymongo import PyMongo

def create_api_blueprint(mongo):
    api_bp = Blueprint('api', __name__)

    @api_bp.route('/products')
    def get_products():
        products = list(mongo.db.products.find())
        for product in products:
            product['_id'] = str(product['_id'])
        return jsonify(products)

    return api_bp