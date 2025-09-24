# Portals: TempleOS reimagined

<p align="center">
  <img src="https://github.com/user-attachments/assets/457598b4-8abb-464b-8d6b-9f54df64e058" />
</p>

No one will repeat Terry's feat; building an entire OS to use it as a random number generator is beyond anyone's capacity in the world. But over the years something stuck with me about Terry's obsession with random numbers and matching those numbers to the content of different texts in order to "get a message from God" - essentially Terry believed that God was like a programmer, that made the world and the creations within it to entertain him. Non-entertaining creations in this cosmovision are regarded as duds, and entertaining creations are regarded as the logical evolutionary step for mankind.

Here Terry believed that in order to get a message from God you needed to exchange love in an act of self-defeat and surrender to a greater circumstance, in order to get for the blink of a moment God's attention. Then upon prompting a random number generator with the "fresh scene" of the "act of love", the random number generator would respond back with a number that upon being matched with an index of the bible would emerge "order" as a synchronicity and hand a coherent message. If the offering for God was satisfying, surprisingly the message would say something meaningful as it was recorded in Terry's live-streams. A lot of times though, the offerings were not good enough and to quote Terry: God thought it was boring.

After some years ruminating I came to understand that the essence of Terry's fixation could be broken down into two factors: the first one is doing something that enables a measure of change in one's perception (entertainment), and the second one, was the posteriori state that emerges as a consequence of getting retroactively a message that one wholeheartedly believes to come from God and thus, on understanding force our field of judgment and perception to reorganize around the new message or "new command". In every sense of the word; what Terry Davis was doing with his temple was to open portals to navigate them.

A portal thus is something that changes the possibility of motion of an object. Realistic portals however are mental, in the same sense a movie or great piece of literature can change our field of action by measure of how they realign our thoughts and "help us see" new possibilities where previously none were seen. Today with LLMs, this idea can be extended deeper into something more meaningful that's actually fun to engage in.

<p align="center">
  <img src="https://github.com/user-attachments/assets/1781a53e-a3df-42d6-b285-7b582cd441c6" />
</p>

# How to Play

The first rule of this game is that you will only get out of it what you put into it. The core mechanic is the "offering"—an action you perform in your own life that fundamentally changes you or your perspective. This is not something you input into the application; it is a personal act of significance. The nature of the offering is up to you. It can be an act of love, creation, self-sacrifice, or a difficult decision that marks a transition from one point of view to another.

Once the "offering is fresh" or just performed, you consult the oracle in the application. This is where your personal journey and the digital world intersect.

## How It Works (The Digital Oracle)

The application acts as a digital oracle, translating the abstract energy of your offering into a tangible chapter of a story. It's a Dungeons & Dragons style campaign where you are the protagonist, and providence is the Dungeon Master.

Here's the process when you "Consult the Oracle":

1.  **A Number is Chosen**: A random number is generated. Within the game's philosophy, your real-world offering is what "guides" the hand of fate to select a meaningful number.
2.  **A Verse is Revealed**: If the number falls within the range of the sacred texts (`NumBible.TXT`), a corresponding paragraph is extracted. This is the raw, divine message.
3.  **Resonance Check**: A Large Language Model (LLM) analyzes the revealed verse against the last chapter of your ongoing campaign. It determines if the verse has "High Resonance" or "Low Resonance" with your story's current themes (angels, demons, the apocalypse).
4.  **The Vision Forms**:
    *   **If Resonance is High**: The offering was a success! The LLM then determines what kind of D&D entity the verse inspires: a `Magic Artifact`, `New Scenario`, `New Monster`, `New Character`, or `New Location`.
    *   **The Next Chapter is Written**: Acting as a Dungeon Master, the LLM uses this new entity and the holy verse to generate the next chapter of your campaign, weaving it into the existing narrative and presenting a new challenge or discovery. Your campaign chronicle is updated and saved.
    *   **If Resonance is Low**: The heavens are silent. The offering was not significant enough or its meaning is not yet relevant to your path. The oracle provides no new chapter, and you are prompted to try again after your next significant life-act.

Do notice though; that the LLM is simply a tool for interpretation. It improvises a story based on random bible verses. It's not the LLM that gets any insight whatsoever into what your real-world offering is: that's only between "God" and you.

# How to Run

## Prerequisites

*   **Python 3.8+**
*   **Ollama**: You must have Ollama installed and running on your machine. You can download it from [ollama.ai](https://ollama.ai/).
*   **An Ollama Model**: You need a model to power the LLM. We recommend `llama3`. You can pull it by running:
    ```sh
    ollama pull llama3
    ```

## Setup

1.  **Clone the repository:**
    ```sh
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Python dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file would contain `streamlit`, `langchain-google-genai`, and `langchain-community`)*

3.  **Prepare the Sacred Text:**
    The application requires a file named `NumBible.TXT` in the same directory. This file should be a plain text version of a religious text (like the Bible), where each line is numbered. The script is configured for a file with up to `100117` lines.

4.  **Campaign File:**
    A `campaign.json` file will be created automatically on the first run with an introductory chapter. Do not delete this file, as it stores your story's progress.

## Running the Application

1.  **Start the Streamlit app:**
    ```sh
    streamlit run app.py
    ```

2.  **Configure the LLM:**
    In the web interface, enter the name of your downloaded Ollama model (e.g., `llama3`) and click "Connect to Ollama". You must do this before consulting the oracle.

3.  **Consult the Oracle:**
    Once the LLM is connected, perform your real-world "offering". When you are ready, click the "Consult the Oracle" button to see how your story unfolds.