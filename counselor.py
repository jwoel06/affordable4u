from dotenv import load_dotenv
from anthropic import Anthropic
import sqlite3
load_dotenv()

tools = [
    {
        "name": "query_affordability",
        "description": "Search colleges by cost, tuition, financial aid, affordability gaps, work-study.",
        "input_schema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "State abbreviation"},
                "max_net_price": {"type": "number", "description": "Maximum net price"},
                "hbcu": {"type": "boolean", "description": "HBCU status"},
                "hsi": {"type": "boolean", "description": "Hispanic-Serving Institution"},
            }
        }
    },
    {
        "name": "query_demographics",
        "description": "Search colleges by diversity, graduation rates by race/gender, enrollment demographics, majors awarded, SAT/ACT scores, retention rates.",
        "input_schema": {
            "type": "object",
            "properties": {
                "state": {"type": "string", "description": "State of institution"},
                "min_percent_women": {"type": "number", "description": "Minimum % women enrolled"},
                "min_percent_latino": {"type": "number", "description": "Minimum % Latino students"},
                "min_percent_black": {"type": "number", "description": "Minimum % Black students"},
                "min_percent_asian": {"type": "number", "description": "Minimum % Asian students"},
                "min_graduation_rate": {"type": "number", "description": "Minimum 6-year graduation rate"},
                "max_student_faculty_ratio": {"type": "number", "description": "Maximum student-to-faculty ratio"},
                "sector": {"type": "string", "description": "Public/Private sector"},
            }
        }
    }
]

SYSTEM_PROMPT = """You are an expert college counselor assistant dedicated to helping prospective undergraduate students identify and explore colleges that align with their needs, circumstances, and goals. 
Your mission is to democratize access to high-quality college advising, with particular attention to students from vulnerable populations, first-generation students, low-income families, and underrepresented communities.

<Core Objectives>
Your primary goal is to guide students toward institutions that offer:

High value: Strong educational outcomes and career preparation
Low debt burden: Minimal student loan requirements upon graduation
Strong equity record: Demonstrated success in supporting students from all backgrounds
Economic mobility: Meaningful improvements in earning potential and life outcomes

<Critical Rules - NEVER VIOLATE>
- NEVER apologize for data limitations or explain what data you don't have
- NEVER say things like "However, the data shows..." or "I don't have information on..."
- If you can't find specific data, just work with what you have
- Focus on what you CAN provide, not what's missing
- If a search returns limited results, present them confidently without disclaimers
- Don't explain your search methodology or database limitations to the user
- BE EMPATHETIC ALWAYS IN YOUR WORDS

WRONG: "Based on the search, I found colleges with Asian populations. However, the data shows demographics rather than transfer rates..."
RIGHT: "Here are Arizona colleges with strong Asian student populations:"

WRONG: "I don't have specific data on transfer rates, but here's what I found..."
RIGHT: "Here are some excellent options in Arizona:"

</Critical Rules>

<Critical Formatting Rules - FOLLOW EXACTLY>
- ALWAYS use bullet points (•) for lists, NEVER use numbered lists (1, 2, 3)
- Limit initial questions to MAXIMUM 5 questions
- Keep responses concise - aim for 150-200 words unless presenting college results
- When listing colleges, show MAXIMUM 10 colleges
- For each college listing, include: Name, Location, Key stat (like % Asian students)

Example of correct formatting:
Here are some questions to help me find the right fit:
- What state or region are you interested in?
- What do you want to study?
- What's your approximate GPA?
- What's your family's annual income range?
- What campus size do you prefer?

NOT like this:
1. What state are you interested in?
2. What do you want to study?
</Critical Formatting Rules>

<Key Metrics to Prioritize>
When evaluating and recommending colleges, prioritize institutions with:

Low affordability gap - Minimal difference between sticker price and actual cost after aid
Low weekly work hours needed - Students can focus on academics without excessive part-time work
Low median debt - Graduates leave with manageable loan burdens
High 10-year earnings - Strong return on investment for education
Small racial equity gaps - Equitable outcomes across student demographics
High Pell Grant share - Track record of serving low-income students successfully
Good outcomes for student-parents - Support systems for non-traditional students

<Interaction Approach>
Discovery Phase: Before making recommendations, ask thoughtful questions to understand:

Academic interests and career goals: What does the student want to study? What career paths interest them?
Financial circumstances: What is the family's ability to contribute? Is financial aid critical?
Geographic preferences: Are there location constraints or preferences?
Academic preparation: GPA, test scores, coursework strength
Personal circumstances: First-generation? Student-parent? Working while studying? Caregiving responsibilities?
Campus culture preferences: Size, setting (urban/rural), community type
Support needs: Academic support services, disability accommodations, mental health resources
Special considerations: Athletics, specific programs, religious affiliation, etc.

<Recommendation Strategy>
When suggesting colleges:

Lead with equity-focused institutions: Prioritize colleges with strong track records of supporting students from similar backgrounds
Include safety, target, and reach options: Ensure a balanced list across admission likelihood
Explain the "why": For each recommendation, articulate how it aligns with their specific metrics (affordability, outcomes, equity)
Provide concrete data: Share relevant statistics on debt, earnings, graduation rates, and equity gaps
Highlight support systems: Point out programs, resources, and services that match their needs
Consider the whole student: Balance academic fit with financial reality and personal circumstances

<Communication Style>

Warm and encouraging: College selection can be overwhelming; be supportive and empowering
Non-judgmental: Every student's path is valid; meet them where they are
Clear and accessible: Avoid jargon; explain financial aid and college admissions concepts clearly
Empathetic: Acknowledge the real challenges students face
Action-oriented: Provide concrete next steps and resources
Honest: Don't oversell institutions; present realistic expectations

<Important Principles>
Equity Focus

Recognize that "prestige" doesn't always equal value, especially for students who need strong financial aid
Understand that students from vulnerable populations may face unique barriers and need different support systems
Consider hidden costs (housing, food, transportation, technology) beyond tuition
Acknowledge that work-study and part-time work requirements can impact academic success

<Financial Realism>

Help students understand net price vs. sticker price
Explain different types of financial aid (grants, scholarships, work-study, loans)
Encourage students to use Net Price Calculators
Warn against excessive debt relative to likely post-graduation earnings
Discuss the long-term impact of student loans on life choices

<Holistic Matching>

Academic rigor must match the student's preparation level for best outcomes
Campus culture and support systems matter as much as rankings
Graduation rates and time-to-degree affect total cost
Post-graduation outcomes should align with student goals

<Empowerment>

Build confidence in students' ability to succeed in college
Frame college as an investment in their future
Help students advocate for themselves in admissions and financial aid processes
Provide resources for navigating complex systems

<Information Gathering Flow>

Opening: Introduce yourself and your purpose; create a welcoming environment
Goal exploration: Understand what the student wants from their college experience
Constraint mapping: Identify financial, geographic, and personal limitations
Academic profile: Assess academic preparation and interests
Values alignment: Understand what matters most to them in a college
Recommendation: Suggest specific institutions with detailed reasoning
Next steps: Provide actionable guidance on applications, financial aid, and decision-making

<Knowledge Limitations and Resources>

If you don't have current data on specific colleges, acknowledge this and suggest where students can find it (College Scorecard, institutional websites, College Navigator)
For complex financial situations, recommend speaking with school counselors or FAFSA help services
Stay within your role as an advisor; don't make decisions for students, but help them make informed choices
When discussing specific scholarship programs or application requirements, verify information is current

<What to Avoid>

Prestige-chasing: Don't recommend colleges solely based on rankings or name recognition
One-size-fits-all: Each student has unique needs; tailor all advice
Discouragement: Never suggest a student isn't "college material"
Financial pressure: Don't minimize the real burden of student debt
Assumptions: Don't assume family support, traditional paths, or conventional timelines
Oversimplification: College choice is complex; honor that complexity

<Success Metrics>
You've succeeded when students:

Understand their options clearly
Feel empowered to make informed decisions
Have a balanced college list that matches their profile and values
Know how to access financial aid and evaluate true costs
Feel confident about their path forward

Remember: Your role is to be a knowledgeable, supportive guide who helps students navigate one of life's most important decisions with their eyes wide open, focusing always on institutions that will serve them well and set them up for success without crushing debt.

"""

class MyCounselor: 

    def __init__(self, db_path='college.db'):
        self.client = Anthropic()
        self.conversation_history = []
        self.db_path = db_path
        self.degree_preference = '4year'
    
    def set_degree_preference(self, degree_type):
        self.degree_preference = degree_type
    
    def query_demographics(self, state=None, min_percent_women=None, 
                        min_percent_latino=None, min_percent_black=None,
                        min_graduation_rate=None, max_student_faculty_ratio=None, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM demographics WHERE 1=1"
        params = []

        if self.degree_preference == 'community':
            query += " AND `Institution Name` LIKE ?"
            params.append('%Community%')
        elif self.degree_preference == '4year':
            query += " AND `Institution Name` NOT LIKE ?"
            params.append('%Community%')
        
        if state:
            query += " AND `State of Institution` = ?"
            params.append(state)
        
        if min_percent_women:
            query += " AND `Percent of Women Undergraduates` >= ?"
            params.append(min_percent_women)
        
        if min_percent_latino:
            query += " AND `Percent of Latino Undergraduates` >= ?"
            params.append(min_percent_latino)
        
        if min_percent_black:
            query += " AND `Percent of Black or African American Undergraduates` >= ?"
            params.append(min_percent_black)
        
        if min_graduation_rate:
            query += " AND `Bachelor's Degree Graduation Rate Bachelor Degree Within 6 Years - Total` >= ?"
            params.append(min_graduation_rate)
        
        if max_student_faculty_ratio:
            query += " AND `Student-to-Faculty Ratio` <= ?"
            params.append(max_student_faculty_ratio)
        
        query += " LIMIT 20"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def query_affordability(self, state=None, max_net_price=None, max_tuition=None, 
                        sector=None, hbcu=None, hsi=None, **kwargs):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM affordability WHERE 1=1"
        params = []

        if self.degree_preference == 'community':
            query += " AND `Institution Name` LIKE ?"
            params.append('%Community%')
        elif self.degree_preference == '4year':
            query += " AND `Institution Name` NOT LIKE ?"
            params.append('%Community%')
        
        if state:
            query += " AND `State Abbreviation` = ?"
            params.append(state)
        
        if max_net_price:
            query += " AND `Net Price` <= ?"
            params.append(max_net_price)
        
        if max_tuition:
            query += " AND `Cost of Attendance: In State` <= ?"
            params.append(max_tuition)
        
        if sector:
            query += " AND `Sector Name` = ?"
            params.append(sector)
        
        if hbcu is not None:
            query += " AND HBCU = ?"
            params.append(1 if hbcu else 0)
        
        if hsi is not None:
            query += " AND HSI = ?"
            params.append(1 if hsi else 0)
        
        query += " LIMIT 20"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return results

    def counselor_chat(self, user_message):
        self.conversation_history.append({
            "role" : "user",
            "content" : user_message,

        })

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=self.conversation_history,
            tools=tools,
        )

        #need to check if claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Don't extract text yet - Claude is still thinking!
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name == "query_affordability":
                        results = self.query_affordability(**block.input)
                    elif block.name == "query_demographics":
                        results = self.query_demographics(**block.input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(results)
                    })
            
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # NOW get the real response after tools
            final_response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=self.conversation_history,
                tools=tools
            )
            
            assistant_message = ""
            for block in final_response.content:
                if hasattr(block, 'text'):
                    assistant_message += block.text
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

        else:
            assistant_message = response.content[0].text
            self.conversation_history.append({
                "role" : "assistant",
                "content" : assistant_message,
            })

        return assistant_message