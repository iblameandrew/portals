import streamlit as st
import json
import random
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama

# --- Configuration ---
BIBLE_FILE = "NumBible.TXT"
CAMPAIGN_FILE = "campaign.json"
MAX_BIBLE_LINE = 100117
RNG_MAX = 1000000

# --- Helper Functions ---

def initialize_files():
    """Creates the necessary bible and campaign files if they don't exist."""
    if not os.path.exists(BIBLE_FILE):
        st.error(f"{BIBLE_FILE} not found. Please create it with numbered lines of text.")
        st.stop()

    if not os.path.exists(CAMPAIGN_FILE):
        initial_campaign = {
            "title": "The War of the Heavens",
            "chapters": [
                {
                    "chapter_num": 1,
                    "content": "You stand on the precipice of the shattered city of Aethelburg, a celestial tear shimmering in the sky above. An angelic feather, pure white, drifts down and lands at your feet. The air crackles with a divine and infernal energy. Your quest has just begun: to seal the rift before the world is consumed by the final war between heaven and hell."
                }
            ]
        }
        with open(CAMPAIGN_FILE, 'w') as f:
            json.dump(initial_campaign, f, indent=4)

def load_campaign():
    """Loads the campaign data from the JSON file."""
    try:
        with open(CAMPAIGN_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # On first run after creation, load the initial data directly
        initialize_files()
        with open(CAMPAIGN_FILE, 'r') as f:
            return json.load(f)


def save_campaign(campaign_data):
    """Saves the campaign data to the JSON file."""
    with open(CAMPAIGN_FILE, 'w') as f:
        json.dump(campaign_data, f, indent=4)

def get_bible_paragraph(line_number):
    """Extracts a paragraph (target line +/- 5 lines) from the Bible file."""
    try:
        with open(BIBLE_FILE, 'r') as f:
            lines = f.readlines()
        
        start = max(0, line_number - 5)
        end = min(len(lines), line_number + 6)
        
        paragraph_lines = lines[start:end]
        return "".join(paragraph_lines)
    except FileNotFoundError:
        return "Error: Bible file not found."
    except IndexError:
        return "Error: Line number out of range."

# --- LangChain Functions ---

def check_semantic_resonance(paragraph, last_chapter_content):
    """Uses an LLM to check if the bible paragraph resonates with the campaign."""
    if 'llm' not in st.session_state or not st.session_state.llm:
        st.error("Please select and configure an LLM provider first.")
        return False, "LLM not configured."
    llm = st.session_state.llm

    prompt_text = f"""
    Analyze the semantic resonance between the following D&D campaign chapter and a religious text paragraph. The campaign is about angels, demons, and the apocalypse.

    Last Campaign Chapter: "{last_chapter_content}"
    
    Religious Paragraph: "{paragraph}"

    Does the religious paragraph semantically match the themes of the chapter? Respond with only "High Resonance" or "Low Resonance".
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({})
    st.session_state.debug_resonance = response # for debugging
    return "High Resonance" in response, response


def determine_fantasy_entity(paragraph):
    """Uses an LLM to determine what kind of fantasy entity the paragraph inspires."""
    if 'llm' not in st.session_state or not st.session_state.llm:
        st.error("Please select and configure an LLM provider first.")
        return "Unknown"
    llm = st.session_state.llm

    prompt_text = f"""
    Read the following religious text paragraph. Based on its contents, what kind of Dungeons & Dragons entity does it most inspire? Choose from one of the following categories:

    - Magic Artifact (e.g., a sword, crown, scroll, chalice)
    - New Scenario (e.g., a trial, a journey, a betrayal, a siege)
    - New Monster (e.g., a beast, a creature from the abyss, a corrupted angel)
    - New Character (e.g., a prophet, a king, a fallen hero, a divine messenger)
    - New Location (e.g., a forgotten temple, a heavenly gate, a pit to the underworld)

    The Paragraph: "{paragraph}"

    Respond with only the chosen category name.
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({})
    st.session_state.debug_entity = response # for debugging
    return response.strip()


def generate_next_chapter(campaign_history, paragraph, entity_type):
    """Uses an LLM to generate the next chapter of the campaign."""
    if 'llm' not in st.session_state or not st.session_state.llm:
        st.error("Please select and configure an LLM provider first.")
        return "LLM not configured."
    llm = st.session_state.llm
        
    full_history = "\n".join([ch["content"] for ch in campaign_history["chapters"]])

    prompt_text = f"""
    You are a Dungeons & Dragons Dungeon Master. Write the next chapter for a campaign about angels, demons, and the end of the world. The player can die but can be resurrected with the correct holy verse.

    Campaign History So Far:
    {full_history}

    The theme of the chapter is based from the following holy text:
    "{paragraph}"

    The new element you must introduce to the story is a: "{entity_type}".

    Write the next chapter of the campaign. It should be about 2-3 paragraphs long. Weave the inspiration from the holy text into the narrative. Introduce a new challenge, decision, or discovery for the player based on the new {entity_type}. End the chapter on a compelling note.
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({})
    return response.strip()

# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="Portals")

# Initialize files on first run
initialize_files()

# Initialize state
if 'campaign' not in st.session_state:
    st.session_state.campaign = load_campaign()
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.title("Portals: TempleOS reimagined")
st.markdown("Consult the oracle to let divine providence guide your adventure.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Oracle's Console")

    st.subheader("1. Configure LLM Provider")
    
    ollama_model = st.text_input("Enter Ollama model name (e.g., 'llama3'):", "dengcao/Qwen3-30B-A3B-Instruct-2507:latest")
    if st.button("Connect to Ollama"):
        try:
            with st.spinner(f"Connecting to Ollama model '{ollama_model}'..."):
                llm_instance = Ollama(model=ollama_model)
                llm_instance.invoke("test")
            st.session_state.llm = llm_instance
            st.success(f"Successfully connected to Ollama with model '{ollama_model}'.")
        except Exception as e:
            st.error(f"Failed to connect to Ollama. Ensure Ollama is running and the model is downloaded. Error: {e}")
            st.session_state.llm = None

    st.markdown("---")
    st.subheader("2. Generate Adventure")

    # This button is disabled if the LLM is not configured OR if processing is ongoing.
    if st.button("Consult the Oracle", type="primary", disabled=(st.session_state.llm is None or st.session_state.processing)):
        st.session_state.messages = [] # Clear previous messages
        st.session_state.processing = True # Set flag to disable button and start processing
        st.rerun() # Rerun to immediately reflect the disabled button state

    # This logic block only runs if the 'processing' flag is True
    if st.session_state.processing:
        # The spinner provides visual feedback during the entire process
        with st.spinner("The Oracle is interpreting the holy message... The Fates are weaving..."):
            try:
                # 1. Generate Random Number
                random_number = random.randint(0, RNG_MAX)
                st.session_state.messages.append(f"The heavens spin... a number is chosen: **{random_number}**")

                if 0 <= random_number <= MAX_BIBLE_LINE:
                    # 2. Extract Bible Paragraph
                    paragraph = get_bible_paragraph(random_number)
                    st.session_state.messages.append(f"A verse is revealed (from line ~{random_number}):\n\n---\n*{paragraph.strip()}*")

                    # 3. Check Resonance (LLM Call 1)
                    last_chapter = st.session_state.campaign['chapters'][-1]['content']
                    has_resonance, reason = check_semantic_resonance(paragraph, last_chapter)
                    st.session_state.messages.append(f"**Analysis:** {reason}")

                    if has_resonance:
                        # 4. Determine Entity (LLM Call 2)
                        entity = determine_fantasy_entity(paragraph)
                        st.session_state.messages.append(f"The verse inspires a new **{entity}**.")

                        # 5. Generate Next Chapter (LLM Call 3)
                        new_chapter_content = generate_next_chapter(st.session_state.campaign, paragraph, entity)
                        
                        # 6. Save Progress
                        new_chapter_num = len(st.session_state.campaign['chapters']) + 1
                        new_chapter = {"chapter_num": new_chapter_num, "content": new_chapter_content}
                        st.session_state.campaign['chapters'].append(new_chapter)
                        save_campaign(st.session_state.campaign)
                        
                        st.session_state.messages.append("The vision is clear! Your story progresses.")

                    else:
                        st.session_state.messages.append("The heavens are silent. The verse holds no meaning for your current path. Consult the oracle again.")
                else:
                    st.session_state.messages.append("The number is outside the sacred texts. The oracle offers no guidance. Try again.")
            
            finally:
                # This block is GUARANTEED to run, whether the process succeeded or failed.
                st.session_state.processing = False # Reset the flag to re-enable the button
                st.rerun() # Rerun to update the UI and show the final results/re-enable button.

    st.markdown("---")
    st.subheader("Oracle Output")
    if st.session_state.messages:
        for message in st.session_state.messages:
            st.markdown(message, unsafe_allow_html=True)
            st.markdown("---")
            
with col2:
    st.header("Campaign Chronicle")
    if st.session_state.campaign:
        st.markdown(f"### {st.session_state.campaign['title']}")
        
        for chapter in reversed(st.session_state.campaign['chapters']):
            with st.expander(f"Chapter {chapter['chapter_num']}", expanded=(chapter['chapter_num'] == len(st.session_state.campaign['chapters']))):
                st.markdown(chapter['content'])