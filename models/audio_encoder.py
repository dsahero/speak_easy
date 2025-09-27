import os
import json
import re
from typing import Dict, List
import yt_dlp
import logging

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*a, **k):
        return False

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None

load_dotenv()
# Helper function for configuring Gemini
def _configure_genai_from_env():
    global genai
    if genai is None:
        import sys as _sys
        if 'google.generativeai' in _sys.modules:
            genai = _sys.modules['google.generativeai']
        elif 'google' in _sys.modules and hasattr(_sys.modules['google'], 'generativeai'):
            genai = getattr(_sys.modules['google'], 'generativeai')
        else:
            try:
                import google.generativeai as _genai  # type: ignore
                genai = _genai
            except Exception:
                return
    if hasattr(genai, "configure") and os.environ.get("GEMINI_API_KEY"):
        try:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        except Exception:
            pass


class AudioEncoder:
    def __init__(self, model_name: str = "gemini-2.5-pro", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.context = {}
        self.audio_examples = []  # will store audio file paths later

    def _call_generate(self, prompt: str):
        _configure_genai_from_env()
        global genai
        if genai is None or not hasattr(genai, "GenerativeModel"):
            raise RuntimeError("Gemini model not available")
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)
        text_val = getattr(response, "text", response)
        if not isinstance(text_val, str):
            text_val = str(text_val)
        from types import SimpleNamespace
        return SimpleNamespace(text=text_val)

    def extract_context(self, text_encoder_context: Dict[str, str]) -> Dict[str, str]:
        """
        Takes context from TextEncoder and stores it for AudioEncoder grading.
        """
        self.context = {
            "specific_topic": text_encoder_context.get("specific_topic", "unknown"),
            "general_topic": text_encoder_context.get("general_topic", "unknown"),
            "format": text_encoder_context.get("format", "unknown")
        }
        return self.context

    def retrieve_audio_examples(self, context: Dict[str, str], limit: int = 3) -> List[str]:
        """
        Given the context from TextEncoder, search for public speaking videos
        that match the topic and format, and return their URLs.
        """

        # Step 1: Extract context
        specific_topic = context.get("specific_topic", "")
        general_topic = context.get("general_topic", "")
        speech_format = context.get("format", "")

        # Step 2: Build search query
        if specific_topic and specific_topic != "unknown":
            search_query = f"public speaking examples for '{specific_topic}' {speech_format}"
        elif general_topic and general_topic != "unknown":
            search_query = f"public speaking examples for '{general_topic}' {speech_format}"
        else:
            search_query = f"public speaking examples for '{speech_format}'"

        # Step 3: Create Gemini prompt (empty string for now)
        prompt = (
          "You are a helpful assistant specializing in finding high-quality public speaking examples.\n"
          "Given the following context, return ONLY a newline-separated list of URLs to videos "
          "or audio recordings of public speeches. Do NOT include explanations, descriptions, "
          "headings, or any extra text.\n\n"
          f"Context:\n"
          f"- Specific Topic: {specific_topic}\n"
          f"- General Topic: {general_topic}\n"
          f"- Format: {speech_format}\n\n"
          f"Search Query: {search_query}\n\n"
          "Return URLs only."
        )

        # Step 4: Call Gemini to retrieve examples
        print(f"AudioEncoder: Calling Gemini for audio examples with query: '{search_query}'...")
        try:
            response = self._call_generate(prompt)
            raw_output = response.text or ""
            # For now, assume Gemini returns a newline-separated list of URLs
            urls = [line.strip() for line in raw_output.split("\n") if line.strip()]
            self.audio_examples = urls[:limit]
        except Exception as e:
            print(f"Warning: Failed to retrieve audio examples. Error: {e}")
            self.audio_examples = []

        return self.audio_examples


    def download_reference_audio(self, video_urls: List[str], output_dir: str = "reference_audios") -> List[str]:
        """
        Downloads audio from given video URLs using yt_dlp and saves them locally.

        Args:
            video_urls (List[str]): List of video URLs to download.
            output_dir (str): Directory to save extracted audios.

        Returns:
            List[str]: List of file paths to the downloaded audios.
        """
        os.makedirs(output_dir, exist_ok=True)
        audio_paths = []

        ydl_opts = {
            "format": "bestaudio/best",  # best quality audio
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),  # output file template
            "postprocessors": [{
                "key": "FFmpegExtractAudio",  # extract audio only
                "preferredcodec": "wav",      # change to "mp3" if desired
                "preferredquality": "192",    # quality for mp3
            }],
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in video_urls:
                try:
                    logging.info(f"Downloading audio from: {url}")
                    info_dict = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info_dict)
                    audio_file = os.path.splitext(filename)[0] + ".wav"
                    audio_paths.append(audio_file)
                except Exception as e:
                    logging.warning(f"Failed to download audio from {url}: {e}")

        return audio_paths

    def grade_audio(self, user_audio_path: str, reference_audio_path: str) -> Dict[str, float]:
        """
        Grade the user's audio against a reference audio using Gemini Pro's audio capabilities.

        Args:
            user_audio_path (str): Path to the user's audio file.
            reference_audio_path (str): Path to the reference audio file.

        Returns:
            Dict[str, float]: Rubric scores for the audio evaluation.
        """

        # Step 1 — Define rubric schema
        rubric_schema = {
            "clarity_score": 0.0,
            "pronunciation_score": 0.0,
            "tone_score": 0.0,
            "pacing_score": 0.0,
            "engagement_score": 0.0
        }

        # Step 2 — Create prompt
        prompt = (
            "You are an empathetic real-time public speaking coach. "
            "Your personality is supportive, constructive, and detailed, aiming to help the speaker improve "
            "by giving contextual notes without overwhelming them. "
            "Your goal is to help the speaker know what their audience is perceiving in real time.\n\n"
            "Analyze and give feedback on:\n"
            "1. Clarity & Understanding: Pronunciation, diction, and message clarity.\n"
            "2. Pacing: Speaking speed; identify moments too fast or too slow.\n"
            "3. Filler Words: Detect filler words (e.g., 'um', 'uh', 'like') and note their timestamps.\n"
            "4. Engagement: Vocal variety (pitch, pace, volume), enthusiasm.\n"
            "5. Message Delivery: Are key points getting across clearly?\n"
            "6. Emotional Tone: Confidence, persuasiveness, engagement.\n"
            "7. Areas for Improvement: Provide specific, constructive tips.\n\n"
            "Speech Context:\n"
            f"- Specific Topic: {self.context.get('specific_topic', '')}\n"
            f"- General Topic: {self.context.get('general_topic', '')}\n"
            f"- Format: {self.context.get('format', '')}\n\n"
            "Transcript:\n\"\"\"{self.transcript}\"\"\"\n\n"
            "User Audio Path:\n\"\"\"{user_audio_path}\"\"\"\n"
            "Reference Audio Path:\n\"\"\"{reference_audio_path}\"\"\"\n\n"
            "Return ONLY a JSON object with the following keys and scores (0.0 to 1.0):\n"
            "{\n"
            "  \"clarity_score\": float,\n"
            "  \"pronunciation_score\": float,\n"
            "  \"tone_score\": float,\n"
            "  \"pacing_score\": float,\n"
            "  \"engagement_score\": float,\n"
            "  \"filler_word_instances\": [{\"word\": str, \"timestamp\": float}],\n"
            "  \"areas_for_improvement\": [str]\n"
            "}\n"
            "Be concise, precise, and encouraging."
        )

        # Step 3 — Call Gemini Pro's audio grading (via helper method)
        print("AudioEncoder: Calling Gemini for audio grading...")
        response = self._call_generate_audio(prompt, user_audio_path, reference_audio_path)

        # Step 4 — Extract JSON safely
        raw = response.text or ""
        raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE)

        try:
            scores = json.loads(raw)
            # Ensure rubric keys are present
            for key in rubric_schema.keys():
                rubric_schema[key] = scores.get(key, 0.0)
        except Exception as e:
            print(f"Warning: Failed to parse Gemini output as JSON. Raw output:\n{raw}\nError: {e}")
            scores = rubric_schema

        return scores