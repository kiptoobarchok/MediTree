from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from application.models import ChatSession, ChatMessage, PlantRecommendation, db
from application.chatbot import PlantCareChatbot
from application.weather import WeatherService
from datetime import datetime

plantcare_bp = Blueprint('plantcare', __name__)
chatbot = PlantCareChatbot()
weather_service = WeatherService()

@plantcare_bp.route('/plantcare')
@login_required
def plantcare_home():
    return render_template('plantcare/index.html')

@plantcare_bp.route('/plantcare/chat', methods=['GET', 'POST'])
@login_required
def plant_care_chat():
    # Get or create chat session
    session = ChatSession.query.filter_by(user_id=current_user.id)\
        .order_by(ChatSession.created_at.desc()).first()
    
    if not session:
        session_id = chatbot.initialize_chat(current_user.id)
        session = ChatSession.query.get(session_id)
    
    messages = ChatMessage.query.filter_by(session_id=session.id)\
        .order_by(ChatMessage.created_at.asc()).all()
    
    if request.method == 'POST':
        user_message = request.form.get('message')
        if user_message:
            response, error = chatbot.get_response(session.id, user_message)
            if error:
                flash(f'Error: {error}', 'danger')
    
    return render_template('plantcare/chat.html', session=session, messages=messages)

@plantcare_bp.route('/plantcare/chat/new', methods=['POST'])
@login_required
def new_chat_session():
    session_id = chatbot.initialize_chat(current_user.id)
    return redirect(url_for('plantcare.plant_care_chat'))

@plantcare_bp.route('/plantcare/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not session_id or not message:
        return jsonify({'error': 'Missing data'}), 400
    
    response, error = chatbot.get_response(session_id, message)
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({'response': response})

@plantcare_bp.route('/plantcare/recommendations', methods=['GET', 'POST'])
@login_required
def plant_recommendations():
    location = None
    weather_data = None
    recommendations = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location')
        if location:
            # Get weather data
            weather_data, weather_error = weather_service.get_current_weather(location)
            if weather_error:
                error = f"Weather data error: {weather_error}"
            
            # Get season
            season = weather_service.get_season(location)
            
            # Get recommendations from database first
            recommendations = PlantRecommendation.query.filter_by(
                location=location,
                season=season
            ).first()
            
            if not recommendations:
                # If not in database, get from chatbot
                response, chat_error = chatbot.get_plant_recommendation(location, season)
                if chat_error:
                    error = f"Chatbot error: {chat_error}"
                else:
                    recommendations = PlantRecommendation(
                        plant_name="Multiple",
                        location=location,
                        season=season,
                        recommendation=response
                    )
                    db.session.add(recommendations)
                    db.session.commit()
            else:
                response = recommendations.recommendation
    
    return render_template('plantcare/recommendations.html',
                         location=location,
                         weather_data=weather_data,
                         recommendations=recommendations.recommendation if recommendations else None,
                         error=error)

@plantcare_bp.route('/plantcare/weather_tips', methods=['GET', 'POST'])
@login_required
def weather_tips():
    location = None
    weather_data = None
    tips = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location')
        if location:
            weather_data, weather_error = weather_service.get_current_weather(location)
            if weather_error:
                error = f"Weather data error: {weather_error}"
            else:
                tips = weather_service.get_gardening_tips(weather_data)
    
    return render_template('plantcare/weather_tips.html',
                         location=location,
                         weather_data=weather_data,
                         tips=tips,
                         error=error)