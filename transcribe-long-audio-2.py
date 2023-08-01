import openai
from pydub import AudioSegment
from pydub.utils import make_chunks
import json
import tempfile
import os
import spacy
import time

print(AudioSegment.converter)
# Set up OpenAI API credentials
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')


print(os.path.isfile("C:/Code/GenAI_Roundtable/Recordings/roundtable-1.mp3"))
#audio_file = AudioSegment.from_file("/Users/henrietta.ridley/vscode/recordings/roundtable-1.m4a", format="m4a")
audio_file = AudioSegment.from_file("C:/Code/GenAI_Roundtable/Recordings/roundtable-1.m4a", format="m4a")

#audio_file = AudioSegment.from_file("/Users/henrietta.ridley/vscode/recordings/roundtable-1.m4a", format="m4a")
# PyDub handles time in milliseconds
ten_minutes = 10 * 60 * 1000

# Test with just 10mins to start off with
# first_10_minutes = audio_file[:ten_minutes]
# first_10_minutes.export("first_10.mp3", format="mp3")
# audio_file= open("first_10.mp3", "rb")
# transcript = openai.Audio.transcribe("whisper-1", audio_file)

# Divide audio into chunks
chunks = make_chunks(audio_file, ten_minutes)
chunks = chunks[1]

# Transcribe each chunk and perform diarization
transcripts = []
speakers = []

# Create a temporary directory to store the audio chunks
temp_dir = tempfile.mkdtemp()

for i, chunk in enumerate(chunks):
    audio_data = chunk.raw_data

    # Write audio data to temporary file
    with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".wav") as f:
        temp_file_path = f.name
        chunk.export(temp_file_path, format="wav")

    # Transcribe audio from file
    with open(temp_file_path, mode='rb') as f:
        response = openai.Audio.transcribe("whisper-1", file=f)
        transcript = response['text']
        transcripts.append(transcript)

    # Remove temporary file
    os.unlink(temp_file_path)

    print("Chunk completed: " + str(i))


# Create functions to summarise the discussion, convert it into interesting talking points and suggest alternative areas to investigate

# prompts
formal_pov = "Incorporate the valuable insights from the discussion. Identify opportunities to enhance service offerings, optimize operational efficiencies, and capitalize on emerging market trends. Focus on adapting to evolving client needs, leveraging data-driven decision-making, and fostering strategic partnerships. Consider exploring AI-driven solutions and digital transformation to stay competitive in the ever-changing business landscape. You are English."
informal_summary = "Take action based on the fascinating insights discussed. Stay ahead of the curve by adapting to evolving client needs, making data-driven decisions, and embracing digital transformation. Explore strategic partnerships and leverage emerging technologies to gain a competitive edge. Look for opportunities to implement innovative approaches and improve operational efficiency. You are English."
next_steps = "Engage in further exploration based on the thought-provoking discussion. Take action by asking the following questions: How can we effectively adapt to evolving client needs? What are some successful examples of data-driven decision-making in our industry? Identify potential strategic partners to expand our reach and offerings. Consider implementing AI and automation to streamline operations and enhance customer experiences. Stay updated on new market trends, such as sustainability initiatives or customer-centric strategies, and assess their relevance for our business. You are English."

def strip_unimportant_parts(text):
    # Load English language model
    nlp = spacy.load("en_core_web_sm")
    # Set of unimportant part-of-speech tags
    unimportant_tags = {"CCONJ", "DET", "PART", "PRON", "SCONJ"}
    # Process the text with spaCy
    doc = nlp(text)
    # Filter out unimportant parts based on part-of-speech tags
    stripped_text = " ".join(token.text for token in doc if token.pos_ not in unimportant_tags)
    return stripped_text

def summarise_discussion(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": formal_pov},
            {"role": "user", "content": text}]
    )
    summary = response["choices"][0]["message"]["content"].strip()
    return summary

def generate_talking_points(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": informal_summary},
            {"role": "user", "content": text}]
    )
    talking_points = response["choices"][0]["message"]["content"].strip()
    return talking_points

def suggest_alternative_areas(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": informal_summary},
            {"role": "user", "content": text}]
    )
    alternatives = response["choices"][0]["message"]["content"].strip()
    return alternatives


text = " ".join(transcripts)
stripped_transcription = strip_unimportant_parts(text)

summary = summarise_discussion(stripped_transcription)
talking_points = generate_talking_points(stripped_transcription)
alternatives = suggest_alternative_areas(stripped_transcription)

print("Summary:")
print(summary)
print("\nTalking Points:")
print(talking_points)
print("\nAlternative Areas to Investigate:")
print(alternatives)
