import openai
from flask import current_app
from application.models import ChatSession, ChatMessage, db
from datetime import datetime

class PlantCareChatbot:
    def __init__(self):
        self.system_prompt = """
        You are a knowledgeable plant care assistant named arborai. Your role is to provide:
        1. Personalized care instructions for plants based on user queries
        2. Optimal growing conditions (light, water, soil, temperature)
        3. Seasonal care tips and reminders
        4. Recommendations for plants based on location and current weather
        5. Advice on planting times and techniques
        6. Troubleshooting for common plant problems
        
        Be friendly, professional, and provide detailed, accurate information. 
        If you're unsure about something, say so rather than guessing.
        """

    def initialize_chat(self, user_id):
        session = ChatSession(user_id=user_id, title="New Chat")
        db.session.add(session)
        db.session.commit()
        return session.id

    def get_response(self, session_id, user_message):
        # Get the chat session
        session = ChatSession.query.get(session_id)
        if not session:
            return None, "Session not found"

        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            content=user_message,
            is_user=True
        )
        db.session.add(user_msg)
        
        # Get previous messages for context
        previous_messages = ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.asc()).all()
        
        # Format messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in previous_messages:
            role = "user" if msg.is_user else "assistant"
            messages.append({"role": role, "content": msg.content})
        
        # Add the new user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Configure Azure OpenAI
            openai.api_type = "azure"
            openai.api_key = current_app.config['AZURE_OPENAI_API_KEY']
            openai.api_base = current_app.config['AZURE_OPENAI_ENDPOINT']
            openai.api_version = current_app.config['AZURE_OPENAI_API_VERSION']
            
            response = openai.ChatCompletion.create(
                engine=current_app.config['AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'],
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            bot_response = response.choices[0].message['content']
            
            # Save bot response
            bot_msg = ChatMessage(
                session_id=session_id,
                content=bot_response,
                is_user=False
            )
            db.session.add(bot_msg)
            db.session.commit()
            
            return bot_response, None
        except Exception as e:
            return None, str(e)

    def get_plant_recommendation(self, location, season):
        prompt = f"""
        Based on the following location and season, recommend suitable plants or trees to grow:
        - Location: {location}
        - Season: {season}
        
        Provide:
        1. A list of 5-8 suitable plants/trees
        2. Brief description of each
        3. Ideal planting time
        4. Basic care requirements
        5. Any special considerations for the location
        
        Format the response in clear, bullet points.
        """
        
        try:
            response = openai.ChatCompletion.create(
                engine=current_app.config['AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message['content'], None
        except Exception as e:
            return None, str(e)