import streamlit as st
import openai

import paperxai.credentials as credentials

########## set up the page ##########
st.set_page_config(
    page_title="PaperXAI",
    page_icon="🧙‍♂️",
    layout="wide",
)
st.header("paperXai🧙")
st.subheader("A web app to explore the most recent papers.")

if "create_report_button_clicked" not in st.session_state:
    st.session_state.create_report_button_clicked = False

def check_session_state_key_empty(session_state: dict, state_key: str): # will put in utils file
    if state_key not in session_state:
        return True
    elif session_state[state_key] in ["", None]:
        return True
    return False

def click_button(): # will put in utils file
    # check that model has been selected + API key entered + webpage url entered
    if (
        (check_session_state_key_empty(st.session_state, "model"))
        or (check_session_state_key_empty(st.session_state, "api_key"))
        ):
        st.session_state.create_report_button_clicked = False
    else:
        st.session_state.create_report_button_clicked = True

########## sidebar ##########

with st.sidebar:
    st.markdown(
        "## How to use\n"
        "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"
        "2. Fill out the information you want to search for in the latest papers\n"
        "3. Chat with the model about the papers you find most interesting 💬\n"
    )
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="Enter your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",
        value=credentials.OPENAI_API_KEY
        or st.session_state.get("OPENAI_API_KEY", ""),
    )

    st.session_state["OPENAI_API_KEY"] = api_key_input

    model = st.sidebar.selectbox(
    "Select the model you want to use:",
    [
        "gpt-3.5-turbo",
        "gpt-4",
    ],
    index=0,
    key="model",
)

    st.markdown("---")
    st.markdown("# About")
    st.markdown(
        "🧙paperXai allows you to filter through all the latest papers "
        "based off your questions. You can then chat to the model about "
        "the papers you find most interesting."
    )
    st.markdown(
        "This tool is a work in progress. "
        "You can contribute to the project on [GitHub](https://github.com/SebastianPartarrieu/paperXai/) "
        "with your feedback and suggestions💡"
    )
    st.markdown("Made by [Seb](https://twitter.com/seb_partarr)")
    st.markdown("---")

openai_api_key = st.session_state.get("OPENAI_API_KEY")
if not openai_api_key:
    st.warning(
        "Enter your OpenAI API key. You can get one from"
        " https://platform.openai.com/account/api-keys."
    )

########## main ##########
with st.form(key="qa_form"):
    query = st.text_area("Ask a question you want to answer about the papers")
    submit = st.form_submit_button("Submit")

st.button("Create report", on_click=click_button)


