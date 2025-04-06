# 🌿 MediTree

---

_Sustainable Identification and Research of Medicinal Trees for Healthcare and Conservation_

---

A web application that provides personalized plant care advice, a plant marketplace,weather-based gardening recommendations and more.

## Resources


![alt text](Microsoft-Data-AI-Hackathon-Timeline-1024x576.png)
**MS - Data AI Hack Roadmap**

---

- [Hack Together: The Microsoft Data + AI Kenya Hack](https://blog.fabric.microsoft.com/en/blog/hack-together-the-microsoft-data-ai-kenya-hack?ft=All)

- [Hackathon Documentation](https://microsoft.github.io/Data-AI-Kenya-Hack/)

- [Access to AZURE OpenAI](https://microsoft.github.io/Data-AI-Kenya-Hack/AI_ACCESS.html)


#### Model Details
| Mdel    | Model Name | Docs  | *(with Python) |
| -------- | ------- |---------| --------------
| GPT-4o | gtp-4o | [Docs](https://aka.ms/fabric-hack24-python-docs-gtp4) |
| GPT-4o-mini | gpt-4o-mini    | [Docs](https://aka.ms/fabric-hack24-python-docs-gtp4)|
| Embeddings    |  text-embedding-ada-002   | [Embeddings Docs](https://aka.ms/fabric-hack24-python-docs-embeddings)|
| DALL-E 3   | dall-e-3 | [DALL-E Docs](https://aka.ms/fabric-hack24-python-docs-dalle) | [Azure OpenAI DALL-E - Python](https://aka.ms/fabric-hack24-python-eg-dalle) | 

### Events
-----
```
March 18th @ 7 PM East African Time: Ready, Set, Hack: and do more with Azure AI and Microsoft Fabric
March 20th @ 7 PM East African Time: A tidy introduction to Microsoft Fabric
March 25th @ 7 PM East African Time: Building Scalable Data Solutions with Microsoft Fabric’s Data Warehouse
March 27th @ 7 PM East African Time: Building high scale RAG Applications with the Eventhouse in Microsoft Fabric
April 1st @ 7 PM East African Time: Building AI Agents using Azure AI Agent Service
April 3rd @ 7 PM East African Time: Wrap up – How to Submit your hack & Next steps
```
-----

#### Folder Structure
```
MediTree/
├── application/
│ ├── static/ # CSS, JS, images
│ ├── templates/ # HTML templates
│ ├── init.py # App factory
│ ├── auth.py # Authentication routes
│ ├── chatbot.py # AI chat functionality
│ ├── database.py # DB initialization
│ ├── forms.py # WTForms
│ ├── marketplace.py # Marketplace routes
│ ├── models.py # SQLAlchemy models
│ └── plantcare.py # Plant care routes
├── arborai.db/ # Database file
├── tests/ # Unit tests
├── .env # Environment variables
├── config.py # Configuration
└── run.py # Launch script
```

---


