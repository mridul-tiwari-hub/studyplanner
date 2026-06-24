import streamlit as st
import os
import json
from dotenv import load_dotenv

# Set page config first
st.set_page_config(
    page_title="Autonomous Study Planner | Capstone",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load helper modules
import state_manager
import agents

# Load env vars
load_dotenv(override=True)

# Inject premium custom CSS styling (slate theme, glassmorphic cards, glowing borders)
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    
    <style>
        /* Base typography */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* App Title Header Banner */
        .header-banner {
            background: linear-gradient(135deg, #4A154B 0%, #611f69 50%, #2e0854 100%);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 25px;
            color: white;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .header-banner h1 {
            font-size: 2.8rem;
            font-weight: 800;
            margin: 0;
            color: #FFFFFF;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .header-banner p {
            font-size: 1.1rem;
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        
        /* Premium Card Styling */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom timeline style */
        .timeline-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            background: rgba(0, 0, 0, 0.1);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .timeline-step {
            flex: 1;
            text-align: center;
            padding: 10px;
            border-radius: 8px;
            margin: 0 5px;
            transition: all 0.3s ease;
        }
        .step-active {
            background: rgba(138, 43, 226, 0.2);
            border: 1px solid rgba(138, 43, 226, 0.6);
            box-shadow: 0 0 10px rgba(138, 43, 226, 0.3);
        }
        .step-completed {
            background: rgba(46, 204, 113, 0.15);
            border: 1px solid rgba(46, 204, 113, 0.5);
        }
        .step-locked {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            opacity: 0.5;
        }
        
        /* Agent Thought bubble */
        .thought-bubble {
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 12px;
            border-left: 5px solid;
            font-size: 0.95rem;
            line-height: 1.4;
        }
        .bubble-planner {
            background: rgba(138, 43, 226, 0.08);
            border-left-color: #8A2BE2;
            border: 1px solid rgba(138, 43, 226, 0.15);
            border-left-width: 5px;
        }
        .bubble-teacher {
            background: rgba(0, 191, 255, 0.08);
            border-left-color: #00BFFF;
            border: 1px solid rgba(0, 191, 255, 0.15);
            border-left-width: 5px;
        }
        .bubble-evaluator {
            background: rgba(255, 215, 0, 0.08);
            border-left-color: #FFD700;
            border: 1px solid rgba(255, 215, 0, 0.15);
            border-left-width: 5px;
        }
        .bubble-guardrail {
            background: rgba(220, 53, 69, 0.08);
            border-left-color: #DC3545;
            border: 1px solid rgba(220, 53, 69, 0.15);
            border-left-width: 5px;
        }
        
        /* Log Agent Header */
        .log-header {
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .time-badge {
            font-size: 0.75rem;
            opacity: 0.6;
        }
    </style>
""", unsafe_allow_html=True)

# App Title Header
st.markdown("""
    <div class="header-banner">
        <h1>🎓 Autonomous Study Planner</h1>
        <p>A Closed-Loop Multi-Agent Swarm for Adaptive Learning — Built with Google ADK (Concierge Track)</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar configurations
st.sidebar.image("https://img.icons8.com/clouds/200/brain.png", width=100)
st.sidebar.markdown("### Swarm Controls")

# API Key Configuration - supports single or separate keys per agent group
st.sidebar.markdown("#### API Configuration")
load_dotenv(override=True)
env_key = os.environ.get("GEMINI_API_KEY", "")
# Choose mode
key_mode = st.sidebar.radio("API Key Mode", options=["Single Key", "Separate Keys"], index=0)

if key_mode == "Single Key":
    # Single key input (overrides all agents)
    custom_api_key = st.sidebar.text_input(
        "Enter Gemini API Key (Overrides .env for all agents):",
        value=st.session_state.get("custom_api_key", ""),
        type="password",
        help="Paste your Gemini API key here. It will override any keys set in the .env file for every agent."
    )
    if custom_api_key.strip():
        if st.session_state.get("custom_api_key", "") != custom_api_key.strip():
            # Update session and env var
            st.session_state["custom_api_key"] = custom_api_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY"] = custom_api_key.strip()
            # Also set role-specific overrides for consistency
            os.environ["OVERRIDE_GEMINI_API_KEY_PLANNER"] = custom_api_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_TEACHER"] = custom_api_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_GUARDRAIL"] = custom_api_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_EVALUATOR"] = custom_api_key.strip()
            # Clear session caches
            for key in ["current_lesson", "current_quiz", "active_day_ref", "api_error_warning"]:
                if key in st.session_state:
                    del st.session_state[key]
            # Clear persisted generated content
            try:
                state_data = state_manager.load_state()
                state_data["generated_lessons"] = {}
                state_data["generated_quizzes"] = {}
                state_manager.save_state(state_data)
            except Exception:
                pass
            # Invalidate client caches
            try:
                import agents as _agents_mod
                _agents_mod.client = None
            except Exception:
                pass
    else:
        # Remove custom key if field cleared
        if "custom_api_key" in st.session_state:
            del st.session_state["custom_api_key"]
            for env_var in ["OVERRIDE_GEMINI_API_KEY", "OVERRIDE_GEMINI_API_KEY_PLANNER", "OVERRIDE_GEMINI_API_KEY_TEACHER", "OVERRIDE_GEMINI_API_KEY_GUARDRAIL", "OVERRIDE_GEMINI_API_KEY_EVALUATOR"]:
                os.environ[env_var] = ""
            # Clear caches as above
            for key in ["current_lesson", "current_quiz", "active_day_ref", "api_error_warning"]:
                if key in st.session_state:
                    del st.session_state[key]
            try:
                state_data = state_manager.load_state()
                state_data["generated_lessons"] = {}
                state_data["generated_quizzes"] = {}
                state_manager.save_state(state_data)
            except Exception:
                pass
            try:
                import agents as _agents_mod
                _agents_mod.client = None
            except Exception:
                pass
else:  # Separate Keys mode
    core_key = st.sidebar.text_input(
        "Enter Core Agents API Key (Planner & Guardrail)",
        value=st.session_state.get("core_api_key", ""),
        type="password",
        help="Key used by Planner and Guardrail agents."
    )
    content_key = st.sidebar.text_input(
        "Enter Content Agents API Key (Teacher & Evaluator)",
        value=st.session_state.get("content_api_key", ""),
        type="password",
        help="Key used by Teacher and Evaluator agents."
    )
    # Handle Core key changes
    if core_key.strip():
        if st.session_state.get("core_api_key", "") != core_key.strip():
            st.session_state["core_api_key"] = core_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_PLANNER"] = core_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_GUARDRAIL"] = core_key.strip()
    else:
        if "core_api_key" in st.session_state:
            del st.session_state["core_api_key"]
        for env_var in ["OVERRIDE_GEMINI_API_KEY_PLANNER", "OVERRIDE_GEMINI_API_KEY_GUARDRAIL"]:
            os.environ[env_var] = ""
    # Handle Content key changes
    if content_key.strip():
        if st.session_state.get("content_api_key", "") != content_key.strip():
            st.session_state["content_api_key"] = content_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_TEACHER"] = content_key.strip()
            os.environ["OVERRIDE_GEMINI_API_KEY_EVALUATOR"] = content_key.strip()
    else:
        if "content_api_key" in st.session_state:
            del st.session_state["content_api_key"]
        for env_var in ["OVERRIDE_GEMINI_API_KEY_TEACHER", "OVERRIDE_GEMINI_API_KEY_EVALUATOR"]:
            os.environ[env_var] = ""
    # When any key changes, clear caches and persisted generated data
    if (core_key.strip() and st.session_state.get("core_api_key", "") == core_key.strip()) or (content_key.strip() and st.session_state.get("content_api_key", "") == content_key.strip()):
        # Clear session caches
        for key in ["current_lesson", "current_quiz", "active_day_ref", "api_error_warning"]:
            if key in st.session_state:
                del st.session_state[key]
        # Clear persisted caches
        try:
            state_data = state_manager.load_state()
            state_data["generated_lessons"] = {}
            state_data["generated_quizzes"] = {}
            state_manager.save_state(state_data)
        except Exception:
            pass
        # Invalidate client caches
        try:
            import agents as _agents_mod
            _agents_mod.client = None
        except Exception:
            pass
# Apply button for both modes
if st.sidebar.button("Apply Gemini Key(s)"):
    # Invalidate cached client and clear session caches (covers both modes)
    try:
        import agents as _agents_mod
        _agents_mod.client = None
    except Exception:
        pass
    for key in ["current_lesson", "current_quiz", "active_day_ref", "api_error_warning"]:
        if key in st.session_state:
            del st.session_state[key]
    try:
        state_data = state_manager.load_state()
        state_data["generated_lessons"] = {}
        state_data["generated_quizzes"] = {}
        state_manager.save_state(state_data)
    except Exception:
        pass
    st.sidebar.success("Gemini key(s) applied. All agents will use the new configuration.")
    st.rerun()

# Sidebar selector for Thought Portal logs
selected_agents = st.sidebar.multiselect(
    "Show logs from agents",
    ["System", "Planner Agent", "Teacher Agent", "Evaluator Agent", "Guardrail Agent"],
    default=["Teacher Agent", "Evaluator Agent"]
)

# Determine overall active key status for UI feedback
active_key = (
    os.environ.get("OVERRIDE_GEMINI_API_KEY")
    or os.environ.get("OVERRIDE_GEMINI_API_KEY_PLANNER")
    or os.environ.get("OVERRIDE_GEMINI_API_KEY_TEACHER")
    or env_key
)
if not active_key or active_key == "YOUR_GEMINI_API_KEY_HERE":
    st.sidebar.error("❌ GEMINI_API_KEY is not configured.")
    st.sidebar.markdown("Please configure a `.env` file or enter your key(s) above.")
else:
    st.sidebar.success("🔑 Gemini API Key(s) active.")

# Load state
state = state_manager.load_state()

# Reset button in Sidebar
if st.sidebar.button("🧹 Reset System State & History"):
    state = state_manager.reset_state()
    if "current_lesson" in st.session_state:
        del st.session_state["current_lesson"]
    if "current_quiz" in st.session_state:
        del st.session_state["current_quiz"]
    if "selected_answer" in st.session_state:
        del st.session_state["selected_answer"]
    if "api_error_warning" in st.session_state:
        del st.session_state["api_error_warning"]
    st.success("State reset successfully!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Capstone Track
**Concierge Agents**
* **Goal**: Closed-loop educational companion.
* **Technological primitives**:
  * ADK-style modular agents
  * Adaptive state updates
  * Safety guardrail validations
""")

# Split Screen Columns
col1, col2 = st.columns([3, 2])

# Left Column: User Study View
with col1:
    st.markdown("### 📖 Study Panel")
    
    # Display API warning banner if any API errors were encountered
    if st.session_state.get("api_error_warning"):
        st.warning(st.session_state["api_error_warning"])
    
    # 1. Start Phase: Set learning goal
    if not state["goal"]:
        st.markdown("""
            Welcome! Enter a broad learning goal below. The **Planner Agent** will structure a custom 
            3-day syllabus, the **Teacher Agent** will instruct you daily, and the **Evaluator Agent** 
            will assess your progress.
        """)
        
        goal_input = st.text_input(
            "What learning goal do you want to master?",
            placeholder="e.g. Learn Python Loops, Backend Architecture, Linear Regression...",
            key="goal_input"
        )
        
        if st.button("🚀 Begin My Learning Journey"):
            if not goal_input.strip():
                st.error("Please enter a valid learning goal.")
            else:
                with st.spinner("Swarm is collaborating... Generating custom syllabus."):
                    try:
                        # Planner Agent structures 3-day syllabus
                        syllabus = agents.run_planner_agent(goal_input.strip())
                        
                        # Initialize state
                        state["goal"] = goal_input.strip()
                        state["syllabus"] = syllabus
                        state["current_day"] = 1
                        state["quiz_history"] = []
                        
                        state_manager.save_state(state)
                        state_manager.log_agent_thought(
                            "System", 
                            f"Journey initiated for goal: '{goal_input.strip()}'"
                        )
                        st.success("Syllabus successfully generated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error starting syllabus generation: {e}")
                        
    # 2. Main Study Phase
    else:
        st.markdown(f"**Goal:** `{state['goal']}`")
        
        # Display syllabus progress timeline
        st.markdown("#### Syllabus Timeline")
        timeline_html = '<div class="timeline-container">'
        
        for item in state["syllabus"]:
            day_num = item["day"]
            topic = item["topic"]
            status = item["status"]
            
            # Determine class
            if status == "active" and day_num == state["current_day"]:
                step_class = "timeline-step step-active"
                icon = "🔥"
            elif status == "completed" or day_num < state["current_day"]:
                step_class = "timeline-step step-completed"
                icon = "✅"
            else:
                step_class = "timeline-step step-locked"
                icon = "🔒"
                
            timeline_html += f'<div class="{step_class}"><strong>Day {day_num}</strong><br><span style="font-size: 0.85rem;">{icon} {topic}</span></div>'
        timeline_html += "</div>"
        st.markdown(timeline_html, unsafe_allow_html=True)
        
        # Identify current day module
        active_module = None
        for item in state["syllabus"]:
            if item["day"] == state["current_day"]:
                active_module = item
                break
                
        # If no active module (completed syllabus)
        if not active_module:
            st.markdown("""
                <div class="glass-card" style="text-align: center; border-color: #2ecc71;">
                    <h2 style="color: #2ecc71;">🎉 Course Completed!</h2>
                    <p>Congratulations, you have finished all topics in your syllabus.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("### Quiz Score Summary")
            for record in state["quiz_history"]:
                outcome = "✅ Passed" if record["correct"] else "❌ Flagged for Review"
                st.markdown(f"- **Day {record['day']}**: {record['topic']} | Score: **{outcome}**")
                
            if st.button("🔄 Start a New Syllabus"):
                state = state_manager.reset_state()
                if "current_lesson" in st.session_state:
                    del st.session_state["current_lesson"]
                if "current_quiz" in st.session_state:
                    del st.session_state["current_quiz"]
                if "selected_answer" in st.session_state:
                    del st.session_state["selected_answer"]
                st.rerun()
        
        # Display current day study content
        else:
            st.markdown(f"### 📍 Current Topic: Day {active_module['day']} - {active_module['topic']}")
            st.caption(active_module["description"])
            
            # Fetch or generate lesson draft
            if "current_lesson" not in st.session_state or st.session_state.get("active_day_ref") != state["current_day"]:
                active_topic = active_module["topic"]
                
                # Check persistent cache first
                if "generated_lessons" not in state:
                    state["generated_lessons"] = {}
                if "generated_quizzes" not in state:
                    state["generated_quizzes"] = {}
                    
                lesson_cached = state["generated_lessons"].get(active_topic)
                quiz_cached = state["generated_quizzes"].get(active_topic)
                
                if not lesson_cached or not quiz_cached:
                    # If either is missing, we need to generate/regenerate them
                    with st.spinner("Teacher Agent is writing the lesson..."):
                        if not lesson_cached:
                            lesson = agents.run_teacher_agent(active_topic, state["goal"])
                            state["generated_lessons"][active_topic] = lesson
                            state_manager.save_state(state)
                        else:
                            lesson = lesson_cached
                            
                    with st.spinner("Evaluator Agent is drafting the quiz question..."):
                        if not quiz_cached:
                            # Pause briefly to prevent hitting concurrent free-tier rate limits
                            import time
                            time.sleep(1)
                            quiz = agents.run_evaluator_agent(lesson)
                            state["generated_quizzes"][active_topic] = quiz
                            state_manager.save_state(state)
                        else:
                            quiz = quiz_cached
                else:
                    lesson = lesson_cached
                    quiz = quiz_cached
                    
                st.session_state["current_lesson"] = lesson
                st.session_state["current_quiz"] = quiz
                st.session_state["active_day_ref"] = state["current_day"]
                        
            lesson_content = st.session_state["current_lesson"]
            quiz_content = st.session_state["current_quiz"]
            
            # Render Lesson Card
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown(lesson_content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Render Quiz Card
            st.markdown("### 📝 Knowledge Check")
            st.markdown('<div class="glass-card" style="border-color: rgba(255, 215, 0, 0.3);">', unsafe_allow_html=True)
            st.write(quiz_content["question"])
            
            # Options
            options = quiz_content["options"]
            selected_option = st.radio("Choose the correct option:", options, key="quiz_radio")
            
            if st.button("Submit Answer"):
                # Evaluate correctness
                # Option format: "A) Option text..." or similar. Extract prefix character.
                user_key = selected_option[0].upper()
                correct_key = quiz_content["correct_option"].upper()
                
                is_correct = (user_key == correct_key)
                
                # Update history
                state["quiz_history"].append({
                    "day": state["current_day"],
                    "topic": active_module["topic"],
                    "question": quiz_content["question"],
                    "selected": selected_option,
                    "correct": is_correct
                })
                
                # Handle correct path
                if is_correct:
                    state_manager.log_agent_thought(
                        "Evaluator Agent", 
                        f"Student answered CORRECTLY ({user_key}) to quiz on Day {state['current_day']}."
                    )
                    st.success("🎉 Correct Answer! Great job mastering this concept.")
                    
                    # Mark day as completed and unlock next
                    state_manager.update_day_status(state["current_day"], "completed")
                    next_day = state["current_day"] + 1
                    
                    # If next day exists, set to active
                    for d in state["syllabus"]:
                        if d["day"] == next_day:
                            d["status"] = "active"
                            
                    state["current_day"] = next_day
                    
                    # Clear session state keys
                    if "current_lesson" in st.session_state:
                        del st.session_state["current_lesson"]
                    if "current_quiz" in st.session_state:
                        del st.session_state["current_quiz"]
                        
                    state_manager.save_state(state)
                    st.button("Continue to Next Day ➡️")
                    
                # Handle incorrect path (CLOSED-LOOP TRIGGER)
                else:
                    state_manager.log_agent_thought(
                        "Evaluator Agent", 
                        f"Student answered INCORRECTLY ({user_key}). Correct key was {correct_key}. "
                        "Triggering syllabus re-plan request!"
                    )
                    st.error("❌ Incorrect Answer. The Evaluator has requested a syllabus re-plan to cover this topic.")
                    
                    # Planner Agent replans syllabus starting from current day
                    with st.spinner("Planner Agent is restructuring the syllabus..."):
                        updated_syllabus = agents.run_planner_agent(
                            state["goal"],
                            current_syllabus=state["syllabus"],
                            quiz_history=state["quiz_history"],
                            replan_day=state["current_day"]
                        )
                        
                        # Save updated syllabus
                        state["syllabus"] = updated_syllabus
                        # Increment current_day to the newly created Review day
                        state["current_day"] = state["current_day"] + 1
                        
                        # Clear session state keys
                        if "current_lesson" in st.session_state:
                            del st.session_state["current_lesson"]
                        if "current_quiz" in st.session_state:
                            del st.session_state["current_quiz"]
                            
                        state_manager.save_state(state)
                        st.button("Proceed to Review Session 🔄")
            
            st.markdown('</div>', unsafe_allow_html=True)


# Right Column: Agent Thoughts & Log Viewer
with col2:
    st.markdown("### 💬 Agent Thought Portal")
    st.markdown("Live interaction log showing how the agents talk to each other to manage your learning path.")
    
    # Scrollable Log Container
    log_container = st.container(height=520)
    
    with log_container:
        if not state["agent_logs"]:
            # Ensure selected_agents exists to avoid NameError
            selected_agents = globals().get('selected_agents', [])
            st.markdown("*No logs recorded yet. Initiate your learning goal to start.*")
        else:
            for log in state["agent_logs"]:
                if log["agent"] not in selected_agents:
                    continue
                agent = log["agent"]
                msg = log["message"]
                time = log["timestamp"]

                # Class selection based on agent
                if agent == "Planner Agent":
                    bubble_class = "bubble-planner"
                    icon = "🧠"
                elif agent == "Teacher Agent":
                    bubble_class = "bubble-teacher"
                    icon = "🏫"
                elif agent == "Evaluator Agent":
                    bubble_class = "bubble-evaluator"
                    icon = "📝"
                elif agent == "Guardrail Agent":
                    bubble_class = "bubble-guardrail"
                    icon = "🛡️"
                else:
                    bubble_class = "glass-card"
                    icon = "⚙️"

                st.markdown(f"""
                    <div class="thought-bubble {bubble_class}">
                        <div class="log-header">
                            <span>{icon} {agent}</span>
                            <span class="time-badge">{time}</span>
                        </div>
                        <div>{msg.replace('\\n', '<br>')}</div>
                    </div>
                """, unsafe_allow_html=True)
