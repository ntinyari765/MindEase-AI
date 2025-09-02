# MindEase AI - Mental Wellness Platform

**🧠 AI-Powered Mental Health Companion | Built with Flask & MySQL**

## Project Links

- [Live Demo](https://web-production-d5f0.up.railway.app/)
- [Source Code](https://github.com/ntinyari765/MindEase-AI)

> **Detect stress early. Prevent burnout. Transform your wellness journey with AI.**

MindEase AI is a comprehensive mental wellness platform that uses artificial intelligence to analyze daily check-ins, detect stress patterns, and provide personalized recommendations for better mental health.

---

## 📸 Screenshots & Demo

### 🏠 Landing Page
![Landing Page](/images/Screenshot%202025-09-01%20235430.png)

### 🤖 AI Chatbot Dashboard
![Dashboard](/images/Screenshot%202025-09-01%20235112.png)

### 📊 Wellness Analytics
![Analytics](/images/Screenshot%202025-09-02%20004133.png)

---

## 🎯 Project Vision & Original Requirements

This project was built based on specific requirements to create a comprehensive mental wellness platform:

### 📝 **Original Prompt & Requirements**

  # Claude AI Prompt: Build Landing Page for AI Stress & Burnout Detector

Build a clean, modern, and responsive landing page for a web application called **AI Stress & Burnout Detector**. Follow these requirements:

## Design & Style
- Use a calming color scheme (soft blues, greens, neutrals).  
- Modern, minimal, with rounded corners, soft shadows, and smooth hover effects.  
- Fully responsive for desktop and mobile.  
- Use plain HTML, CSS, and JavaScript (no frameworks).

## Content Sections

### 1. Header
- Logo text: "MindEase AI"  
- Tagline: "Detect Stress Early. Prevent Burnout."

### 2. Hero Section
- Headline: "Your AI companion for daily stress check-ins."  
- Subtext: "Track your well-being, get personalized tips, and prevent burnout before it starts."  
- Call-to-action button: "Start Your Daily Check-in"

### 3. How It Works (3 steps)
- Step 1: Daily Check-in Chatbot  
- Step 2: AI Stress Analysis  
- Step 3: Personalized Self-Care Tips  
- Include icons or simple illustrations for each step.

### 4. Benefits Section (3 cards)
- Students: Stay balanced during exams.  
- Workers: Reduce burnout and improve focus.  
- Employers/Schools: Monitor wellness and support your team.

### 5. Demo Section
- Button: "Try the Chatbot"

### 6. Pricing/Subscription Section (single card layout)
- Free tier: Basic daily check-in  
- Premium tier: Dashboard & Insights for Employers/Schools  
- Include an "Upgrade with IntaSend" button as a placeholder

### 7. Footer
- Links: About, Contact, Privacy Policy

## Goal
Generate a polished, production-ready HTML, CSS, and JavaScript code snippet that implements all these sections and styling, ready to copy into a project.

> **"Build me a backend in Python using Flask with the following requirements:"**

**1. Database Setup (MySQL)**
- Create a `users` table with fields: `id (int, PK, auto_increment)`, `username (varchar)`, `password (hashed)`, and `created_at`
- Create a `checkins` table with fields: `id (int, PK, auto_increment)`, `user_id (FK)`, `message (text)`, `sentiment (varchar)`, `recommendation (text)`, `created_at`

**2. User Authentication**
- Implement **sign-up** endpoint (`/signup`) to register users and hash their passwords
- Implement **login** endpoint (`/login`) that validates credentials and returns a session token

**3. Chatbot / Check-in Flow**
- A `/checkin` endpoint that takes user text input and runs it through **AI sentiment analysis + recommendation tool**
- Store each check-in with sentiment and recommendation in the database
- Return JSON response with status, sentiment, and personalized recommendation

**4. Frontend Integration**
- Landing page with "Get Started" button redirecting to signup
- After signup, redirect to dashboard with chatbot access
- Add CORS for frontend-backend communication
- Adjust frontend code as needed for seamless flow

**5. Required Endpoints**
- `POST /signup` → register user
- `POST /login` → login user  
- `POST /checkin` → submit daily check-in, return sentiment + recommendation

**Additional Requirements:**
- Use environment variables for DB credentials
- Include example SQL schema
- Use `requests` for Hugging Face API or local sentiment model
- Hash passwords using `werkzeug.security` or bcrypt
- Return JSON responses

---

## ✨ Features Implemented

### 🔐 **Authentication System**
- [x] Secure user registration with password hashing
- [x] Session-based authentication with secure cookies
- [x] Protected routes with automatic redirection
- [x] User profile management

### 🤖 **AI-Powered Analysis**
- [x] **TextBlob Sentiment Analysis** - Polarity and subjectivity detection
- [x] **Keyword-Based Emotion Detection** - Stress, energy, mood indicators
- [x] **Numeric Scale Interpretation** - Context-aware 1-10 scale analysis
- [x] **Personalized Recommendations** - Based on detected emotional state

### 💾 **Database Architecture**
- [x] **Users Table** - Secure user management with hashed passwords
- [x] **Check-ins Table** - Complete conversation history with sentiment scores
- [x] **Sessions Table** - Persistent session management
- [x] **Wellness Activities Table** - Pre-loaded self-care activities

### 🎨 **Frontend Experience**
- [x] **Responsive Landing Page** - Modern gradient design with animations
- [x] **Authentication Pages** - Signup and login with real-time validation
- [x] **Interactive Dashboard** - Real-time chatbot with wellness statistics
- [x] **Progress Tracking** - Visual wellness scores and check-in history

### 📊 **Analytics & Insights**
- [x] **Wellness Score Calculation** - Algorithm based on sentiment history
- [x] **Check-in History** - Complete conversation archive
- [x] **Weekly/Monthly Statistics** - Progress tracking over time
- [x] **Sentiment Distribution** - Visual breakdown of emotional patterns

---

## 🏗️ Architecture & Tech Stack

### **Backend Stack**
```
🐍 Python 3.8+           # Core language
🌶️ Flask 2.3.3           # Web framework
🗄️ MySQL 8.0+            # Database
🧠 TextBlob 0.17.1       # Sentiment analysis
🔐 Werkzeug Security     # Password hashing
🌐 Flask-CORS 4.0.0      # Cross-origin requests
```

### **Frontend Stack**
```
🎨 HTML5/CSS3            # Responsive design
⚡ Vanilla JavaScript    # Interactive features
🎭 Font Awesome 6.0.0    # Icons
🌈 CSS Gradients         # Modern styling
📱 Mobile-First Design   # Responsive layout
```

## 📁 Project Structure

```
mindease-ai/
├── 📄 app.py                    # Main Flask application
├── 🗄️ db.py                     # Database connection & setup
├── 🧠 sentiment_analysis.py     # AI sentiment analysis module
├── 📋 requirements.txt          # Python dependencies
├── 🔐 .env.example             # Environment variables template
├── 📊 schema.sql               # Database schema
├── 📚 README.md                # This file
├── 📁 templates/               # HTML templates
│   ├── 🏠 index.html          # Landing page
│   ├── 📝 signup.html         # User registration
│   ├── 🔑 login.html          # User login
│   └── 📊 dashboard.html      # Main dashboard
├── 📁 static/                 # Static files
│   └── 🎨 styles.css          # CSS styling
```

---

## 🔌 API Documentation

### **Authentication Endpoints**

#### Register User
```http
POST /api/signup
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Account created successfully",
  "user": {
    "id": 1,
    "username": "johndoe"
  }
}
```

#### Login User
```http
POST /api/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "johndoe"
  }
}
```

### **Wellness Endpoints**

#### Submit Check-in
```http
POST /api/checkin
Content-Type: application/json
Cookie: session_token=abc123

{
  "message": "I'm feeling really stressed today, maybe an 8 out of 10",
  "question_index": 2,
  "question": "How would you rate your current stress level?"
}
```

**Response:**
```json
{
  "status": "success",
  "checkin_id": 15,
  "sentiment": "STRESSED",
  "sentiment_score": -0.65,
  "recommendation": "Your stress level seems high. Let's work on bringing it down with some quick relaxation techniques.",
  "wellness_tip": "🧘 Just 2 minutes of deep breathing can activate your relaxation response.",
  "suggested_activity": {
    "title": "4-7-8 Breathing Exercise",
    "description": "A calming breathing technique to reduce stress instantly.",
    "duration_minutes": 3,
    "instructions": ["Sit comfortably...", "Inhale for 4 counts..."]
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### Get Wellness Statistics
```http
GET /api/wellness-stats
Cookie: session_token=abc123
```

**Response:**
```json
{
  "status": "success",
  "stats": {
    "wellness_score": 72,
    "total_checkins": 25,
    "weekly_checkins": 5,
    "sentiment_distribution": {
      "positive": 12,
      "neutral": 8,
      "negative": 5
    }
  }
}
```

---

## 🧠 AI Sentiment Analysis Details

### **Analysis Components**

**1. TextBlob Sentiment Analysis**
- **Polarity**: -1.0 (very negative) to +1.0 (very positive)
- **Subjectivity**: 0.0 (objective) to 1.0 (subjective)

**2. Keyword-Based Emotion Detection**
```python
EMOTION_KEYWORDS = {
    'stress': ['stress', 'pressure', 'overwhelm', 'anxiety', 'tense'],
    'tired': ['tired', 'exhausted', 'fatigue', 'drained', 'low energy'],
    'happy': ['happy', 'joy', 'excited', 'amazing', 'wonderful'],
    'sad': ['sad', 'depressed', 'down', 'disappointed', 'lonely'],
    # ... more categories
}
```

**3. Numeric Scale Analysis**
- Automatically detects 1-10 scale responses
- Context-aware interpretation based on question type
- Different thresholds for energy vs. stress vs. sleep quality

**4. Recommendation Engine**
```python
# Example recommendation logic
if stress_level >= 8:
    recommendation = "High stress detected - breathing exercises recommended"
    activity_category = "breathing"
elif energy_level <= 3:
    recommendation = "Low energy - gentle movement suggested"
    activity_category = "energy"
```

---

## 🌐 Live Demo & Deployment

### **🚀 Live Deployment**
**[View Live Application →](web-production-d5f0.up.railway.app)**

---

## 📈 Roadmap & Future Features

### **🎯 Phase 1 (Current)**
- [x] Core authentication system
- [x] Basic AI sentiment analysis
- [x] Daily check-in functionality
- [x] Simple wellness recommendations

### **🚀 Phase 2 (Planned)**
- [ ] **Advanced AI Models** - GPT integration for better recommendations
- [ ] **Data Visualization** - Charts and graphs for progress tracking
- [ ] **Mobile App** - React Native mobile application
- [ ] **Team Features** - Employer dashboard for team wellness

### **🌟 Phase 3 (Future)**
- [ ] **Wearable Integration** - Apple Health, Fitbit data sync
- [ ] **Mood Prediction** - Predictive analytics for stress patterns
- [ ] **Telemedicine Integration** - Connect with mental health professionals
- [ ] **AI Therapist** - Advanced conversational therapy bot

---

### **Privacy & Data Protection**
- All user data encrypted at rest
- GDPR compliance implemented
- No personal data shared with third parties
- Users can request data deletion

### **Disclaimer**
This application is for informational purposes only and should not replace professional mental health treatment. If you're experiencing severe mental health issues, please consult a qualified healthcare provider.

---

## 👥 Team & Acknowledgments

### **Core Team**
- **Lead Developer**: Your Name ([@ntinyari765](https://github.com/ntinyari765))
- **AI/ML Consultant**: Claude AI (Anthropic)
- **UI/UX Design**: Community Contributors

### **Special Thanks**
- **TextBlob** - For sentiment analysis capabilities
- **Flask Community** - For excellent documentation
- **MySQL** - For reliable database solutions
- **Anthropic** - For AI development assistance

### **Open Source Libraries Used**
- Flask 2.3.3 - Web framework
- TextBlob 0.17.1 - Natural language processing
- MySQL Connector - Database connectivity
- Werkzeug - Security utilities
- Font Awesome - Icon library

---


<div align="center">

**🌟 If this project helped you, please consider giving it a star! ⭐**

**Built with ❤️ for better mental wellness**

</div>
