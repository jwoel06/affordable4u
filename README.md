Affordable4U - College Counseling Chatbot

**Note: This is a demo application for educational purposes.**

Overview
Affordable4U is a Flask-based web application that provides AI-powered college counseling focused on equity and accessibility. The system helps prospective undergraduate students, particularly those from underserved populations, identify colleges that offer high value, low debt burden, strong equity records, and economic mobility opportunities.

The application uses Anthropic's Claude AI as a conversational agent with function-calling capabilities to query a SQLite database containing college equity metrics and social impact data. The chatbot provides personalized college recommendations based on student preferences and degree type (4-year programs).

User Preferences
Preferred communication style: Simple, everyday language.

System Architecture
Frontend Architecture
Technology Stack:

HTML templates with Bootstrap 5 for responsive UI
Bootstrap Icons for visual elements
Marked.js for markdown rendering (chat responses)
Vanilla JavaScript for chat interactions
Design Pattern:

Server-side rendering with Jinja2 templates
AJAX-based chat interface using fetch API
Three-page structure: main chat (index.html), FAQ, and About pages
Sidebar navigation pattern for consistent UX
Rationale: Simple, lightweight frontend without complex frameworks allows for quick iterations and easy maintenance. Bootstrap provides professional styling out-of-the-box while keeping the codebase minimal.

Backend Architecture
Framework: Flask (Python web microframework)

Design Pattern: MVC-inspired separation

app.py: Routes and HTTP handling (Controller)
counselor.py: Business logic and AI integration (Model)
templates/: View layer
Key Components:

Flask Application (app.py)

RESTful API endpoint /api/chat for chat interactions
Static page routes for FAQ and About sections
Stateful chatbot instance (single MyCounselor object)
Handles degree preference setting (4-year vs other degree types)
AI Counselor Module (counselor.py)

Integrates Anthropic's Claude API
Implements function-calling (tools) for database queries
System prompt defines counselor personality and rules
Emphasizes equity-focused college search with specific constraints:
Never apologizes for data limitations
Focuses on positive, empathetic guidance
Prioritizes underserved student populations
Tool Definition:

query_equity_outcomes: Searches colleges by equity metrics including Pell Grant recipients, racial demographics, debt-to-income ratios, social impact scores, and champion/hidden gem status
Rationale: Flask provides simplicity and flexibility for this chatbot use case. The conversational AI pattern with function-calling allows natural language queries to be translated into structured database searches without building complex query interfaces.

Data Storage
Database: SQLite (new_college.db)

Schema:

Primary table: social (contains social impact and equity metrics)
Imported from CSV: data/social_impact_final.csv
Data Pipeline:

import_csv.py: Pandas-based ETL script
One-time import process converts CSV to SQLite
Source Data: The data/metrics directory contains calculation scripts for equity metrics derived from:

College Results View 2021 dataset
Affordability Gap Data AY2022-23
Key Metrics Calculated:

Graduation rates by race/ethnicity
Pell Grant recipient percentages
Debt-to-income ratios
Social impact scores
ROI calculations for different demographics
Rationale: SQLite chosen for simplicity and zero-configuration deployment. Single-file database works well for read-heavy workload with pre-calculated metrics. No concurrent write operations required since data is batch-imported.

Alternative Considered: PostgreSQL would provide better query performance and concurrent access but adds deployment complexity unnecessary for this use case.

Authentication & Authorization
Current State: No authentication implemented

The application currently runs as an open chatbot without user accounts or session management beyond degree preference storage in the chatbot instance.

Implication: All users share the same chatbot instance state, which may cause preference conflicts in multi-user scenarios.

External Dependencies
Third-Party APIs
Anthropic Claude API

Purpose: Conversational AI engine
Integration: Official anthropic Python SDK (v0.73.0)
Authentication: API key via environment variables (.env file)
Function: Powers the MyCounselor chatbot with tool-calling capabilities
Python Libraries
Web Framework:

Flask==3.1.2: Core web application framework
flask-cors==4.0.0: Cross-Origin Resource Sharing support
gunicorn==21.2.0: Production WSGI server
Data Processing:

pandas==2.1.0: CSV import and data manipulation
numpy==1.24.0: Numerical operations for metric calculations
scikit-learn==1.3.0: Data preprocessing (MinMaxScaler for normalization)
AI & Configuration:

anthropic==0.73.0: Claude API client
python-dotenv==1.2.1: Environment variable management
Frontend Libraries (CDN-based)
Bootstrap 5.3.0: UI framework
Bootstrap Icons 1.11.0: Icon library
Marked.js: Markdown parser for AI responses
Database
SQLite3: Built-in Python library, no external service required

Environment Variables
Required configuration in .env:

Anthropic API key for Claude access
Rationale for Dependency Choices:

Anthropic Claude chosen for strong reasoning and function-calling capabilities essential for equity-focused counseling
Pandas selected for its CSV handling and data transformation capabilities
Flask chosen over Django for simplicity since no admin interface or ORM needed
CDN-hosted frontend libraries reduce bundle size and leverage browser caching
