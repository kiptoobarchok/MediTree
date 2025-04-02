# app/core/llm.py
import os
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain.llms import AzureOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain.schema import HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationChain
from typing import List, Dict, Any
import openai

# Load environment variables
load_dotenv()

class ArborAIChat:
    def __init__(self):
        # Configure Azure OpenAI
        self.azure_openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.gpt4_deployment = os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT")
        self.dalle_deployment = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT")
        
        # Initialize LLMs
        self.chat_llm = self._init_chat_model()
        self.image_llm = self._init_image_model()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        # System prompts
        self.tree_care_prompt = """You are ArborAI, an expert arborist and horticulturist. Provide:
        1. Specific care advice for {tree_name}
        2. Solutions for: {user_query}
        3. Common mistakes to avoid
        4. When to consult a professional
        
        Current season: {season}
        User location: {location}
        
        Answer in markdown with clear sections."""
        
        self.marketplace_prompt = """As a plant nursery assistant, help users:
        - Find trees matching: {criteria}
        - Compare options
        - Understand pricing factors
        - Estimate shipping costs
        
        Nursery inventory: {inventory}"""

    def _init_chat_model(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI GPT-4 for chat"""
        return AzureChatOpenAI(
            openai_api_base=self.azure_endpoint,
            openai_api_key=self.azure_openai_key,
            deployment_name=self.gpt4_deployment,
            temperature=0.7,
            max_tokens=1000,
            openai_api_version="2023-05-15"
        )

    def _init_image_model(self) -> AzureOpenAI:
        """Initialize Azure OpenAI for image generation"""
        return AzureOpenAI(
            openai_api_base=self.azure_endpoint,
            openai_api_key=self.azure_openai_key,
            deployment_name=self.dalle_deployment,
            temperature=0.9,
            max_tokens=500
        )

    def get_tree_care_advice(
        self,
        tree_name: str,
        user_query: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate personalized tree care advice"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.tree_care_prompt),
            HumanMessage(content=user_query)
        ])
        
        chain = LLMChain(
            llm=self.chat_llm,
            prompt=prompt,
            memory=self.memory
        )
        
        return chain.run({
            "tree_name": tree_name,
            "user_query": user_query,
            "season": context.get("season", "unknown"),
            "location": context.get("location", "unknown")
        })

    def recommend_trees(self, criteria: Dict[str, Any]) -> List[Dict[str, str]]:
        """Recommend trees based on user criteria"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.marketplace_prompt),
            HumanMessage(content=str(criteria))
        ])
        
        chain = LLMChain(
            llm=self.chat_llm,
            prompt=prompt
        )
        
        response = chain.run({
            "criteria": criteria,
            "inventory": self._get_current_inventory()
        })
        
        return self._parse_recommendations(response)

    def generate_tree_image(self, description: str) -> str:
        """Generate tree image using DALL-E"""
        try:
            response = openai.Image.create(
                engine=self.dalle_deployment,
                prompt=f"Botanically accurate illustration of {description}",
                size="1024x1024",
                quality="hd",
                n=1
            )
            return response["data"][0]["url"]
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    def _get_current_inventory(self) -> str:
        """Mock inventory fetch - replace with DB call"""
        return """1. Japanese Maple - $34.99
                2. Red Oak - $29.99
                3. Blueberry Bush - $24.99"""

    def _parse_recommendations(self, text: str) -> List[Dict[str, str]]:
        """Parse LLM response into structured recommendations"""
        # Implement parsing logic based on your response format
        return [{"name": "Sample Tree", "reason": "Matches your criteria"}]

# Singleton instance for easy import
arborai_llm = ArborAIChat()

# Example usage:
# advice = arborai_llm.get_tree_care_advice("Japanese Maple", "How often to water?")
# image_url = arborai_llm.generate_tree_image("Mature oak tree with acorns")