from google.adk.agents import SequentialAgent, LlmAgent
from .tools import scrape_news

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
        "Agent to analyze recent news data for certain ticker from Yahoo Finance."
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