import json
import streamlit as st
import time
from phi.agent import Agent
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.model.google import Gemini
from phi.tools.newspaper4k import Newspaper4k
from phi.tools.youtube_tools import YouTubeTools

# Configure page
st.set_page_config(
    page_title="SelectStream CompanyPrep",
    page_icon="🎯",
    layout="wide"
)

# Update custom CSS with better tab styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .title { text-align: center; color: #1976d2; }
    .stProgress > div > div > div > div { background-color: #1976d2; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 8px 16px;
        background-color: #263238;
        border-radius: 4px;
        color: #ffffff;
        opacity: 0.7;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976d2;
        opacity: 1;
    }
    .api-section {
        font-size: 0.9em;
        margin-bottom: 1rem;
    }
    .api-section a {
        font-size: 0.8em;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='title'>🎯 SelectStream CompanyPrep</h1>", unsafe_allow_html=True)
st.markdown("### Your AI-Powered Company Research Assistant")
st.markdown("---")

# Create tabs
tab1, tab2 = st.tabs(["🎯 CompanyPrep Basic", "⭐ CompanyPrep Pro"])

# Common function for progress and status
def show_research_progress(status, progress):
    steps = [
        ("📚 Gathering web information...", 25),
        ("💹 Analyzing financial data...", 50),
        ("📰 Gathering latest news and analysis...", 75),
        ("🎥 Searching video content...", 85),
        ("✍️ Generating comprehensive report... This takes 2-3 Mins", 90)
    ]
    for step_text, step_progress in steps:
        status.text(step_text)
        progress.progress(step_progress)
        time.sleep(1)

# Basic Version Tab
with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        basic_api_key = st.text_input("Gemini API Key 🔑", type="password", key="basic_key")
        st.markdown('<div class="api-section">Need API? <a href="https://aistudio.google.com/" target="_blank">Get here</a></div>', unsafe_allow_html=True)
        basic_company = st.text_input("Company Name 🏢", placeholder="e.g., Google, Microsoft", key="basic_company")

    with col2:
        st.markdown("### Basic Features")
        st.markdown("""
        - 🔍 Web research
        - 📊 Financial analysis
        - 📰 Latest news and trends
        """)

    if st.button("🚀 Research Company", type="primary", key="basic_button"):
        if not basic_api_key or not basic_company:
            st.error("Please provide both API key and company name!")
        else:
            try:
                with st.spinner('🔍 Researching company information...'):
                    progress = st.progress(0)
                    status = st.empty()
                    
                    # Initialize basic agents with existing configuration
                    web_agent = Agent(
                        name="Web Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=basic_api_key),
                        tools=[DuckDuckGo()],
                        instructions=[" This includes the company's specialization, core values, mission statement, recent achievements, Rivals and Competitors organizational structure, customer service approach, work culture, main products/services, key personnel, and growth strategy. Always include the sources."],
                        show_tool_calls=True,
                        markdown=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    finance_agent = Agent(
                        name="Finance Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=basic_api_key),
                        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
                        instructions=["Use tables to display data"],
                        show_tool_calls=True,
                        markdown=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    research_agent = Agent(
                        name="Research Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=basic_api_key),
                        tools=[DuckDuckGo(), Newspaper4k()],
                        description="You are a senior researcher writing an article on a topic.",
                        instructions=[
                            "For a given company, search for the top links in biggest challenges facing the company, its strategic initiatives, and growth patterns. Prioritize reliable and reputable sources .",
                            "Then read each URL and extract the article text, if a URL isn't available, ignore it.",
                            "Analyse and prepare an NYT worthy article based on the information.",
                        ],
                        markdown=True,
                        show_tool_calls=True,
                        add_datetime_to_instructions=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    agent_team = Agent(
                        team=[web_agent, finance_agent, research_agent],
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=basic_api_key),
                        instructions=[
                            "You are a placement support agent designed to gather comprehensive information about a company given only the company's name.",
                            "Your goal is to provide a thorough overview that would be useful for a student preparing for a placement drive.",
                            "Initiate a broad and systematic information gathering process using the available agents.",
                            "Follow this structure to collect information:",
                            "   1. **Web Search Agent:** First, use the web search agent to identify and collect general company information. This includes the company's specialization, core values, mission statement, recent achievements, organizational structure, customer service approach, work culture, main products/services, key personnel, and growth strategy. Always include the sources.",
                            "   2. **Finance Agent:** Then, use the finance agent to gather all relevant financial data. This includes the latest stock price, analyst recommendations, and other key financial metrics. Present this data in a well-formatted table. Do not perform this if no financial data is available.",
                            "   3. **Research Agent:** Concurrently, use the research agent to look for in-depth analysis, articles, and reports. Always include the source links.",
                            "Be as detailed as possible in your report. Use Markdown for formatting. Use tables when presenting data. Include links to the sources when available.",
                            "Make all the outputs as Single article Do not Provide Duplicate Information",
                            
                        ],
                        show_tool_calls=True,
                        markdown=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    show_research_progress(status, progress)
                    
                    # Get and display response
                    response = agent_team.print_response(basic_company)
                    response = agent_team.get_chat_history()
                    
                    progress.empty()
                    status.empty()
                    
                    with st.container():
                        st.success(f"🎉 Research complete for {basic_company}!")
                        response_json = json.loads(response)
                        st.markdown("### 📋 Company Analysis Report")
                        st.markdown(response_json[1]['content'])
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Pro Version Tab
with tab2:
    col3, col4 = st.columns([2, 1])
    with col3:
        pro_api_key = st.text_input("Enter your Gemini API Key 🔑", type="password", key="pro_key")
        st.markdown('<div class="api-section">Need API? <a href="https://aistudio.google.com/" target="_blank">Get here</a></div>', unsafe_allow_html=True)
        pro_company = st.text_input("Enter Company Name 🏢", placeholder="e.g., Google, Microsoft, Amazon", key="pro_company")

    with col4:
        st.markdown("### Pro Features ⭐")
        st.markdown("""
        - 🔍 Enhanced web research
        - 📊 Detailed financial analysis
        - 📰 Comprehensive news coverage
        - 🎥 Video content analysis
        - 📈 Growth trends
        - 🤝 Competitor analysis
        """)

    # Create a container for buttons side by side
    button_col1, button_col2 = st.columns(2)
    
    with button_col1:
        pro_button = st.button("🚀 Research Company (Pro)", type="primary", key="pro_button")
    
    with button_col2:
        stock_button = st.button("📈 Get Live Stock Price", key="stock_button")

    if pro_button:
        if not pro_api_key or not pro_company:
            st.error("Please provide both API key and company name!")
        else:
            try:
                with st.spinner('🔍 Conducting comprehensive research...'):
                    progress = st.progress(0)
                    status = st.empty()
                    
                    # Initialize pro agents with enhanced configuration
                    web_agent = Agent(
                        name="Web Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=pro_api_key),
                        tools=[DuckDuckGo()],
                        instructions=[" This includes the company's specialization, core values, mission statement, recent achievements, Rivals and Competitors organizational structure, customer service approach, work culture, main products/services, key personnel, and growth strategy. Always include the sources."],
                        show_tool_calls=True,
                        markdown=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    finance_agent = Agent(
                        name="Finance Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=pro_api_key),
                        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
                        instructions=["Use tables to display data"],
                        show_tool_calls=True,
                        markdown=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    research_agent = Agent(
                        name="Research Agent",
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=pro_api_key),
                        tools=[DuckDuckGo(), Newspaper4k()],
                        description="You are a senior researcher writing an article on a topic.",
                        instructions=[
                            "For a given company, search for the top links in biggest challenges facing the company, its strategic initiatives, and growth patterns. Prioritize reliable and reputable sources .",
                            "Then read each URL and extract the article text, if a URL isn't available, ignore it.",
                            "Analyse and prepare an NYT worthy article based on the information.",
                        ],
                        markdown=True,
                        show_tool_calls=True,
                        add_datetime_to_instructions=True,
                        debug_mode=True,
                        prevent_hallucinations=True
                    )
                    
                    # Initialize other pro agents...
                    
                    show_research_progress(status, progress)
                    
                    # Get and display response using pro agent team
                    YT_agent = Agent(
    name="YouTube Agent",
    role="A video content researcher specialized in company-related videos on YouTube.",
    tools=[DuckDuckGo(),YouTubeTools()],
    description="You are responsible for finding and summarizing relevant video content about a company on YouTube. This includes company presentations, interviews with key personnel, product demos, and employee testimonials. Use the YouTube search tool to perform the search and to extract the relevant content from the top videos found. Focus on providing a concise and informative summary of each video found and always include the link of the videos.",
    instructions=[
       "Your primary role is to search YouTube for video content relevant to a given company.",
        "Use the provided DuckDuckGo to find videos such as company presentations, CEO interviews, product demos, employee testimonials, or other relevant content.",
        "When a relevant URL found use YoutubeTools, watch and explain the video in detail, focusing on the key topics and information presented.",
        "Provide summaries of each video, highlighting the most important points that could be valuable for a student preparing for a placement drive.",
        "Always provide the direct YouTube link to the videos you summarize.",
        "Focus on videos from the official company channels or those with credible sources.",
        "Write the summaries as an article and mention link at end as sources"
        "Do not search for music videos or other non-relevant content.",
        "Provide a brief summary of the video and the link. Use bullet points for multiple videos.",
    ],
    markdown=True,
    show_tool_calls=True,
    model=Gemini(id="gemini-2.0-flash-exp",api_key="AIzaSyCZ3nRdZcgspprXE3Ivb5BpFjkfFz62goU"),
    add_datetime_to_instructions=True,
    debug_mode=True,
    prevent_hallucinations=True,
)

                    agent_team = Agent(
    team=[web_agent, finance_agent,research_agent ],
    instructions=[
     "You are a placement support agent designed to gather comprehensive information about a company given only the company's name.",
    "Your goal is to provide a thorough and insightful overview that would be extremely useful for a student preparing for a placement drive.",
    "Initiate a broad and systematic information gathering process using the available agents, ensuring that there is no duplication of information.",
    "Follow this structure to collect information, and always ensure no duplicate info is provided:",
    "   1. **Web Search Agent:** First, use the web search agent to identify and collect general company information. This includes the company's specialization, core values, mission statement, recent achievements, organizational structure, customer service approach, work culture, main products/services, key personnel, and growth strategy. Always include the source URLs.",
    "   2. **Finance Agent:** Then, use the finance agent to gather all relevant financial data. This includes the latest stock price, analyst recommendations, and other key financial metrics. Present this data in a well-formatted table. If no financial data is available, do not use this agent.",
    "   3. **Research Agent:** Concurrently, use the research agent to look for in-depth analysis, articles, and reports. Focus on identifying the biggest challenges facing the company, its strategic initiatives, and growth patterns. Always include the source links.",
    "   4. **YouTube Agent:** Finally, use the YouTube agent to search for relevant videos about the company, such as company presentations, CEO interviews, product demos, and employee testimonials. Summarize every relevant video and always include the sources.",
    "Compile all the information gathered from all the agents into a single, detailed report, ensuring that there is no duplication of data. Structure it without differentiating agents",
     "Be as detailed as possible in your report. Use Markdown for formatting. Use tables when presenting data. Include links to the sources when available.",
      "Make all the outputs as Single article Do not Provide Duplicate Information. Ensure all sections are present even if there is no information available for some of them. If no information available mark as NA.",
        ],
    model=Gemini(id="gemini-2.0-flash-exp",api_key="AIzaSyCZ3nRdZcgspprXE3Ivb5BpFjkfFz62goU"),
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
    prevent_hallucinations=True
    
)



                    
                    response = agent_team.print_response(pro_company)
                    response = agent_team.get_chat_history()
                    
                    progress.empty()
                    status.empty()
                    
                    with st.container():
                        st.success(f"🎉 Pro Research complete for {pro_company}!")
                        response_json = json.loads(response)
                        st.markdown("### 📋 Advanced Company Analysis Report")
                        st.markdown(response_json[1]['content'])
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    if stock_button:
        if not pro_api_key or not pro_company:
            st.error("Please provide both API key and company name!")
        else:
            try:
                with st.spinner('🔍 Fetching live stock price...'):
                    Stock_agent = Agent(
                        tools=[DuckDuckGo(), YFinanceTools(stock_price=True)],
                        debug_mode=True,
                        show_tool_calls=True,
                        model=Gemini(id="gemini-2.0-flash-exp", api_key=pro_api_key),
                        description="You need to get the live stock price of the provided company.",
                        instructions=[
                            "Find the stock symbol of the company using DuckDuckGo search.",
                            "Use YFinanceTools to get the live stock price of the company."
                        ]
                    )
                    
                    response = Stock_agent.print_response(pro_company)
                    response = Stock_agent.get_chat_history()
                    
                    with st.container():
                        st.success(f"🎉 Live stock price fetched for {pro_company}!")
                        response_json = json.loads(response)
                        st.markdown("### 📋 Live Stock Price")
                        st.markdown(response_json[1]['content'])
            except Exception as e:
                st.error(f"An error occurred while fetching the stock price: {str(e)}")

# Footer
st.markdown("---")
st.markdown("### 💡 Pro Tips")
col5, col6 = st.columns(2)
with col5:
    st.info("Use company's official name for best results!")
with col6:
    st.info("Pro version includes video content and deeper analysis!")

