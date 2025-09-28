import os
import shutil
import json
import re
from typing import Dict, List
import yt_dlp
import logging
from types import SimpleNamespace

from dotenv import load_dotenv

import requests
from typing import Dict, List

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

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
    def __init__(self, text_scores: str, json_config: str, user_audio_path:str, model_name: str = "gemini-2.5-pro", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.user_audio_path = user_audio_path
        self.context = json_config
        self.text_scores = text_scores
        self.scores = {}
        self.audio_urls = []  # will store audio file paths later

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
        return SimpleNamespace(text=text_val)

    def _generate_keywords(self, context: Dict[str, str]) -> List[str]:
        """
        Calls Gemini to generate multiple highly specific keywords based on context.
        """
        specific_topic = context.get("specific_topic", "")
        general_topic = context.get("general_topic", "")
        speech_format = context.get("format", "")

        prompt = (
            "You are an expert in public speaking and YouTube content search.\n"
            "Given the context below, generate 5-7 highly specific, precise keywords or short phrases "
            "that would return the most relevant public speaking videos on YouTube. "
            "Focus on different angles or styles, e.g., emotional, persuasive, TED-style, professional.\n"
            "Return them as a comma-separated list.\n\n"
            f"Context:\n- Specific Topic: {specific_topic}\n- General Topic: {general_topic}\n- Format: {speech_format}\n"
        )
        try:
            keywords_text = self._call_generate(prompt)
            keywords = [kw.strip() for kw in keywords_text.replace("\n", ",").split(",") if kw.strip()]
            return keywords
        except Exception as e:
            print(f"Warning: Gemini keyword generation failed: {e}")
            fallback = []
            if specific_topic:
                fallback.append(f"{specific_topic} {speech_format}".strip())
            if general_topic:
                fallback.append(f"{general_topic} {speech_format}".strip())
            if not fallback:
                fallback.append(f"{speech_format}".strip())
            return fallback

    def _search_youtube(self, keyword: str, max_results: int = 3) -> List[str]:
        """
        Queries the YouTube Data API for videos matching the keyword.
        """
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": max_results,
            "key": YOUTUBE_API_KEY
        }
        try:
            response = requests.get(YOUTUBE_SEARCH_URL, params=params)
            response.raise_for_status()
            items = response.json().get("items", [])
            return [f"https://www.youtube.com/watch?v={item['id']['videoId']}" for item in items]
        except Exception as e:
            print(f"Warning: YouTube search failed for keyword '{keyword}': {e}")
            return []

    def retrieve_audio_examples(self, context: Dict[str, str], limit: int = 3):
        """
        Main method: generates highly targeted keywords using Gemini, fetches top videos
        for each keyword, deduplicates, and stores them in self.audio_urls.
        """
        keywords = self._generate_keywords(context)
        print(f"Gemini suggested keywords: {keywords}")

        all_urls = []
        for kw in keywords:
            urls = self._search_youtube(kw)
            all_urls.extend(urls)

        # Deduplicate and limit results
        self.audio_urls = list(dict.fromkeys(all_urls))[:limit]
        print(f"Retrieved {len(self.audio_urls)} video URLs.")


    def download_reference_audio(self, video_urls: List[str], output_dir: str = "training_data"):
        """
        Downloads audio from given video URLs using yt_dlp and saves them locally.

        Args:
            video_urls (List[str]): List of video URLs to download.
            output_dir (str): Directory to save extracted audios.

        Returns:
            List[str]: List of file paths to the downloaded audios.
        """
        if os.path.exists(output_dir):
            try:
                shutil.rmtree(output_dir)
            except OSError as e:
                raise OSError(f"Failed to delete existing directory {output_dir}: {e}")
        
        # Create the directory (recursively if needed)
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory {output_dir}: {e}")
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
                    print(f"Downloading audio from: {url}")
                    info_dict = ydl.extract_info(url, download=True)
                    print(f"Downloaded: {info_dict.get('title', 'unknown title')}")
                    filename = ydl.prepare_filename(info_dict)
                    print(f"Prepared filename: {filename}")
                    audio_file = os.path.splitext(filename)[0] + ".wav"
                    print(f"Converted to audio file: {audio_file}")
                    audio_paths.append(audio_file)
                    print(f"Audio saved to: {audio_file}")
                except Exception as e:
                    logging.warning(f"Failed to download audio from {url}: {e}")

    def grade_audio(self, reference_audio_path: str) -> Dict[str, float]:
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
            f"Text Scores (script evaluation):\n\"\"\"{self.text_scores}\"\"\"\n\n"
            "Note: These text scores represent the grading of the user's script. "
            "You can use them as additional context to make more accurate and fair grading decisions.\n\n"
            f"User Audio Path:\n\"\"\"{self.user_audio_path}\"\"\"\n"
            f"Reference Audio Files:\n\"\"\"{reference_audio_path}\"\"\"\n\n"
            "Note: The reference audio path may contain multiple audio files. Compare the user's audio "
            "against all provided reference audios to generate more reliable and well-rounded feedback.\n\n"
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
        response = self._call_generate(prompt)

        # Step 4 — Extract JSON safely
        raw = response.text or ""
        raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE)

        try:
            self.scores = json.loads(raw)
            # Ensure rubric keys are present
            for key in rubric_schema.keys():
                rubric_schema[key] = self.scores.get(key, 0.0)
        except Exception as e:
            print(f"Warning: Failed to parse Gemini output as JSON. Raw output:\n{raw}\nError: {e}")
            self.scores = rubric_schema

    
    def encode_and_contextualize(self) -> tuple[dict, dict, str]:
        """
        Wrapper
        """
        self.retrieve_audio_examples(self.context)
        self.download_reference_audio(self.audio_urls,"training_data")
        self.grade_audio("training_data")

        if os.path.exists("training_data"):
            shutil.rmtree("training_data")

        return self.scores