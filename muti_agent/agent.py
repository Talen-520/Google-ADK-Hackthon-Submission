from google.adk.agents import Agent,SequentialAgent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from .subAgent.fundamental_analyzer.agent import fundamental_analyzer_agent

from .tools import (
 scrape_news, 
 get_current_time, 
 get_company_profile,
 get_historical_prices, 
 calculate_technical_indicators
)

# news collector agent that will be used to get news data for a given ticker
news_collector = LlmAgent(
    name="news_collector", 
    # You need longer input and output for this agent, tool return long context
    model="gemini-2.5-flash-preview-05-20",
    instruction= """
    You are a hyper-efficient data processing engine specializing in stock market news. Your sole purpose is to fetch, clean, and format news articles for a given stock ticker. You must operate with precision and follow the rules strictly.

    **Core Workflow:**
    1.  Immediately identify the stock ticker symbol from the user's query (e.g., 'AAPL', 'TSLA', 'GOOGL').
    2.  Use the `scrape_news` tool to fetch news for that ticker. The number of articles to fetch will be provided by the `num_url` parameter. If not provided, use the default 10, for deeper research, set it 20.
    3.  For each article returned by the tool, perform the following data cleaning and formatting steps.
    4.  Your final output must *only* be the structured, cleaned news data and nothing else. Do not add any introductory or concluding remarks.

    **Data Cleaning & Formatting Rules:**
    - From the article's content, meticulously remove all non-essential text. This includes, but is not limited to: advertisements, promotional materials, newsletter sign-ups, 'related articles' links, and social media sharing buttons.
    - The goal is to leave only the pure journalistic content of the article.
    - Format each cleaned article precisely into the Markdown structure specified below.

    **Mandatory Output Format:**
    You must format each article using the following Markdown template. Do not deviate from this structure.
    state how many news you processed in the end

    ```markdown
    * **Title:** [The title of the article] \n
    * **Date:** [The date of the article] \n
    * **Content:** \n\n
    [The full, cleaned text content of the article. Paragraphs should be preserved.]
    \n
    **Title:** [The title of the next article] \n
    rest of the article...
    ```
    """,
    tools=[scrape_news],
    output_key="news_data",
    ) # Saves output to state['data']

# data_analyst agent that will be used to analyze news data for a given ticker
news_analyzer_agent = LlmAgent(
    name="finance_news_analyzer_agent", 
    # You need longer input and output for this agent, tool return long context
    model = "gemini-2.5-flash-preview-05-20",
    description=(
        "Agent to analyze news data for certain ticker from Yahoo Finance."
    ),

    instruction="""
    You are a professional and insightful financial news analyst. Your task is to analyze a pre-processed set of news articles provided to you and generate a structured analytical report.

    **Input Source:**
    Your input is a block of cleaned, Markdown-formatted news articles. 
    This data is provided from a previous step and is provided in session state with key {news_data}

    **Core Analytical Tasks:**
    For the entire set of news, perform the following analyses:
    1.  **Sentiment Analysis:** For each individual article, classify its sentiment as **Positive**, **Negative**, or **Neutral** from an investor's perspective.
    2.  **Event Extraction:** For each article, identify and name the key event it describes (e.g., "Product Launch", "Earnings Report", "Executive Change", "Regulatory Scrutiny", "Price Target Update").
    3.  **Relevance Filtering:** If any article is clearly not relevant to the company's business or stock performance, discard it from your analysis.
    
    
    **Mandatory Output Format:**
    analyze all news data and give each news data a title, date, sentiment, and event.
    You must structure your entire output as a single Markdown block. Follow the format in the example precisely, .
    
    **Example:**
  

    Title: Tesla's Gigafactory Expansion Faces New Hurdles
    Date: 2025-06-12
    Sentiment: Negative
    Event: Regulatory Scrutiny
    Key takeaway: Your Professional analysis of each article**

    Title: Analyst Upgrades Tesla to 'Buy' with a $300 Price Target
    Date: ...

    Remind users how much irrelevant content has been filtered out, and provide the filtered information to users upon request
    """,
    output_key="news_analysis_result",
)

news_analysis_pipeline = SequentialAgent(
    name="new_analysis_pipeline",
    description="a pipline to analyze news data for certain ticker from Yahoo Finance. ", 
    sub_agents=[news_collector, news_analyzer_agent])

technical_analyzer = LlmAgent(
    name="technical_analyzer",
    instruction="""
    You are a quantitative chart analyst (Quant). Your job is to interpret stock price movements and technical indicators to identify trends and market sentiment.

    **Core Tasks:**
    1.  Analyze historical price and volume data to identify the primary trend (Uptrend, Downtrend, Sideways).
    2.  Interpret key technical indicators (e.g., SMA, RSI, MACD).

    **Mandatory Output Format:**
    ```markdown
    ### Technical Analysis Summary

    **Primary Trend:** [Uptrend/Downtrend/Sideways]
    **Support Level:** ~$[Price]
    **Resistance Level:** ~$[Price]

    **Indicator Signals:**
    - **RSI (14):** [Value] (Indicates: [Overbought/Oversold/Neutral])
    - **MACD:** [Bullish Crossover/Bearish Crossover/Neutral]
    - **Moving Averages:** [e.g., Price is above the 50-day SMA, indicating a positive short-term trend.]
    ```
    """,
    tools=[get_historical_prices, calculate_technical_indicators],
    output_key="technical_analysis_result"
)

root_agent = LlmAgent(
    name="Stock_Agent",
    # model="gemini-2.5-pro-preview-06-05",
    model="gemini-2.0-flash",

    # global_instruction="""You're an investment assistant. Always respond politely.""",
    instruction=(
        """
        You are a personal stock agent specialized for investor
        If use ask recent news about certain ticker, check you state first, if not, transfer to sub agent news_analysis_pipeline to get result.
        if session contains it's data, use it directly.

        news_analysis_pipeline:
        - news_collector: collect news data for certain ticker from Yahoo Finance.
        - news_analyzer_agent: analyze news data for certain ticker from Yahoo Finance.
        """
    ),
    sub_agents=[
        news_analysis_pipeline,
        #technical_analyzer,
        #fundamental_analyzer_agent,
        ],
    
    tools=[
        get_company_profile,
        #AgentTool(agent=news_analysis_pipeline),
        AgentTool(agent=technical_analyzer),
        AgentTool(agent=fundamental_analyzer_agent),  
        ],
)
