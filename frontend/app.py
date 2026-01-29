import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI SQL Agent | Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with animations and modern design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header with gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 1s ease-in-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Animated sub-header */
    .sub-header {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* SQL Query Box with glow effect */
    .sql-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .sql-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Agent log cards with pulse animation */
    .agent-log {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #10b981;
        transition: all 0.3s ease;
        animation: slideInLeft 0.5s ease-in-out;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .agent-log:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    /* Error box with shake animation */
    .error-box {
        background: linear-gradient(135deg, #fee 0%, #fdd 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #ef4444;
        margin: 1.5rem 0;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Success box */
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #10b981;
        margin: 1.5rem 0;
        animation: fadeIn 0.5s ease-in-out;
    }
    
    /* Stat cards with hover effect */
    .stat-card {
        background: linear-gradient(135deg, #fff 0%, #f8fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #64748b;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    
    /* Chat message styling */
    .stChatMessage {
        animation: fadeIn 0.5s ease-in-out;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
        animation: loadingDots 1.5s infinite;
    }
    
    @keyframes loadingDots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60%, 100% { content: '...'; }
    }
    
    /* Pulse animation for status indicators */
    .status-pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #10b981;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
        }
        50% {
            opacity: 0.5;
            transform: scale(1.1);
        }
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Code block styling */
    code {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #10b981;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'total_tables' not in st.session_state:
    st.session_state.total_tables = 0

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.session_state.total_tables = data.get('total_tables', 0)
            return True
        return False
    except:
        return False

def send_query(question: str):
    """Send query to backend API"""
    try:
        payload = {
            "question": question,
            "conversation_history": st.session_state.conversation_history
        }
        response = requests.post(
            f"{BACKEND_URL}/query",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def get_schema_info():
    """Get database schema information"""
    try:
        response = requests.get(f"{BACKEND_URL}/schema", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def display_message(role: str, content: str, sql_query=None, results=None, agent_logs=None):
    """Display a chat message with optional SQL and results"""
    with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🤖"):
        st.markdown(content)
        
        if sql_query:
            with st.expander("🔍 View Generated SQL Query", expanded=False):
                st.code(sql_query, language="sql")
        
        if results and len(results) > 0:
            with st.expander(f"📊 Query Results ({len(results)} rows)", expanded=False):
                st.json(results[:20])
        
        if agent_logs:
            with st.expander("🤖 Multi-Agent Execution Logs", expanded=False):
                for i, log in enumerate(agent_logs, 1):
                    status_emoji = "✅" if log['status'] == "Completed" else "⚠️" if log['status'] == "Error" else "⏳"
                    
                    st.markdown(f"""
                    <div class="agent-log">
                        <strong>{status_emoji} Agent {i}: {log['agent']}</strong><br>
                        <small>Status: {log['status']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'output' in log:
                        st.caption(log['output'])

# Header with animation
st.markdown('<div class="main-header">🤖 Multi-Agent SQL Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions in natural language • AI converts to SQL • Get instant insights</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ System Dashboard")
    
    # System status with pulse animation
    backend_status = check_backend_health()
    
    if backend_status:
        st.markdown("""
        <div class="success-box">
            <span class="status-pulse"></span>
            <strong> Backend Online</strong><br>
            <small>All systems operational</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-box">
            <strong>❌ Backend Offline</strong><br>
            <small>Please start the backend server</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Statistics cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state.total_tables}</div>
            <div class="stat-label">Tables</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{st.session_state.query_count}</div>
            <div class="stat-label">Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Database schema
    st.markdown("### 📚 Database Schema")
    
    if st.button("🔄 Load Schema", use_container_width=True, key="load_schema_btn"):
        with st.spinner("Loading schema..."):
            schema_info = get_schema_info()
            if schema_info:
                st.session_state.schema_info = schema_info
                st.success("✅ Schema loaded!")
                st.rerun()  # Refresh to show the data
            else:
                st.error("Failed to load schema")
    
    if 'schema_info' in st.session_state:
        schema = st.session_state.schema_info
        st.metric("Total Tables", len(schema['tables']))
        
        with st.expander("📋 View All Tables"):
            for i, table in enumerate(schema['tables'], 1):
                st.markdown(f"**{i}.** `{table}`")
    
    st.divider()
    
    # Sample questions with emojis
    st.markdown("### 💡 Try These Questions")
    
    sample_questions = [
        ("📊", "How many customers do we have?"),
        ("🏆", "Show top 5 best-selling products"),
        ("🎨", "Which categories exist?"),
        ("💰", "What is total revenue?"),
        ("👥", "List all employees"),
        ("🌍", "Show orders by country"),
        ("📈", "Product inventory status")
    ]
    
    for emoji, question in sample_questions:
        if st.button(f"{emoji} {question}", key=f"sample_{hash(question)}", use_container_width=True):
            st.session_state.pending_question = question
            st.rerun()  # Force immediate rerun
    
    st.divider()
    
    # Clear history button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary", key="clear_history_btn"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.session_state.query_count = 0
        st.success("✅ Chat cleared!")
        time.sleep(0.5)
        st.rerun()
    
    st.divider()
    
    # How it works section
    st.markdown("### 🔬 Multi-Agent System")
    
    agents = [
        ("🔍", "Schema Analyzer", "Identifies relevant tables"),
        ("💻", "SQL Generator", "Converts to SQL query"),
        ("⚡", "Query Executor", "Runs query safely"),
        ("📝", "Response Formatter", "Natural language output")
    ]
    
    for emoji, name, desc in agents:
        st.markdown(f"""
        <div style="margin: 0.5rem 0;">
            {emoji} <strong>{name}</strong><br>
            <small style="color: #64748b;">{desc}</small>
        </div>
        """, unsafe_allow_html=True)

# Main chat area
st.divider()

# Display chat history with animations
for message in st.session_state.messages:
    display_message(
        message['role'],
        message['content'],
        message.get('sql_query'),
        message.get('results'),
        message.get('agent_logs')
    )

# Handle pending question from sample buttons
prompt_to_process = None

if 'pending_question' in st.session_state:
    prompt_to_process = st.session_state.pending_question
    del st.session_state.pending_question
    
# Chat input with placeholder
user_input = st.chat_input("💬 Ask me anything about the database...")

if user_input:
    prompt_to_process = user_input

# Process the prompt
if prompt_to_process:
    
    # Check backend
    if not check_backend_health():
        st.error("❌ Backend is not running! Please start the backend server first.")
        st.code("cd text-to-sql-agent\npython run_backend.py", language="bash")
        st.stop()
    
    # Increment query count
    st.session_state.query_count += 1
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt_to_process
    })
    
    # Display user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt_to_process)
    
    # Get response from backend
    with st.chat_message("assistant", avatar="🤖"):
        
        # Show thinking animation
        with st.status("🧠 AI Agents are thinking...", expanded=True) as status:
            st.write("🔍 Agent 1: Analyzing database schema...")
            time.sleep(0.5)
            st.write("💻 Agent 2: Generating SQL query...")
            time.sleep(0.5)
            st.write("⚡ Agent 3: Executing query...")
            time.sleep(0.5)
            st.write("📝 Agent 4: Formatting response...")
            
            response_data, error = send_query(prompt_to_process)
            
            if error:
                status.update(label="❌ Error occurred", state="error")
            else:
                status.update(label="✅ Query completed successfully!", state="complete")
        
        # Display results OUTSIDE the status context
        if error:
            st.error(f"Error: {error}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {error}"
            })
        else:
            # Display response
            answer = response_data.get('answer', 'No answer provided')
            sql_query = response_data.get('sql_query')
            results = response_data.get('results')
            agent_logs = response_data.get('agent_logs', [])
            
            st.markdown(answer)
            
            # Show SQL query in styled box
            if sql_query:
                st.markdown('<div class="sql-box">', unsafe_allow_html=True)
                st.markdown("**🔍 Generated SQL Query:**")
                st.code(sql_query, language="sql")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Show results
            if results and len(results) > 0:
                with st.expander(f"📊 View Query Results ({len(results)} rows)", expanded=True):
                    st.dataframe(results, use_container_width=True)
            
            # Show agent logs
            if agent_logs:
                with st.expander("🤖 Multi-Agent Execution Timeline", expanded=False):
                    for i, log in enumerate(agent_logs, 1):
                        status_emoji = "✅" if log['status'] == "Completed" else "⚠️" if log['status'] == "Error" else "⏳"
                        
                        st.markdown(f"""
                        <div class="agent-log">
                            <strong>{status_emoji} Agent {i}: {log['agent']}</strong><br>
                            <small>Status: {log['status']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'output' in log:
                            st.caption(log['output'])
            
            # Add to message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sql_query": sql_query,
                "results": results,
                "agent_logs": agent_logs
            })
            
            # Update conversation history
            st.session_state.conversation_history.append({
                "question": prompt_to_process,
                "answer": answer
            })

# Footer with gradient
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;">
        Powered by <strong>Groq AI</strong> • Built with <strong>FastAPI</strong> & <strong>Streamlit</strong>
    </div>
    <div style="font-size: 0.8rem; color: #94a3b8;">
        🔒 Secure • ⚡ Fast • 🎯 Accurate
    </div>
</div>
""", unsafe_allow_html=True)