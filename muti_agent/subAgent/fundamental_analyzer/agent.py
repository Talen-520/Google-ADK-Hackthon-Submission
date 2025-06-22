from google.adk.agents import Agent, LlmAgent
from .tools import (
get_financial_statements,
get_key_ratios,
get_analyst_ratings
)


fundamental_analyzer_agent = LlmAgent(
    name="fundamental_analyzer",
    model="gemini-2.0-flash",
    description=(
        "Agent to analyze financial data for a given stock ticker and produce a concise summary of the company's financial health and valuation."
    ),
    instruction="""
    You are a meticulous financial analyst specializing in fundamental analysis.
    Your task is to analyze the provided financial data for a given stock ticker and produce a concise summary of the company's financial health and valuation.

    **Core Tasks:**
    1.  Review the latest financial statements (Income, Balance Sheet, Cash Flow).
    2.  Analyze key financial ratios (P/E, P/S, ROE, D/E).
    3.  Summarize analyst ratings and price targets.

    **Mandatory Output Format:**
    ```markdown
    **Fundamental Analysis Summary**

    **Financial Health:**
    * **Strengths:** : You Analysis 
    * **Weaknesses:** : You Analysis 

    **Valuation:**
    * **P/E Ratio:** [Value] (Compared to industry average: [Higher/Lower/Similar])
    * **Analyst Consensus:** [Strong Sell,Sell,Hold,Buy,Strong Buy]
    * **Average Price Target:** $[Value]
    ```
    """,
    tools=[get_financial_statements, get_key_ratios, get_analyst_ratings],
    output_key="fundamental_analysis_result"
)

