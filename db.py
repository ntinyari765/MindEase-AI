from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 3306),
    'database': os.getenv('DB_NAME', 'mindease_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        connection.cursor().execute("SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise

def init_db():
    """Initialize database and create tables if they don't exist"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create users table
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) DEFAULT '',
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Create checkins table
        create_checkins_table = """
        CREATE TABLE IF NOT EXISTS checkins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            message TEXT NOT NULL,
            sentiment VARCHAR(20) DEFAULT 'NEUTRAL',
            sentiment_score DECIMAL(3,2) DEFAULT 0.0,
            recommendation TEXT,
            question_index INT DEFAULT 0,
            question TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at),
            INDEX idx_sentiment (sentiment)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Create sessions table (optional, for persistent sessions)
        create_sessions_table = """
        CREATE TABLE IF NOT EXISTS sessions (
            id VARCHAR(36) PRIMARY KEY,
            user_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_expires_at (expires_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Create wellness_activities table for recommendations
        create_activities_table = """
        CREATE TABLE IF NOT EXISTS wellness_activities (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            category VARCHAR(50),
            duration_minutes INT DEFAULT 5,
            instructions JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        # Execute table creation
        cursor.execute(create_users_table)
        print("✓ Users table created/verified")
        
        cursor.execute(create_checkins_table)
        print("✓ Checkins table created/verified")
        
        cursor.execute(create_sessions_table)
        print("✓ Sessions table created/verified")
        
        cursor.execute(create_activities_table)
        print("✓ Wellness activities table created/verified")
        
        # Insert default wellness activities
        insert_default_activities(cursor)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✓ Database initialization completed successfully")
        
    except Error as e:
        print(f"Error initializing database: {e}")
        raise

def insert_default_activities(cursor):
    """Insert default wellness activities"""
    try:
        # Check if activities already exist
        cursor.execute("SELECT COUNT(*) as count FROM wellness_activities")
        result = cursor.fetchone()
        
        if result[0] > 0:
            return  # Activities already exist
        
        default_activities = [
            {
                'title': '4-7-8 Breathing Exercise',
                'description': 'A calming breathing technique to reduce stress and anxiety instantly.',
                'category': 'breathing',
                'duration_minutes': 3,
                'instructions': [
                    'Sit comfortably with your back straight',
                    'Exhale completely through your mouth',
                    'Close your mouth and inhale through your nose for 4 counts',
                    'Hold your breath for 7 counts',
                    'Exhale through your mouth for 8 counts',
                    'Repeat this cycle 3-4 times'
                ]
            },
            {
                'title': 'Quick Desk Stretches',
                'description': 'Simple movements to release tension and improve circulation at your workspace.',
                'category': 'movement',
                'duration_minutes': 5,
                'instructions': [
                    'Roll your shoulders backward 10 times',
                    'Gentle neck side bends (hold for 10 seconds each side)',
                    'Seated spinal twist (hold for 15 seconds each direction)',
                    'Wrist and ankle circles (10 times each direction)',
                    'Stand up and do 10 gentle toe touches'
                ]
            },
            {
                'title': 'Gratitude Moment',
                'description': 'A mindfulness exercise to shift focus to positive aspects of your day.',
                'category': 'mindfulness',
                'duration_minutes': 2,
                'instructions': [
                    'Think of one person you\'re grateful for today',
                    'Recall a recent positive experience, however small',
                    'Notice something beautiful in your current environment',
                    'Feel the warmth of gratitude in your heart',
                    'Take three deep, appreciative breaths'
                ]
            },
            {
                'title': '5-Minute Energy Boost',
                'description': 'Quick exercises to increase energy and alertness when feeling tired.',
                'category': 'energy',
                'duration_minutes': 5,
                'instructions': [
                    'Do 20 jumping jacks or march in place',
                    'Take 10 deep breaths with arms raised overhead',
                    'Do gentle neck and shoulder rolls',
                    'Drink a glass of water mindfully',
                    'Look out the window or at something distant for 1 minute'
                ]
            },
            {
                'title': 'Progressive Muscle Relaxation',
                'description': 'Systematic relaxation technique to release physical tension.',
                'category': 'relaxation',
                'duration_minutes': 10,
                'instructions': [
                    'Sit or lie down comfortably',
                    'Tense and release your toes for 5 seconds',
                    'Move up to calves, thighs, abdomen',
                    'Continue with hands, arms, shoulders',
                    'Finish with face and head muscles',
                    'Take 5 deep breaths feeling completely relaxed'
                ]
            },
            {
                'title': 'Mindful Walking',
                'description': 'A gentle way to combine movement with mindfulness.',
                'category': 'mindfulness',
                'duration_minutes': 10,
                'instructions': [
                    'Find a quiet space to walk slowly',
                    'Focus on the sensation of your feet touching the ground',
                    'Notice your breathing as you walk',
                    'Observe your surroundings without judgment',
                    'If your mind wanders, gently return focus to walking'
                ]
            }
        ]
        
        for activity in default_activities:
            cursor.execute(
                """INSERT INTO wellness_activities 
                   (title, description, category, duration_minutes, instructions) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (activity['title'], activity['description'], activity['category'], 
                 activity['duration_minutes'], json.dumps(activity['instructions']))
            )
        
        print(f"✓ Inserted {len(default_activities)} default wellness activities")
        
    except Error as e:
        print(f"Error inserting default activities: {e}")

def test_connection():
    """Test database connection"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        connection.close()
        
        print(f"✓ Successfully connected to MySQL version: {version[0]}")
        return True
        
    except Error as e:
        print(f"✗ Failed to connect to MySQL: {e}")
        return False

def get_wellness_activity_by_category(category='breathing'):
    """Get a random wellness activity by category"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM wellness_activities WHERE category = %s ORDER BY RAND() LIMIT 1",
            (category,)
        )
        activity = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return activity
        
    except Error as e:
        print(f"Error getting wellness activity: {e}")
        return None

if __name__ == '__main__':
    print("Testing database connection...")
    if test_connection():
        print("Initializing database...")
        init_db()
        print("Database setup completed!")
    else:
        print("Database connection failed!")