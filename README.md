![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python)

Stock Analysis Multi-Agent

## Prerequisites

- Python 3.11+
- Google API Key
- MacOS system  (windows not tested)
## Installation

clone this repo then install the requirements
```bash
pip install -r requirements.txt
```

replace `.env.example` to `.env` and add your google api key

## Start the demo with google web adk
```bash
adk web
```

try prompt:
```bash
# what happened to nvidia recently?
```


## Inspiration
Navigating the complexities of the financial markets often presents investors with challenges such as information overload, siloed analysis, and the need for timely decision-making. Traditional methods of acquiring and analyzing information can be time-consuming and struggle to integrate diverse market signals. Inspired by the ability of Multi-Agent Systems (MAS) to handle complex tasks and facilitate collaborative division of labor, we envisioned an AI system that could emulate a professional investment analysis team. This system aims to efficiently acquire, analyze, and present stock information through intelligent agent collaboration, thereby empowering users to make more informed investment decisions.

## What it does
This Muti Agent System integrates multiple specialized agents, each responsible for a specific domain of financial analysis:

- **Real-time** News Dynamics: Gathers and analyzes the latest stock-related news, extracting key events and sentiment to help users stay informed about market movements.
- **In-depth Fundamental Research**: Provides fundamental analysis of companies, including financial statements, key financial ratios, and analyst ratings with price targets, assisting users in evaluating a company's financial health and valuation.
- **Professional Technical Chart Interpretation**: Performs technical analysis of stocks, identifying price trends, support/resistance levels, and interpreting technical indicators like RSI and MACD, offering insights into market sentiment and momentum.
Through these core functions, the system aims to provide users with a one-stop stock analysis platform, revealing potential value and risks from various perspectives.

## How I built it
This system using a multi-agent architecture, where each agent is powered by a Large Language Model (LLM) and equipped with specialized tools and instruction sets:

- **ROOT_AGENT**: Acts as the system's orchestrator and router, intelligently dispatching user queries to the most appropriate specialized agent.
- **News Analysis Pipeline (Sequential Agent)**: A sequential agent pipeline comprising two sub-agents:
  - **news_collector**: Responsible for fetching raw news data from Yahoo Finance using the scrape_news tool, followed by initial cleaning and formatting.
  - **finance_news_analyzer_agent**: Receives output from news_collector to perform sentiment analysis, event extraction, and relevance filtering, ultimately generating a structured news analysis report.
- **Fundamental Analyzer (fundamental_analyzer_agent)**: Utilizes tools such as get_financial_statements, get_key_ratios, and get_analyst_ratings to conduct in-depth analysis of company financial data and produce a fundamental summary.
- **Technical Analyzer (technical_analyzer)**: Employs get_historical_prices and calculate_technical_indicators tools to retrieve historical price data and compute technical indicators, then generates a technical analysis report.


## Challenges I Ran Into
During development, we encountered several challenges:

- **Precision of Tool Calling**: Ensuring the root agent accurately understands user intent and selects the correct tool, especially for ambiguous queries or those involving multiple analytical dimensions.
- **News Content Cleaning and Structuring**: Raw news web pages contain a lot of non-textual content and redundant information. Extracting pure text efficiently and accurately with **playwrite**, and presenting it in a standardized format, was a significant challenge.
- **Collaboration and Information Transfer Between Multi-Agents**: Ensuring seamless information flow and between different agents. For instance, the output of news_collector must be correctly received and processed by finance_news_analyzer_agent.
- **Interpretability and Trustworthiness**: As an investment aid, ensuring the transparency and interpretability of AI analysis results, and avoiding misleading users, remains a continuous focus.

## Accomplishments That I'm Proud Of
I'm proud of the following accomplishments:

- **Integrated Multi-dimensional Analysis**: Successfully integrated news, fundamental, and technical analysis into a unified system, providing users with a comprehensive perspective.
- **Efficient Information Processing Pipeline**: Built an automated pipeline from data scraping to analysis, significantly enhancing information processing efficiency.
- **Modular Agent Design**: Each agent has clear responsibilities and well-defined input/output formats, contributing to the system's excellent scalability and maintainability.

## What I Learned
Throughout the development of this system, I learned:

- **The Importance of Multi-Agent Collaboration**: For complex tasks, breaking down the task and assigning it to specialized agents for collaborative completion is more efficient and effective than processing with a single large model.
- **Deep Integration of Tools and LLMs**: The ability of LLMs to integrate with external tools is powerful. Designing effective tool interfaces and LLM calling strategies is crucial.
- **The Criticality of Data Preprocessing**: Clean, structured data is the foundation for high-quality analysis. The news collection and cleaning steps are vital for the accuracy of subsequent analysis.
- **Asynchronous Process**: The system adopts an asynchronous processing model, where agents independently execute tasks and communicate results through asynchronous channels. This approach enables efficient parallelism and resource utilization, especially for tasks like data scraping and analysis, which can be time-consuming.

## What's Next for Stock Agent System
In the future, I will continue to refine this Stock Agent System:

- **Adding More Analytical Dimensions:** Consider integrating macroeconomic analysis, industry analysis, social media sentiment analysis, and other data sources and analytical perspectives.
- **Enhancing Personalized Recommendations**: Provide more personalized stock recommendations and investment strategies based on user investment preferences and risk tolerance.
- **Supporting More Trading Markets**: Expand support to major global stock markets beyond just Yahoo Finance.
- **Introducing Visualization Tools**: Incorporate charts and visual interfaces to display analysis results and trends more intuitively.
- **Real-time Interaction and Proactive Alerts**: Explore implementing more real-time market updates and intelligent alert functions based on user-defined settings.


[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
