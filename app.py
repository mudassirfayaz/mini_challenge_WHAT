import streamlit as st
import os
import asyncio
from datetime import date
from main import FamilyConnectionOrchestrator

st.set_page_config(
    page_title="Family Connection AI Dashboard",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body {
    background-color: #f7f4ef;
}
.st-emotion-cache-1v0mbdj, .st-emotion-cache-1v0mbdj:before {
    background: linear-gradient(90deg, #f7cac9 0%, #92a8d1 100%) !important;
}
.st-emotion-cache-1c7y2kd {
    color: #4b3832 !important;
}
.stButton>button {
    background-color: #f7cac9 !important;
    color: #4b3832 !important;
    border-radius: 8px;
    font-weight: bold;
    font-size: 1.1em;
}
</style>
""", unsafe_allow_html=True)

st.title("🎂 Family Connection AI Dashboard")
st.write("Welcome! This dashboard helps you stay connected with your loved ones, remember important dates, and see how the AI agents are working together.")

# Check API key
def get_orchestrator():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return None
    return FamilyConnectionOrchestrator(openai_api_key)

orchestrator = get_orchestrator()

if orchestrator:
    # Get today's birthdays
    memory_agent = orchestrator.agents["memory"]
    elderly_agent = orchestrator.agents["elderly"]
    master_agent = orchestrator.agents["master"]
    younger_agent = orchestrator.agents["younger_relative"]

    async def get_todays_birthdays():
        return await memory_agent.analyze_todays_birthdays()

    async def trigger_reminders():
        await memory_agent.check_and_alert()
        await asyncio.sleep(2)  # Let agents process

    # Sidebar: Actions
    st.sidebar.header("Actions")
    if st.sidebar.button("🔔 Trigger Birthday Reminders"):
        asyncio.run(trigger_reminders())
        st.sidebar.success("Reminders triggered!")

    # Main: Today's Birthdays
    st.subheader("🎉 Today's Birthdays")
    todays_birthdays = asyncio.run(get_todays_birthdays())
    if todays_birthdays:
        for b in todays_birthdays:
            st.info(f"**{b['name']}** ({b['relationship']}, Age {b.get('age', '?')}) - {b.get('notes', '')}")
            if 'llm_analysis' in b:
                st.write(f"_AI Insights:_ {b['llm_analysis']}")
    else:
        st.write("No birthdays today!")

    # Conversation Log
    st.subheader("🗒️ Master Agent Conversation Log")
    master_log = master_agent.get_conversation_log()
    if master_log:
        for entry in master_log[::-1]:
            st.markdown(f"**[{entry['timestamp']}]** {entry['type'].replace('_', ' ').title()}")
            st.json(entry)
    else:
        st.write("No interactions yet.")

    # Elderly Agent Responses
    st.subheader("👵 Elderly Agent Responses")
    elderly_responses = elderly_agent.get_user_responses()
    if elderly_responses:
        for r in elderly_responses[::-1]:
            st.markdown(f"**[{r['timestamp']}]** {r['birthday_info']['name']}")
            st.write(f"**Reminder:** {r['reminder_message']}")
            st.write(f"**User Response:** {r['user_response']}")
    else:
        st.write("No responses yet.")

    # Younger Relative Notifications
    st.subheader("🧑‍🦱 Younger Relative Notifications")
    notifications = younger_agent.get_notifications()
    if notifications:
        for n in notifications[::-1]:
            st.markdown(f"**[{n['timestamp']}]** Insights for {n['context']['birthday_info']['name']}")
            st.write(f"**Insights:** {n['insights']}")
            if 'suggestions' in n:
                st.write(f"**Suggestions:** {n['suggestions']}")
    else:
        st.write("No notifications yet.")

    st.markdown("---")
    st.caption("Made with ❤️ for families and connection.") 