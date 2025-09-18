from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
import secrets
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
csrf = CSRFProtect(app)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROFILES_FOLDER'] = 'static/profiles'

# Create upload directories
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/profiles', exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_db_connection()

    # Users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        birthdate DATE NOT NULL,
        password TEXT NOT NULL,
        profile_picture TEXT DEFAULT 'default.jpg',
        role TEXT DEFAULT 'user',
        banned_until DATETIME DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Movies table - Enhanced with more fields
    conn.execute('''CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        genre TEXT NOT NULL,
        year INTEGER NOT NULL,
        poster TEXT NOT NULL,
        video_url TEXT NOT NULL,
        duration INTEGER DEFAULT 0,
        director TEXT DEFAULT '',
        cast TEXT DEFAULT '',
        imdb_rating REAL DEFAULT 0.0,
        tmdb_id INTEGER DEFAULT NULL,
        added_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (added_by) REFERENCES users (id)
    )''')

    # Comments table
    conn.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (movie_id) REFERENCES movies (id)
    )''')

    # Favorites table
    conn.execute('''CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        UNIQUE(user_id, movie_id)
    )''')

    # New Ratings table
    conn.execute('''CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        movie_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        review TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (movie_id) REFERENCES movies (id),
        UNIQUE(user_id, movie_id)
    )''')

    # Reports table
    conn.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    # Create default admin user only in development
    admin_exists = conn.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('admin@moviesite.ge',)).fetchone()[0]
    if not admin_exists and app.debug:
        admin_password = 'admin123'  # Simple password for development
        hashed_password = generate_password_hash(admin_password)
        conn.execute('''INSERT INTO users (name, surname, email, birthdate, password, role)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                      ('Admin', 'User', 'admin@moviesite.ge', '1990-01-01', hashed_password, 'admin'))
        print(f"Admin created - Email: admin@moviesite.ge, Password: {admin_password}")

    conn.commit()
    conn.close()

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    genre_filter = request.args.get('genre', '')
    year_filter = request.args.get('year', '')
    rating_filter = request.args.get('rating', '')

    conn = get_db_connection()

    # Base query
    query = '''SELECT m.*, u.name as added_by_name,
                      COALESCE(AVG(r.rating), 0) as avg_rating,
                      COUNT(r.rating) as rating_count
               FROM movies m
               JOIN users u ON m.added_by = u.id
               LEFT JOIN ratings r ON m.id = r.movie_id
               WHERE 1=1'''

    params = []

    # Add search filters
    if search_query:
        query += ' AND (m.title LIKE ? OR m.description LIKE ? OR m.director LIKE ? OR m.cast LIKE ?)'
        search_param = f'%{search_query}%'
        params.extend([search_param, search_param, search_param, search_param])

    if genre_filter:
        query += ' AND m.genre LIKE ?'
        params.append(f'%{genre_filter}%')

    if year_filter:
        query += ' AND m.year = ?'
        params.append(int(year_filter))

    query += ' GROUP BY m.id'

    if rating_filter:
        query += ' HAVING avg_rating >= ?'
        params.append(float(rating_filter))

    query += ' ORDER BY m.created_at DESC LIMIT 20'

    movies = conn.execute(query, params).fetchall()

    # Get available genres and years for filters
    genres = conn.execute('SELECT DISTINCT genre FROM movies ORDER BY genre').fetchall()
    years = conn.execute('SELECT DISTINCT year FROM movies ORDER BY year DESC').fetchall()

    conn.close()

    return render_template('index.html',
                         movies=movies,
                         search_query=search_query,
                         genre_filter=genre_filter,
                         year_filter=year_filter,
                         rating_filter=rating_filter,
                         genres=genres,
                         years=years)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        birthdate = request.form['birthdate']
        password = request.form['password']

        if not all([name, surname, email, birthdate, password]):
            flash('ყველა ველი აუცილებელია', 'error')
            return render_template('register.html')

        conn = get_db_connection()

        # Check if email exists
        user_exists = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if user_exists:
            flash('ეს ელ.ფოსტა უკვე რეგისტრირებულია', 'error')
            conn.close()
            return render_template('register.html')

        # Create user
        hashed_password = generate_password_hash(password)
        conn.execute('''INSERT INTO users (name, surname, email, birthdate, password)
                        VALUES (?, ?, ?, ?, ?)''',
                      (name, surname, email, birthdate, hashed_password))
        conn.commit()
        conn.close()

        flash('რეგისტრაცია წარმატებით დასრულდა!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Check if user is banned
            if user['banned_until']:
                try:
                    banned_until = datetime.fromisoformat(user['banned_until'])
                    if banned_until > datetime.now():
                        flash('თქვენი ანგარიში დროებით დაბლოკილია', 'error')
                        return render_template('login.html')
                except (ValueError, TypeError):
                    pass

            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            flash('წარმატებით შეხვედით!', 'success')
            return redirect(url_for('index'))
        else:
            flash('არასწორი ელ.ფოსტა ან პაროლი', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('წარმატებით გამოხვედით', 'success')
    return redirect(url_for('index'))

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_db_connection()
    movie = conn.execute('''SELECT m.*, u.name as added_by_name,
                                  COALESCE(AVG(r.rating), 0) as avg_rating,
                                  COUNT(r.rating) as rating_count
                           FROM movies m
                           JOIN users u ON m.added_by = u.id
                           LEFT JOIN ratings r ON m.id = r.movie_id
                           WHERE m.id = ?
                           GROUP BY m.id''', (movie_id,)).fetchone()

    if not movie:
        flash('ფილმი ვერ მოიძებნა', 'error')
        conn.close()
        return redirect(url_for('index'))

    # Get comments with user info
    comments = conn.execute('''SELECT c.comment, c.created_at, u.name, u.surname
                              FROM comments c JOIN users u ON c.user_id = u.id
                              WHERE c.movie_id = ? ORDER BY c.created_at DESC''',
                          (movie_id,)).fetchall()

    # Get ratings and reviews
    ratings = conn.execute('''SELECT r.rating, r.review, r.created_at, u.name, u.surname
                             FROM ratings r JOIN users u ON r.user_id = u.id
                             WHERE r.movie_id = ? AND r.review != ''
                             ORDER BY r.created_at DESC''',
                          (movie_id,)).fetchall()

    # Check if current user has favorited this movie
    is_favorite = False
    user_rating = None
    if 'user_id' in session:
        favorite = conn.execute('SELECT id FROM favorites WHERE user_id = ? AND movie_id = ?',
                               (session['user_id'], movie_id)).fetchone()
        is_favorite = favorite is not None

        # Get user's rating
        user_rating_row = conn.execute('SELECT rating, review FROM ratings WHERE user_id = ? AND movie_id = ?',
                                      (session['user_id'], movie_id)).fetchone()
        if user_rating_row:
            user_rating = dict(user_rating_row)

    conn.close()
    return render_template('movie_detail.html',
                         movie=movie,
                         comments=comments,
                         ratings=ratings,
                         is_favorite=is_favorite,
                         user_rating=user_rating)

@app.route('/movie/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id):
    if 'user_id' not in session:
        flash('ავტორიზაცია საჭიროა', 'error')
        return redirect(url_for('login'))
    
    # Check if user is admin or moderator
    if session.get('user_role') not in ['admin', 'moderator']:
        flash('ამ მოქმედების შესასრულებლად არ გაქვთ უფლება', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get movie info before deletion
    movie = conn.execute('SELECT title FROM movies WHERE id = ?', (movie_id,)).fetchone()
    if not movie:
        flash('ფილმი ვერ მოიძებნა', 'error')
        conn.close()
        return redirect(url_for('index'))
    
    try:
        # Delete related data first (foreign key constraints)
        conn.execute('DELETE FROM comments WHERE movie_id = ?', (movie_id,))
        conn.execute('DELETE FROM favorites WHERE movie_id = ?', (movie_id,))
        conn.execute('DELETE FROM ratings WHERE movie_id = ?', (movie_id,))
        
        # Delete the movie
        conn.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        
        conn.commit()
        flash(f'ფილმი "{movie["title"]}" წარმატებით წაშლილია', 'success')
        
    except Exception as e:
        conn.rollback()
        flash('ფილმის წაშლისას მოხდა შეცდომა', 'error')
        print(f"Error deleting movie: {e}")
    finally:
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/movie/<int:movie_id>/rate', methods=['POST'])
def rate_movie(movie_id):
    if 'user_id' not in session:
        flash('რეიტინგის დასატოვებლად გაიარეთ ავტორიზაცია', 'error')
        return redirect(url_for('login'))

    rating = request.form.get('rating')
    review = request.form.get('review', '')

    if not rating or int(rating) < 1 or int(rating) > 5:
        flash('რეიტინგი უნდა იყოს 1-დან 5-მდე', 'error')
        return redirect(url_for('movie_detail', movie_id=movie_id))

    conn = get_db_connection()

    # Insert or update rating
    conn.execute('''INSERT OR REPLACE INTO ratings (user_id, movie_id, rating, review)
                   VALUES (?, ?, ?, ?)''',
                 (session['user_id'], movie_id, int(rating), review))
    conn.commit()
    conn.close()

    flash('რეიტინგი წარმატებით დაემატა', 'success')
    return redirect(url_for('movie_detail', movie_id=movie_id))

@app.route('/movie/<int:movie_id>/favorite', methods=['POST'])
def toggle_favorite(movie_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Authorization required'})

    conn = get_db_connection()

    # Check if already favorited
    favorite = conn.execute('SELECT id FROM favorites WHERE user_id = ? AND movie_id = ?',
                           (session['user_id'], movie_id)).fetchone()

    if favorite:
        # Remove from favorites
        conn.execute('DELETE FROM favorites WHERE user_id = ? AND movie_id = ?',
                    (session['user_id'], movie_id))
        is_favorite = False
        message = 'ფავორიტებიდან წაშლილია'
    else:
        # Add to favorites
        conn.execute('INSERT INTO favorites (user_id, movie_id) VALUES (?, ?)',
                    (session['user_id'], movie_id))
        is_favorite = True
        message = 'ფავორიტებში დაემატა'

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'is_favorite': is_favorite, 'message': message})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)