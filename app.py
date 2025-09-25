# app_chat.py — Streamlit Chat with Bedrock Agent
import streamlit as st
import boto3
import uuid
from botocore.exceptions import ClientError

# --- CONFIG ---
REGION = "us-east-2"
AGENT_ID = "KNR6EZLQLR"   # your agent ID
ALIAS_ID = "G0BBSZPKRC"   # your alias ID

# --- SETUP AWS SESSION ---
def get_aws_session():
    """Load AWS credentials only from Streamlit secrets.toml"""
    try:
        return boto3.Session(
            aws_access_key_id=st.secrets.aws.access_key_id,
            aws_secret_access_key=st.secrets.aws.secret_access_key,
            region_name=REGION
        )
    except Exception as e:
        st.error(f"❌ AWS credentials not found in .streamlit/secrets.toml: {e}")
        return None

# --- CALL BEDROCK AGENT ---
def call_bedrock_agent(prompt_text: str, aws_session):
    try:
        client = aws_session.client("bedrock-agent-runtime", region_name=REGION)
        session_id = str(uuid.uuid4())

        resp = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=ALIAS_ID,
            sessionId=session_id,
            enableTrace=False,
            inputText=prompt_text
        )

        completion = ""
        for event in resp.get("completion", []):
            if "chunk" in event and "bytes" in event["chunk"]:
                completion += event["chunk"]["bytes"].decode()

        return completion.strip() or "⚠️ No response from agent."
    except ClientError as e:
        return f"❌ Bedrock API Error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# --- STREAMLIT CHAT UI ---
st.set_page_config(page_title="Timezone Chat — Bedrock Agent", page_icon="⏰")
st.title("⏰ Timezone Chat with Bedrock Agent")

aws_session = get_aws_session()
if not aws_session:
    st.stop()

# Session state for chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me about meeting times, timezone conversions, etc."):
    # User message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        response = call_bedrock_agent(prompt, aws_session)
        st.markdown(response)
    st.session_state["messages"].append({"role": "assistant", "content": response})
