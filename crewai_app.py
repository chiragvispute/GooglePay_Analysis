#!/usr/bin/env python3
"""
Google Pay Smart Analyzer API with CrewAI
Advanced AI-powered transaction analysis using CrewAI agents
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure LLM for CrewAI to use Gemini
os.environ["OPENAI_API_KEY"] = "dummy"  # CrewAI requires this even when not using OpenAI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup Gemini LLM for CrewAI
gemini_llm = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        # Use a simpler LLM setup for older CrewAI version
        from crewai.llm import LLM
        gemini_llm = LLM(
            model="gemini-pro",
            api_key=GEMINI_API_KEY
        )
    except Exception as e:
        print(f"Warning: Could not configure Gemini LLM: {e}")
        # Fallback to basic analysis without LLM
        gemini_llm = None

# Initialize FastAPI
app = FastAPI(title="Google Pay Smart Analyzer with CrewAI", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@tool
def analyze_transaction_data(transaction_data: str) -> str:
    """Analyze Google Pay transaction data for patterns, insights, and recommendations"""
    try:
        data = json.loads(transaction_data)
        df = pd.DataFrame(data)
        
        if len(df) == 0:
            return "No transactions to analyze"
        
        # Basic analysis
        total_spend = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        top_merchant = df['recipient'].value_counts().head(1).to_dict()
        
        # Monthly trends
        df['month'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m')
        monthly_spend = df.groupby('month')['amount'].sum().to_dict()
        
        # Payment methods
        payment_methods = df['payment_method'].value_counts().to_dict()
        
        analysis = {
            "total_spend": float(total_spend),
            "average_transaction": float(avg_transaction),
            "transaction_count": len(df),
            "top_merchants": dict(df['recipient'].value_counts().head(5)),
            "monthly_trends": monthly_spend,
            "payment_methods": payment_methods,
            "date_range": {
                "start": df['date'].min(),
                "end": df['date'].max()
            }
        }
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

class GPPayAnalyzer:
    def __init__(self):
        self.transactions = []
        self.setup_crew()
        
    def setup_crew(self):
        """Setup CrewAI agents and tasks"""
        
        # Check if we have LLM available
        if not gemini_llm:
            print("Warning: No LLM configured, using basic analysis")
            return
        
        # Financial Analyst Agent
        self.financial_analyst = Agent(
            role='Financial Data Analyst',
            goal='Analyze Google Pay transaction data to identify spending patterns, trends, and financial insights',
            backstory="""You are an expert financial analyst specializing in personal finance and transaction analysis. 
            You excel at identifying spending patterns, detecting anomalies, and providing actionable financial insights 
            from transaction data.""",
            tools=[analyze_transaction_data],
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Financial Advisor Agent
        self.financial_advisor = Agent(
            role='Personal Financial Advisor',
            goal='Provide personalized financial recommendations and budgeting advice based on spending analysis',
            backstory="""You are a certified financial advisor with expertise in personal budgeting, expense optimization, 
            and financial planning. You provide practical, actionable advice to help individuals manage their finances better.""",
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )
        
        # Insights Generator Agent
        self.insights_generator = Agent(
            role='Financial Insights Specialist',
            goal='Generate comprehensive financial insights and identify important trends from transaction data',
            backstory="""You are a specialist in financial data interpretation and insight generation. You excel at 
            finding meaningful patterns in financial data and presenting them in an easy-to-understand format.""",
            llm=gemini_llm,
            verbose=True,
            allow_delegation=False
        )
        
    def parse_html_content(self, html_content: str) -> List[Dict]:
        """Convert Google Pay HTML content to structured JSON with improved date parsing"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find transaction blocks
        blocks = soup.find_all('div', class_=re.compile(r'outer-cell.*mdl-shadow'))
        
        transactions = []
        for i, block in enumerate(blocks):
            try:
                main_text = block.find('div', class_=re.compile(r'mdl-typography--body-1'))
                if not main_text:
                    continue
                    
                text = main_text.get_text(strip=True)
                
                # Extract key data using improved regex
                amount_match = re.search(r'₹\s*([0-9,]+(?:\.[0-9]+)?)', text)
                recipient_match = re.search(r'to\s+(.+?)(?:\s+using|\s+on)', text)
                
                # Better date pattern - looking for proper date format
                date_match = re.search(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', text)
                method_match = re.search(r'using\s+([A-Za-z0-9 \-&()/.]+?)(?:\s+[Xx]+|\s*$)', text)
                
                if amount_match and recipient_match and date_match:
                    amount = float(amount_match.group(1).replace(',', ''))
                    recipient = recipient_match.group(1).strip()
                    
                    # Parse date properly
                    day, month, year = date_match.groups()
                    method = method_match.group(1).strip() if method_match else "UPI"
                    
                    # Validate and format date
                    try:
                        date_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
                        date_formatted = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        continue  # Skip invalid dates
                    
                    transactions.append({
                        'amount': amount,
                        'recipient': recipient,
                        'date': date_formatted,
                        'payment_method': method,
                        'id': f"tx_{i}"
                    })
                    
            except Exception:
                continue
        
        self.transactions = transactions
        return transactions
    
    def analyze_with_crewai(self, query: str, timeframe: str = "all") -> Dict:
        """Use CrewAI to analyze transactions and provide insights"""
        
        # Filter transactions
        filtered_txns = self.filter_by_timeframe(timeframe)
        
        if not filtered_txns:
            return {"error": f"No transactions found for timeframe: {timeframe}"}
        
        # If no LLM configured, return basic analysis
        if not gemini_llm or not hasattr(self, 'financial_analyst'):
            df = pd.DataFrame(filtered_txns)
            total_spend = df['amount'].sum()
            top_merchant = df['recipient'].value_counts().head(1).to_dict()
            
            return {
                "summary": f"Analyzed {len(filtered_txns)} transactions for {timeframe} period",
                "analysis": f"Total spending: ₹{total_spend:,.2f}. Top merchant: {list(top_merchant.keys())[0] if top_merchant else 'N/A'}",
                "recommendations": ["Track high-value transactions", "Monitor recurring payments", "Consider budgeting apps"],
                "key_insights": [
                    f"You spent ₹{total_spend:,.2f} across {len(filtered_txns)} transactions",
                    f"Average transaction: ₹{df['amount'].mean():.2f}",
                    f"Most frequent merchant: {list(top_merchant.keys())[0] if top_merchant else 'N/A'}"
                ],
                "total_transactions": len(filtered_txns),
                "ai_engine": "Basic Analysis (LLM not configured)"
            }
        
        # Create tasks for CrewAI analysis
        analysis_task = Task(
            description=f"""
            Analyze the following Google Pay transaction data to answer: "{query}"
            
            Transaction Data: {json.dumps(filtered_txns[:10])}
            Total Transactions: {len(filtered_txns)}
            Timeframe: {timeframe}
            
            Provide detailed financial analysis including spending patterns, top categories, and trends.
            """,
            agent=self.financial_analyst,
            expected_output="Comprehensive financial analysis with specific insights"
        )
        
        recommendations_task = Task(
            description=f"""
            Based on the transaction analysis, provide financial recommendations for: "{query}"
            
            Focus on budget optimization, spending improvements, and savings opportunities.
            """,
            agent=self.financial_advisor,
            expected_output="Actionable financial recommendations"
        )
        
        insights_task = Task(
            description=f"""
            Generate key insights answering: "{query}"
            
            Include 3-5 key findings, alerts, and improvement areas.
            """,
            agent=self.insights_generator,
            expected_output="List of key insights and findings"
        )
        
        # Create and run crew
        try:
            crew = Crew(
                agents=[self.financial_analyst, self.financial_advisor, self.insights_generator],
                tasks=[analysis_task, recommendations_task, insights_task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "summary": f"Analyzed {len(filtered_txns)} transactions for {timeframe} period",
                "analysis": str(analysis_task.output) if hasattr(analysis_task, 'output') else "Analysis completed",
                "recommendations": str(recommendations_task.output) if hasattr(recommendations_task, 'output') else "Recommendations generated",
                "key_insights": str(insights_task.output) if hasattr(insights_task, 'output') else "Insights generated",
                "total_transactions": len(filtered_txns),
                "ai_engine": "CrewAI with Gemini"
            }
            
        except Exception as e:
            return {"error": f"CrewAI analysis failed: {str(e)}"}
    
    def filter_by_timeframe(self, timeframe: str) -> List[Dict]:
        """Filter transactions by timeframe"""
        if timeframe == "all":
            return self.transactions
        
        if not self.transactions:
            return []
        
        # Sort transactions by date (newest first)
        sorted_txns = sorted(self.transactions, key=lambda x: x['date'], reverse=True)
        
        if "month" in timeframe.lower():
            if "three" in timeframe or "3" in timeframe:
                return sorted_txns[:90]  # Last 90 transactions
            else:
                return sorted_txns[:30]  # Last 30 transactions
        elif "week" in timeframe.lower():
            return sorted_txns[:7]  # Last 7 transactions
        elif "year" in timeframe.lower():
            return sorted_txns[:365]  # Last 365 transactions
            
        return sorted_txns[:30]  # Default: last 30 transactions

# Initialize analyzer
analyzer = GPPayAnalyzer()

@app.get("/")
def read_root():
    return {"message": "Google Pay Smart Analyzer with CrewAI", "version": "2.0.0", "ai_engine": "CrewAI"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "ai_enabled": True, "ai_engine": "CrewAI"}

@app.post("/upload")
async def upload_html(file: UploadFile = File(...)):
    """Upload Google Pay HTML file and parse transactions"""
    
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Please upload an HTML file")
    
    try:
        content = await file.read()
        html_content = content.decode('utf-8')
        
        transactions = analyzer.parse_html_content(html_content)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in HTML file")
        
        total_amount = sum(t['amount'] for t in transactions)
        date_range = {
            'start': min(t['date'] for t in transactions),
            'end': max(t['date'] for t in transactions)
        }
        
        return {
            "status": "success",
            "message": f"Parsed {len(transactions)} transactions",
            "summary": {
                "total_transactions": len(transactions),
                "total_amount": total_amount,
                "date_range": date_range
            },
            "transactions": transactions[:5]  # Preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/analyze")
async def analyze_transactions(
    file: UploadFile = File(...),
    query: str = Form(...),
    timeframe: str = Form(default="all")
):
    """Upload HTML file and get CrewAI-powered analysis"""
    
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Please upload an HTML file")
    
    try:
        content = await file.read()
        html_content = content.decode('utf-8')
        
        transactions = analyzer.parse_html_content(html_content)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in HTML file")
        
        # Auto-detect timeframe from query
        if timeframe == "all" and query:
            if "month" in query.lower():
                timeframe = "one month"
            elif "week" in query.lower():
                timeframe = "one week"
            elif "year" in query.lower():
                timeframe = "one year"
        
        # Get CrewAI insights
        insights = analyzer.analyze_with_crewai(query, timeframe)
        
        return {
            "status": "success",
            "query": query,
            "timeframe": timeframe,
            "total_transactions_parsed": len(transactions),
            "insights": insights,
            "ai_engine": "CrewAI"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transactions: {str(e)}")

@app.post("/quick-insights")
async def get_quick_insights(file: UploadFile = File(...)):
    """Upload HTML file and get quick spending insights"""
    
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Please upload an HTML file")
    
    try:
        content = await file.read()
        html_content = content.decode('utf-8')
        
        transactions = analyzer.parse_html_content(html_content)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in HTML file")
        
        df = pd.DataFrame(transactions)
        
        total_spend = df['amount'].sum()
        avg_transaction = df['amount'].mean()
        top_merchant = df['recipient'].value_counts().head(1).to_dict()
        
        return {
            "status": "success",
            "insights": {
                "total_spend": float(total_spend),
                "average_transaction": float(avg_transaction),
                "transaction_count": len(transactions),
                "top_merchant": top_merchant,
                "date_range": {
                    "start": df['date'].min(),
                    "end": df['date'].max()
                }
            },
            "ai_engine": "CrewAI Ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)