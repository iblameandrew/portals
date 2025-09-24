import streamlit as st
import re
import json
import random
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from datetime import date, timedelta

# --- Astrological Imports ---
# Add kerykeion for astrological calculations. Ensure you have installed it:
# pip install kerykeion
try:
    from kerykeion import AstrologicalSubject, NatalAspects, Report
except ImportError:
    st.error("The 'kerykeion' library is not installed. Please install it by running: pip install kerykeion")
    st.stop()


# --- Configuration ---
BIBLE_FILE = "NumBible.TXT"
CAMPAIGN_FILE = "campaign.json"
MAX_BIBLE_LINE = 100117
RNG_MAX = 1000000

def strip_think_tags(text: str) -> str:
    """
    Removes <think>...</think> tags and their content from a string.

    Args:
        text: The input string that may contain think tags.

    Returns:
        A new string with all think tags and their inner content removed.
    """
    pattern = r"<think>.*?</think>"
    return re.sub(pattern, "", text, flags=re.DOTALL)

# --- Astrological Data Functions (from astro.py) ---

def trim_astrological_report(full_report_text: str) -> str:
    """Trims the full astrological report to only major aspects for LLM analysis."""
    try:
        parts = full_report_text.split("## Natal Aspects")
        if len(parts) != 2:
            return full_report_text
        header = parts[0].strip()
        json_string = parts[1]
        aspects_list = json.loads(json_string)
    except (json.JSONDecodeError, IndexError):
        return full_report_text

    MAJOR_BODIES = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']
    MAJOR_ASPECTS = ['conjunction', 'opposition', 'trine', 'square', 'sextile']
    ORB_THRESHOLD = 3.0
    
    important_aspect_summaries = []
    for aspect in aspects_list:
        p1, p2, aspect_type, orbit = aspect.get('p1_name'), aspect.get('p2_name'), aspect.get('aspect'), aspect.get('orbit')
        if (p1 in MAJOR_BODIES and p2 in MAJOR_BODIES and aspect_type in MAJOR_ASPECTS and abs(orbit) <= ORB_THRESHOLD):
            summary_line = f"- {p1} {aspect_type} {p2} (orb: {orbit:.2f}°)"
            important_aspect_summaries.append(summary_line)
            
    if not important_aspect_summaries:
        summary_section = f"## Key Natal Aspects\nNo major aspects found within a {ORB_THRESHOLD}° orb."
    else:
        summary_section = "## Key Natal Aspects\n" + "\n".join(important_aspect_summaries)
    return header + "\n\n" + summary_section

def generate_birth_chart_markdown(target_date):
    """Generates a full birth chart report for a given date."""
    try:
        # Using a default time and location for a "mundane" chart of the day
        subject = AstrologicalSubject(name=target_date.strftime("%Y-%m-%d"), year=target_date.year, month=target_date.month, day=target_date.day, hour=0, minute=0, city="New York", nation="US")
        report = Report(subject).get_full_report()
        aspects = NatalAspects(subject)
        aspects_data = [a.model_dump() for a in aspects.relevant_aspects]
        return f"{report}\n## Natal Aspects\n{json.dumps(aspects_data, indent=2)}"
    except Exception as e:
        return f"Could not generate birth chart for {target_date.strftime('%Y-%m-%d')}. Error: {e}"

# --- Helper Functions (from app.py) ---

def initialize_files():
    """Creates the necessary bible and campaign files if they don't exist."""
    if not os.path.exists(BIBLE_FILE):
        st.error(f"{BIBLE_FILE} not found. Please create it with numbered lines of text.")
        st.stop()
    
    # --- MODIFICATION: Initialize campaign with an empty chapter list ---
    if not os.path.exists(CAMPAIGN_FILE):
        initial_campaign = {
            "title": "The War of the Heavens",
            "chapters": []  # Start with no chapters
        }
        with open(CAMPAIGN_FILE, 'w') as f:
            json.dump(initial_campaign, f, indent=4)

def load_campaign():
    """Loads the campaign data from the JSON file."""
    try:
        with open(CAMPAIGN_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
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
    response = strip_think_tags(response)
    st.session_state.debug_resonance = response # for debugging
    return "High Resonance" in response, response

def determine_fantasy_entity(paragraph):
    """Uses an LLM to determine what kind of fantasy entity the paragraph inspires."""
    if 'llm' not in st.session_state or not st.session_state.llm:
        st.error("Please select and configure an LLM provider first.")
        return "Unknown"
    llm = st.session_state.llm

    prompt_text = f"""
    Read the following religious text. Based on its contents, what kind of entity does it most inspire? Choose from one of the following categories:

    - Magic Artifact 
    - New Scenario 
    - New Monster 
    - New Character 
    - New Location 

    The Religious Paragraph: "{paragraph}"

    Respond with only the chosen category name.
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({})
    response = strip_think_tags(response)
    st.session_state.debug_entity = response # for debugging
    return response.strip()

def generate_next_chapter(campaign_history, paragraph, trimmed_chart, entity_type):
    """Uses an LLM to generate the next chapter of the campaign."""
    if 'llm' not in st.session_state or not st.session_state.llm:
        st.error("Please select and configure an LLM provider first.")
        return "LLM not configured."
    llm = st.session_state.llm
        
    full_history = "\n".join([ch["content"] for ch in campaign_history["chapters"]])
    
    # --- MODIFICATION: Adjust prompt if history is empty ---
    if not full_history:
        history_prompt = "This is the very first chapter. Begin the story."
    else:
        history_prompt = f"Campaign History So Far:\n{full_history}"


    prompt_text = f"""
    You are a Dungeons & Dragons Dungeon Master inspired by Apophatic theology and Mundane Astrology. 
    
    Write the next chapter for a campaign about angels, demons, and the end of the world. The player can die but can be resurrected with the correct holy verse.

    Omit mentioning astrological data in the chapter.

    {history_prompt}

    Your two sources of divine inspiration for this chapter are:

    1. A Holy Text:
    "{paragraph}"

    2. The Astrological Chart that must serve you as a guide to narrate the chapter: 
    "{trimmed_chart}"

    The new element you must introduce to the story, derived from these sources, is a: "{entity_type}".

    Write the next chapter of the campaign (2-3 paragraphs). 
    
    Weave the inspiration from BOTH the holy text's cryptic message and the astrological chart's tensions (e.g., a Mars-Pluto square suggesting conflict, a Venus-Jupiter trine suggesting a fortunate alliance) into the narrative. Introduce a new challenge, decision, or discovery for the player based on the new {entity_type}. 

    The story must be written without any references to the holy text or the astrological chart, but regardless be inspired by it.
    
    End the chapter on a compelling note.
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    response = strip_think_tags(response)

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

    st.subheader("1. Configure Oracle")
    
    ollama_model = st.text_input("Enter Ollama model name:", "qwen3:30b-a3b-thinking-2507-q4_K_M")
    if st.button("Connect to Ollama"):
        try:
            with st.spinner(f"Connecting to Ollama model '{ollama_model}'..."):
                llm_instance = Ollama(model=ollama_model)
            st.session_state.llm = llm_instance
            st.success(f"Successfully connected to Ollama with model '{ollama_model}'.")
        except Exception as e:
            st.error(f"Failed to connect to Ollama. Ensure Ollama is running and the model is downloaded. Error: {e}")
            st.session_state.llm = None
    
    st.markdown("---")
    st.subheader("2. Set the Date")
    selected_date = st.date_input("Select a date to consult the heavens", date.today())
    
    st.markdown("---")
    st.subheader("3. Generate Adventure")

    if st.button("Consult the Oracle", type="primary", disabled=(st.session_state.llm is None or st.session_state.processing)):
        st.session_state.messages = []
        st.session_state.processing = True
        st.rerun()

    if st.session_state.processing:
        with st.spinner("The Oracle is interpreting the celestial and holy messages..."):
            try:
                # 1. Generate Random Number for Bible verse
                random_number = random.randint(0, RNG_MAX)
                st.session_state.messages.append(f"A number is chosen: **{random_number}**")

                if 0 <= random_number <= MAX_BIBLE_LINE:
                    # 2. Extract Bible Paragraph
                    paragraph = get_bible_paragraph(random_number)
                    st.session_state.messages.append(f"A verse is revealed (from line ~{random_number}):\n\n---\n*{paragraph.strip()}*")

                    # --- MODIFICATION: Handle resonance check for new campaigns ---
                    # If chapters exist, check resonance. Otherwise, skip for the first chapter.
                    if st.session_state.campaign['chapters']:
                        last_chapter_content = st.session_state.campaign['chapters'][-1]['content']
                        has_resonance, reason = check_semantic_resonance(paragraph, last_chapter_content)
                        st.session_state.messages.append(f"**Verse Analysis:** {reason}")
                    else:
                        has_resonance = True # Automatically true for the first chapter
                        st.session_state.messages.append("**Verse Analysis:** Generating the first chapter. The path is new and resonance is assumed.")


                    if has_resonance:
                        # 4. Generate and Trim Astrological Chart
                        st.session_state.messages.append(f"Consulting the heavens for **{selected_date.strftime('%Y-%m-%d')}**...")
                        full_chart = generate_birth_chart_markdown(selected_date)
                        trimmed_chart = trim_astrological_report(full_chart)
                        
                        # 5. Determine Entity from both sources
                        entity = determine_fantasy_entity(paragraph)
                        st.session_state.messages.append(f"The verse and stars inspire a new **{entity}**.")

                        # 6. Generate Next Chapter from both sources
                        new_chapter_content = generate_next_chapter(st.session_state.campaign, paragraph, trimmed_chart, entity)
                        
                        # 7. Save Progress
                        new_chapter_num = len(st.session_state.campaign['chapters']) + 1
                        new_chapter = {"chapter_num": new_chapter_num, "content": new_chapter_content}
                        st.session_state.campaign['chapters'].append(new_chapter)
                        save_campaign(st.session_state.campaign)
                        
                        st.session_state.messages.append("The vision is clear! Your story progresses.")
                    else:
                        st.session_state.messages.append("The verse holds no meaning for your current path. Consult again.")
                else:
                    st.session_state.messages.append("The number is outside the sacred texts. The oracle offers no guidance.")
            
            finally:
                st.session_state.processing = False
                st.rerun()

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
        
        # Display chapters if any exist
        if not st.session_state.campaign['chapters']:
            st.info("Your campaign has not yet begun. Consult the Oracle to write the first chapter.")

        for chapter in reversed(st.session_state.campaign['chapters']):
            # The first chapter should be expanded by default
            is_first_chapter_view = (len(st.session_state.campaign['chapters']) == 1)
            with st.expander(f"Chapter {chapter['chapter_num']}", expanded=(chapter['chapter_num'] == len(st.session_state.campaign['chapters']) or is_first_chapter_view)):
                st.markdown(chapter['content'])