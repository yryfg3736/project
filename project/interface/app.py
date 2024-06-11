from flask import Flask, render_template, request, redirect, url_for
from database.db_connection import get_collection
from datetime import datetime
import asyncio
from engine.scraping_engine import fetch_with_selenium

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    collection = get_collection('tweets')
    query = {}

    if request.method == 'POST':
        search_query = request.form.get('search')
        if search_query:
            query['user'] = {'$regex': search_query, '$options': 'i'}  # Case-insensitive search

    tweets = collection.find(query).sort('date', -1)  # Sort by date descending

    # Process tweets to handle datetime and media
    tweets = list(tweets)
    for tweet in tweets:
        tweet['date'] = datetime.strptime(tweet['date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%b %d, %Y %H:%M') if tweet['date'] != 'N/A' else 'N/A'
        tweet['media'] = tweet['media'] if 'media' in tweet else []

    return render_template('index.html', tweets=tweets)

@app.route('/add_user', methods=['POST'])
def add_user():
    new_user = request.form.get('new_user')
    if new_user:
        user_list = [user.strip() for user in new_user.split(',')]
        urls = [f"https://x.com/{user}" for user in user_list]

        # Use asyncio to fetch tweets asynchronously
        try:
            asyncio.run(fetch_with_selenium(urls))
        except Exception as e:
            print(f"Error adding new user tweets: {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
