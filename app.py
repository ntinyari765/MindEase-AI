from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
from datetime import datetime
import os
from db import get_db_connection, init_db
from sentiment_analysis import analyze_sentiment_and_recommend

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# Enable CORS for all routes
CORS(app, supports_credentials=True)

# In-memory session storage (in production, use Redis or database)
user_sessions = {}

# Initialize database on startup
with app.app_context():
    init_db()

@app.route('/')
def home():
    """Serve the landing page"""
    return render_template('index.html')

@app.route('/signup') 
def signup_page(): 
    """Serve the signup page""" 
    return render_template('signup.html')

@app.route('/login-page')
def login_page():
    """Serve the login page"""
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    # Check if user is logged in
    token = request.cookies.get('session_token')
    if not token or token not in user_sessions:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        email = data.get('email', '').strip()
        
        if len(username) < 3:
            return jsonify({
                'status': 'error',
                'message': 'Username must be at least 3 characters long'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Username already exists'
            }), 409
        
        # Hash password and create user
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Create session
        session_token = str(uuid.uuid4())
        user_sessions[session_token] = {
            'user_id': user_id,
            'username': username,
            'created_at': datetime.now().isoformat()
        }
        
        response = jsonify({
            'status': 'success',
            'message': 'Account created successfully',
            'user': {
                'id': user_id,
                'username': username
            }
        })
        
        # Set session cookie
        response.set_cookie('session_token', session_token, httponly=True, max_age=86400)  # 24 hours
        
        return response
        
    except Exception as e:
        app.logger.error(f"Signup error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({
                'status': 'error',
                'message': 'Username and password are required'
            }), 400
        
        username = data['username'].strip()
        password = data['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user from database
        cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
        
        # Create session
        session_token = str(uuid.uuid4())
        user_sessions[session_token] = {
            'user_id': user['id'],
            'username': user['username'],
            'created_at': datetime.now().isoformat()
        }
        
        response = jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        })
        
        # Set session cookie
        response.set_cookie('session_token', session_token, httponly=True, max_age=86400)  # 24 hours
        
        return response
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    token = request.cookies.get('session_token')
    if token and token in user_sessions:
        del user_sessions[token]
    
    response = jsonify({
        'status': 'success',
        'message': 'Logged out successfully'
    })
    response.set_cookie('session_token', '', expires=0)
    
    return response

@app.route('/api/checkin', methods=['POST'])
def checkin():
    """Process daily check-in with sentiment analysis"""
    try:
        # Check authentication
        token = request.cookies.get('session_token')
        if not token or token not in user_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        user_info = user_sessions[token]
        user_id = user_info['user_id']
        
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({
                'status': 'error',
                'message': 'Message is required'
            }), 400
        
        message = data['message'].strip()
        question_index = data.get('question_index', 0)
        question = data.get('question', '')
        all_answers = data.get('all_answers', None)
        
        # Analyze sentiment and get recommendation
        analysis_result = analyze_sentiment_and_recommend(message, question_index, all_answers)
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO checkins (user_id, message, sentiment, recommendation, 
               question_index, question, created_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (user_id, message, analysis_result['sentiment'], 
             analysis_result['recommendation'], question_index, question, datetime.now())
        )
        conn.commit()
        checkin_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'checkin_id': checkin_id,
            'sentiment': analysis_result['sentiment'],
            'sentiment_score': analysis_result['sentiment_score'],
            'recommendation': analysis_result['recommendation'],
            'wellness_tip': analysis_result.get('wellness_tip', ''),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Check-in error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/checkin-history', methods=['GET'])
def get_checkin_history():
    """Get user's check-in history"""
    try:
        # Check authentication
        token = request.cookies.get('session_token')
        if not token or token not in user_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        user_info = user_sessions[token]
        user_id = user_info['user_id']
        
        # Get limit from query params
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT id, message, sentiment, recommendation, question_index, 
               question, created_at FROM checkins 
               WHERE user_id = %s ORDER BY created_at DESC LIMIT %s""",
            (user_id, limit)
        )
        
        checkins = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format response
        history = []
        for checkin in checkins:
            history.append({
                'id': checkin['id'],
                'message': checkin['message'],
                'sentiment': checkin['sentiment'],
                'recommendation': checkin['recommendation'],
                'question_index': checkin['question_index'],
                'question': checkin['question'],
                'created_at': checkin['created_at'].isoformat() if checkin['created_at'] else None
            })
        
        return jsonify({
            'status': 'success',
            'checkins': history,
            'total_count': len(history)
        })
        
    except Exception as e:
        app.logger.error(f"History error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/wellness-stats', methods=['GET'])
def get_wellness_stats():
    """Get user's wellness statistics"""
    try:
        # Check authentication
        token = request.cookies.get('session_token')
        if not token or token not in user_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        user_info = user_sessions[token]
        user_id = user_info['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get sentiment distribution
        cursor.execute(
            """SELECT sentiment, COUNT(*) as count FROM checkins 
               WHERE user_id = %s GROUP BY sentiment""",
            (user_id,)
        )
        sentiment_stats = cursor.fetchall()
        
        # Get recent check-ins count
        cursor.execute(
            """SELECT COUNT(*) as total FROM checkins 
               WHERE user_id = %s AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)""",
            (user_id,)
        )
        weekly_checkins = cursor.fetchone()['total']
        
        # Get total check-ins
        cursor.execute(
            "SELECT COUNT(*) as total FROM checkins WHERE user_id = %s",
            (user_id,)
        )
        total_checkins = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # Calculate wellness score (simple algorithm)
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        
        for stat in sentiment_stats:
            if stat['sentiment'] in ['POSITIVE', 'HAPPY', 'EXCITED']:
                positive_count += stat['count']
            elif stat['sentiment'] in ['NEGATIVE', 'SAD', 'STRESSED', 'ANXIOUS']:
                negative_count += stat['count']
            else:
                neutral_count += stat['count']
        
        total_sentiment_checkins = positive_count + neutral_count + negative_count
        wellness_score = 50  # Default neutral score
        
        if total_sentiment_checkins > 0:
            wellness_score = int(((positive_count * 2 + neutral_count) / (total_sentiment_checkins * 2)) * 100)
        
        return jsonify({
            'status': 'success',
            'stats': {
                'wellness_score': wellness_score,
                'total_checkins': total_checkins,
                'weekly_checkins': weekly_checkins,
                'sentiment_distribution': {
                    'positive': positive_count,
                    'neutral': neutral_count,
                    'negative': negative_count
                }
            }
        })
        
    except Exception as e:
        app.logger.error(f"Stats error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    try:
        # Check authentication
        token = request.cookies.get('session_token')
        if not token or token not in user_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        user_info = user_sessions[token]
        user_id = user_info['user_id']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'member_since': user['created_at'].isoformat() if user['created_at'] else None
            }
        })
        
    except Exception as e:
        app.logger.error(f"Profile error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/daily-tip', methods=['GET'])
def get_daily_tip():
    """Get a daily wellness tip"""
    try:
        # Daily wellness tips
        daily_tips = [
            "💧 Stay hydrated - even mild dehydration affects mood and energy.",
            "🌱 Take micro-breaks every hour, even just 30 seconds of stretching helps.",
            "🌞 Natural light exposure helps regulate your circadian rhythm.",
            "🫂 Social connection is as important for health as diet and exercise.",
            "🎯 Focus on progress, not perfection. Small steps lead to big changes.",
            "🧘 Just 2 minutes of deep breathing can activate your relaxation response.",
            "📱 Consider a 'phone-free' meal today to practice mindful eating.",
            "🚶 A 5-minute walk can boost creativity and reduce stress hormones.",
            "😴 Quality sleep is the foundation of good mental health.",
            "🍎 Eating regular, balanced meals helps stabilize your mood and energy.",
            "🎵 Music can be a powerful tool for mood regulation and stress relief.",
            "📝 Journaling for just 5 minutes can help process emotions and reduce anxiety.",
            "🌿 Spending time in nature, even just looking at plants, can reduce stress.",
            "🤝 Reach out to a friend or family member today - connection matters.",
            "🎨 Creative activities like drawing or coloring can be surprisingly therapeutic.",
            "⏰ Set boundaries with your time - it's okay to say no to protect your energy.",
            "🔄 Practice gratitude by writing down 3 things you're thankful for today.",
            "🧠 Challenge negative thoughts by asking 'Is this thought helpful or true?'",
            "🏃‍♀️ Even 10 minutes of physical activity can boost your mood and energy.",
            "🌅 Start your day with intention - set one small goal for today.",
            "💤 Create a relaxing bedtime routine to improve sleep quality.",
            "🍃 Practice mindful breathing: 4 counts in, hold 4, 4 counts out.",
            "📚 Reading for pleasure can be a great way to unwind and escape stress.",
            "🎪 Laughter truly is medicine - watch something funny or call a funny friend.",
            "🌙 Limit screen time 1 hour before bed for better sleep quality.",
            "💝 Do something kind for yourself today - you deserve care and compassion.",
            "🎯 Break large tasks into smaller, manageable steps to reduce overwhelm.",
            "🌱 Try a new healthy recipe - cooking can be a mindful, creative activity.",
            "🧘‍♀️ Practice body scanning: notice tension and consciously relax each muscle group.",
            "📞 Call someone you haven't talked to in a while - connection is healing."
        ]
        
        # Get today's date to determine which tip to show
        today = datetime.now()
        day_of_year = today.timetuple().tm_yday
        
        # Use day of year to select a consistent tip for the day
        tip_index = day_of_year % len(daily_tips)
        daily_tip = daily_tips[tip_index]
        
        return jsonify({
            'status': 'success',
            'tip': daily_tip,
            'date': today.strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        app.logger.error(f"Daily tip error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load daily tip'
        }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)