from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime, timezone
import os
import logging

from app.analyzer import analyze_prices, analyze_sentiment
from app.api import create_api_blueprint
from app.config import get_config

mongo = PyMongo()


def create_app(config_object=None):
    app = Flask(__name__)
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(get_config())

    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)

    mongo.init_app(app)
    api_bp = create_api_blueprint(mongo)
    app.register_blueprint(api_bp, url_prefix='/api')
    logging.basicConfig(level=logging.INFO)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))

            if mongo.db.users.find_one({"username": username}):
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))

            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = {
                "username": username,
                "email": email,
                "password": hashed_password
            }
            mongo.db.users.insert_one(new_user)

            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = mongo.db.users.find_one({"username": username})

            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/search', methods=['POST'])
    def search():
        if 'user_id' not in session:
            flash('You must be logged in to perform a search.', 'warning')
            return redirect(url_for('login'))

        user_id = session['user_id']
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)

        product_name = request.form['product']
        results = analyze_prices(product_name)
        search_data = {
            "user_id": user_id,
            "product_name": product_name,
            "results": results,
            "timestamp": datetime.now(timezone.utc)
        }
        mongo.db.search_history.insert_one(search_data)

        app.logger.info(f"Search performed for: {product_name}")
        return render_template('results.html', product=product_name, results=results)

    @app.route('/recent')
    def recent_searches():
        if 'user_id' not in session:
            flash('You must be logged in to view recent searches.', 'warning')
            return redirect(url_for('login'))

        user_id = ObjectId(session['user_id'])
        searches = mongo.db.search_history.find({"user_id": user_id}).sort("timestamp", -1)

        return render_template('recent.html', searches=searches)

    @app.route('/analyze_sentiment', methods=['POST'])
    def sentiment_analysis():
        data = request.json
        titles = data['titles']
        result = analyze_sentiment(titles)
        return jsonify(result)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)