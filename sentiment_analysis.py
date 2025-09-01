import re
import random
from textblob import TextBlob # type: ignore
from db import get_wellness_activity_by_category

# Keywords for different emotional states
EMOTION_KEYWORDS = {
    'stress': ['stress', 'stressed', 'pressure', 'overwhelm', 'burden', 'anxiety', 'anxious', 'worry', 'tense'],
    'tired': ['tired', 'exhausted', 'fatigue', 'sleepy', 'drained', 'worn out', 'low energy'],
    'sad': ['sad', 'depressed', 'down', 'upset', 'disappointed', 'lonely', 'empty', 'hopeless'],
    'angry': ['angry', 'frustrated', 'mad', 'irritated', 'annoyed', 'furious', 'rage'],
    'happy': ['happy', 'joy', 'excited', 'great', 'amazing', 'wonderful', 'fantastic', 'awesome', 'good'],
    'motivated': ['motivated', 'energetic', 'productive', 'focused', 'determined', 'inspired'],
    'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'content', 'balanced', 'centered']
}

# Sleep quality indicators
SLEEP_INDICATORS = {
    'good': ['well', 'great', 'amazing', 'perfect', 'sound', '8', '9', '10'],
    'poor': ['bad', 'terrible', 'awful', 'poorly', 'restless', '1', '2', '3', '4']
}

# Workload indicators
WORKLOAD_INDICATORS = {
    'overwhelmed': ['overwhelming', 'too much', 'crazy', 'insane', 'impossible', 'drowning'],
    'manageable': ['manageable', 'okay', 'fine', 'good', 'reasonable', 'just right'],
    'light': ['light', 'easy', 'not much', 'quiet', 'slow']
}

def analyze_sentiment_basic(text):
    """Basic sentiment analysis using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
    subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
    
    # Convert polarity to sentiment label
    if polarity >= 0.3:
        sentiment = 'POSITIVE'
    elif polarity <= -0.3:
        sentiment = 'NEGATIVE'
    else:
        sentiment = 'NEUTRAL'
    
    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'confidence': abs(polarity)
    }

def detect_emotions(text):
    """Detect specific emotions based on keywords"""
    text_lower = text.lower()
    detected_emotions = []
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_emotions.append(emotion)
                break
    
    return detected_emotions

def analyze_numeric_response(text, question_index):
    """Analyze numeric responses (1-10 scale questions)"""
    # Extract numbers from text
    numbers = re.findall(r'\b(\d{1,2})\b', text)
    
    if not numbers:
        return None
    
    try:
        score = int(numbers[0])
        if score < 1 or score > 10:
            return None
        
        # Different interpretations based on question type
        if question_index == 1:  # Energy level
            if score >= 8:
                return {'level': 'high', 'category': 'energy', 'score': score}
            elif score >= 5:
                return {'level': 'moderate', 'category': 'energy', 'score': score}
            else:
                return {'level': 'low', 'category': 'energy', 'score': score}
        
        elif question_index == 2:  # Stress level
            if score >= 8:
                return {'level': 'high', 'category': 'stress', 'score': score}
            elif score >= 5:
                return {'level': 'moderate', 'category': 'stress', 'score': score}
            else:
                return {'level': 'low', 'category': 'stress', 'score': score}
        
        elif question_index == 3:  # Sleep quality
            if score >= 8:
                return {'level': 'good', 'category': 'sleep', 'score': score}
            elif score >= 5:
                return {'level': 'moderate', 'category': 'sleep', 'score': score}
            else:
                return {'level': 'poor', 'category': 'sleep', 'score': score}
        
        # Default interpretation
        if score >= 7:
            return {'level': 'good', 'category': 'general', 'score': score}
        elif score >= 4:
            return {'level': 'moderate', 'category': 'general', 'score': score}
        else:
            return {'level': 'poor', 'category': 'general', 'score': score}
        
    except ValueError:
        return None

def generate_recommendation(sentiment_result, emotions, numeric_analysis, question_index):
    """Generate personalized recommendations based on analysis"""
    recommendations = []
    activity_category = 'breathing'  # default
    
    # Base recommendations on numeric scores if available
    if numeric_analysis:
        category = numeric_analysis['category']
        level = numeric_analysis['level']
        score = numeric_analysis['score']
        
        if category == 'stress' and level == 'high':
            recommendations.extend([
                "Your stress level seems high. Let's work on bringing it down with some quick relaxation techniques.",
                "Take a few minutes for deep breathing - it can significantly reduce stress hormones.",
                "Consider stepping away from your current task for a 5-minute break."
            ])
            activity_category = 'breathing'
        
        elif category == 'energy' and level == 'low':
            recommendations.extend([
                "Your energy seems low. Let's find ways to naturally boost it without caffeine.",
                "A quick movement break can help increase circulation and alertness.",
                "Make sure you're staying hydrated - dehydration is a common cause of fatigue."
            ])
            activity_category = 'energy'
        
        elif category == 'sleep' and level == 'poor':
            recommendations.extend([
                "Poor sleep affects everything. Let's focus on relaxation techniques for better rest tonight.",
                "Consider establishing a calming bedtime routine starting 30 minutes before sleep.",
                "Avoid screens for at least an hour before bed if possible."
            ])
            activity_category = 'relaxation'
    
    # Add emotion-based recommendations
    if 'stress' in emotions or 'anxious' in emotions:
        recommendations.extend([
            "I notice you're feeling stressed. Remember, this feeling is temporary and manageable.",
            "Try the 4-7-8 breathing technique - it activates your body's relaxation response.",
            "Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear."
        ])
        activity_category = 'breathing'
    
    elif 'tired' in emotions:
        recommendations.extend([
            "Feeling tired is your body's way of asking for care. Listen to those signals.",
            "A few gentle stretches can help increase blood flow and energy.",
            "Natural light exposure can help boost alertness - try looking out a window."
        ])
        activity_category = 'energy'
    
    elif 'sad' in emotions:
        recommendations.extend([
            "It's okay to feel sad sometimes. Acknowledging your feelings is the first step to healing.",
            "Gentle movement and fresh air can help lift your mood naturally.",
            "Consider reaching out to a friend or doing something kind for yourself."
        ])
        activity_category = 'mindfulness'
    
    elif 'happy' in emotions or 'motivated' in emotions:
        recommendations.extend([
            "It's wonderful that you're feeling positive! Let's maintain this energy.",
            "Use this good energy to tackle something you've been putting off.",
            "Consider sharing your positive mood with someone else - it's contagious!"
        ])
        activity_category = 'mindfulness'
    
    # Sentiment-based fallbacks
    if sentiment_result['sentiment'] == 'NEGATIVE' and not recommendations:
        recommendations.extend([
            "I sense you're going through a challenging time. Remember, difficult feelings are temporary.",
            "Be gentle with yourself today. Small acts of self-care can make a big difference.",
            "Focus on what you can control right now, even if it's just taking the next breath."
        ])
        activity_category = 'breathing'
    
    elif sentiment_result['sentiment'] == 'POSITIVE' and not recommendations:
        recommendations.extend([
            "Your positive energy is wonderful! Keep nurturing that mindset.",
            "Gratitude practices can help maintain and amplify positive feelings.",
            "Consider setting a small, achievable goal while you're feeling motivated."
        ])
        activity_category = 'mindfulness'
    
    else:  # NEUTRAL or no specific recommendations
        recommendations.extend([
            "Thank you for checking in. Regular self-awareness is a powerful wellness practice.",
            "Even small moments of mindfulness throughout the day can improve your overall well-being.",
            "Consider taking a few deep breaths to center yourself."
        ])
        activity_category = 'breathing'
    
    # Select a recommendation
    main_recommendation = random.choice(recommendations) if recommendations else "Take care of yourself today."
    
    # Add wellness tip
    wellness_tips = [
        "💧 Stay hydrated - even mild dehydration affects mood and energy.",
        "🌱 Take micro-breaks every hour, even just 30 seconds of stretching helps.",
        "🌞 Natural light exposure helps regulate your circadian rhythm.",
        "🫂 Social connection is as important for health as diet and exercise.",
        "🎯 Focus on progress, not perfection. Small steps lead to big changes.",
        "🧘 Just 2 minutes of deep breathing can activate your relaxation response.",
        "📱 Consider a 'phone-free' meal today to practice mindful eating.",
        "🚶 A 5-minute walk can boost creativity and reduce stress hormones."
    ]
    
    return {
        'recommendation': main_recommendation,
        'activity_category': activity_category,
        'wellness_tip': random.choice(wellness_tips)
    }

def analyze_sentiment_and_recommend(text, question_index=0, all_answers=None):
    """Main function to analyze sentiment and generate recommendations"""
    try:
        # For comprehensive analysis (question_index 4), analyze all answers
        if question_index == 4 and all_answers:
            return analyze_comprehensive_checkin(all_answers)
        
        # Basic sentiment analysis
        sentiment_result = analyze_sentiment_basic(text)
        
        # Detect specific emotions
        emotions = detect_emotions(text)
        
        # Analyze numeric responses
        numeric_analysis = analyze_numeric_response(text, question_index)
        
        # Generate recommendations
        recommendation_data = generate_recommendation(
            sentiment_result, emotions, numeric_analysis, question_index
        )
        
        # Get a wellness activity
        activity = get_wellness_activity_by_category(recommendation_data['activity_category'])
        
        # Determine final sentiment label
        final_sentiment = sentiment_result['sentiment']
        
        # Override based on detected emotions or numeric analysis
        if 'stress' in emotions or (numeric_analysis and numeric_analysis.get('category') == 'stress' and numeric_analysis.get('level') == 'high'):
            final_sentiment = 'STRESSED'
        elif 'tired' in emotions or (numeric_analysis and numeric_analysis.get('category') == 'energy' and numeric_analysis.get('level') == 'low'):
            final_sentiment = 'TIRED'
        elif 'sad' in emotions:
            final_sentiment = 'SAD'
        elif 'happy' in emotions:
            final_sentiment = 'HAPPY'
        elif 'angry' in emotions:
            final_sentiment = 'ANGRY'
        elif 'calm' in emotions:
            final_sentiment = 'CALM'
        
        return {
            'sentiment': final_sentiment,
            'sentiment_score': round(sentiment_result['polarity'], 2),
            'confidence': round(sentiment_result['confidence'], 2),
            'emotions': emotions,
            'recommendation': recommendation_data['recommendation'],
            'wellness_tip': recommendation_data['wellness_tip'],
            'suggested_activity': activity,
            'numeric_analysis': numeric_analysis
        }
        
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        # Return safe fallback
        return {
            'sentiment': 'NEUTRAL',
            'sentiment_score': 0.0,
            'confidence': 0.0,
            'emotions': [],
            'recommendation': "Thank you for your check-in. Take care of yourself today.",
            'wellness_tip': "🧘 Remember to breathe deeply and be kind to yourself.",
            'suggested_activity': None,
            'numeric_analysis': None
        }

def analyze_comprehensive_checkin(all_answers):
    """Analyze all answers from a complete check-in session"""
    try:
        # Extract numeric scores from answers
        energy_score = None
        stress_score = None
        sleep_score = None
        workload_text = ""
        
        for answer in all_answers:
            question = answer.get('question', '')
            answer_text = answer.get('answer', '')
            
            if 'energized' in question.lower():
                energy_score = analyze_numeric_response(answer_text, 1)
            elif 'stress level' in question.lower():
                stress_score = analyze_numeric_response(answer_text, 2)
            elif 'sleep' in question.lower():
                sleep_score = analyze_numeric_response(answer_text, 3)
            elif 'workload' in question.lower():
                workload_text = answer_text
        
        # Determine overall wellness state
        overall_sentiment = 'NEUTRAL'
        primary_concerns = []
        recommendations = []
        activity_category = 'breathing'
        
        # Analyze energy
        if energy_score and energy_score['level'] == 'low':
            primary_concerns.append('low energy')
            recommendations.append("Your energy seems low. Consider a quick movement break or some natural light exposure.")
            activity_category = 'energy'
        
        # Analyze stress
        if stress_score and stress_score['level'] == 'high':
            primary_concerns.append('high stress')
            recommendations.append("Your stress level is elevated. Let's focus on relaxation techniques.")
            activity_category = 'breathing'
            overall_sentiment = 'STRESSED'
        
        # Analyze sleep
        if sleep_score and sleep_score['level'] == 'poor':
            primary_concerns.append('poor sleep')
            recommendations.append("Poor sleep affects everything. Consider establishing a calming bedtime routine.")
            if activity_category == 'breathing':
                activity_category = 'relaxation'
        
        # Analyze workload
        if workload_text:
            workload_lower = workload_text.lower()
            if any(word in workload_lower for word in ['overwhelming', 'too much', 'crazy', 'insane', 'impossible']):
                primary_concerns.append('workload overwhelm')
                recommendations.append("Your workload seems overwhelming. Consider breaking tasks into smaller chunks.")
                if not primary_concerns or primary_concerns == ['workload overwhelm']:
                    activity_category = 'mindfulness'
        
        # Generate comprehensive recommendation
        if not recommendations:
            recommendations.append("Thank you for your check-in. You seem to be in a balanced state today.")
            overall_sentiment = 'POSITIVE'
        
        # Combine recommendations
        main_recommendation = " ".join(recommendations)
        
        # Add specific wellness tip based on concerns
        if 'high stress' in primary_concerns:
            wellness_tip = "🧘 Try the 4-7-8 breathing technique: Inhale for 4, hold for 7, exhale for 8."
        elif 'low energy' in primary_concerns:
            wellness_tip = "⚡ A 5-minute walk or some gentle stretching can boost your energy naturally."
        elif 'poor sleep' in primary_concerns:
            wellness_tip = "🌙 Create a relaxing bedtime routine and avoid screens 1 hour before sleep."
        else:
            wellness_tip = "💚 Keep up the great work! Regular check-ins like this are powerful for maintaining wellness."
        
        # Get appropriate wellness activity
        activity = get_wellness_activity_by_category(activity_category)
        
        return {
            'sentiment': overall_sentiment,
            'sentiment_score': 0.5 if overall_sentiment == 'POSITIVE' else -0.3 if overall_sentiment == 'STRESSED' else 0.0,
            'confidence': 0.8,
            'emotions': primary_concerns,
            'recommendation': main_recommendation,
            'wellness_tip': wellness_tip,
            'suggested_activity': activity,
            'numeric_analysis': {
                'energy': energy_score,
                'stress': stress_score,
                'sleep': sleep_score
            }
        }
        
    except Exception as e:
        print(f"Error in comprehensive analysis: {e}")
        return {
            'sentiment': 'NEUTRAL',
            'sentiment_score': 0.0,
            'confidence': 0.0,
            'emotions': [],
            'recommendation': "Thank you for completing your check-in. Take care of yourself today.",
            'wellness_tip': "🧘 Remember to breathe deeply and be kind to yourself.",
            'suggested_activity': None,
            'numeric_analysis': None
        }

def get_contextual_response(question_index, user_response):
    """Get contextual responses based on the specific question asked"""
    responses = {
        0: "Thanks for starting your wellness check-in! Your self-awareness is the first step to better mental health.",
        1: "I understand your energy level today. Let's work with where you're at right now.",
        2: "Thank you for sharing your stress level. Remember, stress is manageable with the right techniques.",
        3: "Sleep quality affects everything. Let's focus on what we can do to support your rest.",
        4: "I hear you about your workload. Finding balance is key to sustainable productivity.",
        5: "Thank you for completing your check-in. You've taken an important step for your wellness today."
    }
    
    return responses.get(question_index, "Thank you for sharing that with me.")

# Test function
if __name__ == '__main__':
    test_messages = [
        "I'm feeling really stressed about work today, probably an 8 out of 10",
        "My energy is super low, maybe a 3. Didn't sleep well last night",
        "I'm actually feeling pretty good today! Had great sleep and feeling motivated",
        "Overwhelmed with everything right now. Too much to handle",
        "Just okay, nothing special. Average day I guess"
    ]
    
    print("Testing Sentiment Analysis:")
    print("=" * 50)
    
    for i, message in enumerate(test_messages):
        print(f"\nTest {i+1}: {message}")
        result = analyze_sentiment_and_recommend(message, question_index=i%5)
        print(f"Sentiment: {result['sentiment']}")
        print(f"Score: {result['sentiment_score']}")
        print(f"Emotions: {result['emotions']}")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Tip: {result['wellness_tip']}")
        print("-" * 30)
