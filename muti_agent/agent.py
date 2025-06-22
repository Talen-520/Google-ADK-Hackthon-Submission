from google.adk.agents import Agent,SequentialAgent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from .subAgent.fundamental_analyzer.agent import fundamental_analyzer_agent
from .subAgent.technical_analyzer.agent import technical_analyzer
from .subAgent.news_analysis_pipeline.agent import news_analysis_pipeline
from .prompt import ROOT_AGENT_PROMPT
from .tools import (
 scrape_news, 
 get_current_time, 
)

root_agent = LlmAgent(
    name="Stock_Agent",
    model="gemini-2.5-pro-preview-06-05",
    # global_instruction="""You're an investment assistant. Always respond politely.""",
    instruction=ROOT_AGENT_PROMPT,
    sub_agents=[
        news_analysis_pipeline,
        ],
    
    tools=[
        AgentTool(agent=technical_analyzer),
        AgentTool(agent=fundamental_analyzer_agent),  
        ],
)
