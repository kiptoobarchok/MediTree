from openai import AzureOpenAI
from datetime import datetime
from flask import current_app
from application.models import ChatSession, ChatMessage, db
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

class PlantCareChatbot:
    def __init__(self):
        self.system_prompt = """
        You are Arborai, a knowledgeable plant care assistant. Provide:
        1. Personalized care instructions
        2. Optimal growing conditions
        3. Seasonal care tips
        4. Troubleshooting advice
        
        Format responses with clear headings and bullet points.
        """
        self.logger = logging.getLogger(__name__)
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        if not current_app:
            return
            
        required_configs = [
            'AZURE_OPENAI_API_KEY',
            'AZURE_OPENAI_ENDPOINT',
            'AZURE_OPENAI_CHAT_DEPLOYMENT'
        ]
        
        if all(current_app.config.get(key) for key in required_configs):
            self._client = AzureOpenAI(
                api_key=current_app.config['AZURE_OPENAI_API_KEY'],
                api_version=current_app.config.get('AZURE_OPENAI_API_VERSION', '2023-05-15'),
                azure_endpoint=current_app.config['AZURE_OPENAI_ENDPOINT']
            )
        else:
            self.logger.warning("Azure OpenAI client not initialized due to missing configs")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_azure_openai(self, messages):
        """Make API call with retry logic"""
        if not self._client:
            raise ValueError("Azure OpenAI client not initialized")

        try:
            response = self._client.chat.completions.create(
                model=current_app.config['AZURE_OPENAI_CHAT_DEPLOYMENT'],
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            return response
        except Exception as e:
            self.logger.error(f"Azure API call failed: {str(e)}")
            raise ValueError("Failed to communicate with plant care assistant")

    def initialize_chat(self, user_id):
        """Create new chat session"""
        try:
            session = ChatSession(
                user_id=user_id,
                title="New Chat",
                created_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            return session.id
        except Exception as e:
            self.logger.error(f"Session creation failed: {str(e)}")
            raise ValueError("Could not start chat session")

    def get_response(self, session_id, user_message):
        """Get AI response for user message"""
        try:
            # Save user message
            user_msg = ChatMessage(
                session_id=session_id,
                content=user_message,
                is_user=True,
                created_at=datetime.utcnow()
            )
            db.session.add(user_msg)

            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
            history = ChatMessage.query.filter_by(session_id=session_id)\
                .order_by(ChatMessage.created_at.desc())\
                .limit(5)\
                .all()
            
            for msg in reversed(history):
                messages.append({
                    "role": "user" if msg.is_user else "assistant",
                    "content": msg.content
                })

            # Get AI response
            if self._client:
                response = self._call_azure_openai(messages)
                bot_response = response.choices[0].message.content
            else:
                bot_response = self._get_fallback_response(user_message)

            # Save bot response
            bot_msg = ChatMessage(
                session_id=session_id,
                content=bot_response,
                is_user=False,
                created_at=datetime.utcnow()
            )
            db.session.add(bot_msg)
            db.session.commit()

            return bot_response, None

        except Exception as e:
            self.logger.error(f"Error in get_response: {str(e)}")
            db.session.rollback()
            return self._get_fallback_response(user_message), str(e)

    def _get_fallback_response(self, user_message):
        """Provide fallback when Azure is unavailable"""
        fallbacks = [
            "I'm currently unable to access my full knowledge base. As a general tip: "
            "most plants prefer consistent watering when the top inch of soil is dry.",
            
            "My plant care resources are temporarily unavailable. Remember that "
            "overwatering is the most common cause of houseplant problems.",
            
            "I can't access detailed information right now. A good practice is to "
            "research your specific plant's native environment for care clues."
        ]
        import random
        return random.choice(fallbacks)