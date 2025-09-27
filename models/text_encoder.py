import os
import json
from datetime import datetime
from typing import List, Union, Dict, Any
import re
import torch
from dotenv import load_dotenv

# Try to import the optional Google Generative AI client. During unit tests
# the test harness injects a mock into sys.modules['google.generativeai']
# before importing this module. Guard the import so tests can run without
# the real package installed.
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore

load_dotenv()  # Load .env variables


def _configure_genai_from_env():
    """Configure genai client from environment if available.

    This is called lazily so tests can set sys.modules mocks prior to use.
    """
    global genai
    if genai is None:
        # Prefer any test-injected module in sys.modules to support mocking
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
    # Configure only if module exposes configure and GEMINI_API_KEY is present
    if hasattr(genai, "configure") and os.environ.get("GEMINI_API_KEY"):
        try:
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        except Exception:
            # Avoid failing import/configuration in environments without network or creds
            pass


class TextEncoder:
    """
    A text encoder that processes transcripts, extracts context,
    finds public speaking examples, and produces rubric scores.
    """

    feat_dim = 16  # dummy tensor size for compatibility

    def __init__(self, model_name: str = "gemini-1.5-flash", device: str = "cpu"):
        self.device = device
        # Store model name and defer creating model instances until call-time so
        # unit tests can patch `google.generativeai.GenerativeModel.generate_content`.
        self.model_name = model_name
        self.model = None
        self.transcript = ""
        self.scores = {}
        self.context = {}
        self.examples = "" # Store raw text examples or URLs

    def __call__(self, texts: Union[str, List[str]]) -> torch.Tensor:
        """Allow batch calls returning dummy tensors."""
        if isinstance(texts, str):
            batch = [texts]
        elif isinstance(texts, (list, tuple)):
            batch = texts
        else:
            raise ValueError("Input to TextEncoder must be str or list of str")

        return torch.zeros(len(batch), self.feat_dim, device=self.device)

    def read_transcript(self, transcript_file: str):
        """Load transcript text from a file."""
        try:
            with open(transcript_file, "r", encoding="utf-8") as f:
                self.transcript = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Transcript file not found: {transcript_file}")

    def extract_context(self, speech_purpose: str) -> Dict[str, str]:
        """
        Uses Gemini to determine the specific topic, general topic, and format
        of the speech based on the transcript and user-provided purpose.
        """
        prompt = (
            "Analyze the following transcript of a speech and identify its core context. "
            f"The user indicated the speech purpose is: '{speech_purpose}'.\n"
            "Provide the output as a JSON object with three keys: 'specific_topic', 'general_topic', and 'format'.\n"
            "Specific topic should be a concise phrase (e.g., 'bioluminescence in squid').\n"
            "General topic should be a broader category (e.g., 'marine biology').\n"
            "Format should describe the speech type (e.g., 'scientific conference presentation', 'persuasive debate', 'casual storytelling', 'job interview pitch').\n"
            "Return ONLY the JSON object. No explanations, no markdown fences.\n\n"
            f"Transcript:\n\"\"\"{self.transcript}\"\"\""
        )
        print("TextEncoder: Calling Gemini for context extraction...")
        response = self._call_generate(prompt)
        raw = response.text or ""
        raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE)

        try:
            self.context = json.loads(raw)
            # Ensure all keys are present, even if empty
            self.context = {
                "specific_topic": self.context.get("specific_topic", ""),
                "general_topic": self.context.get("general_topic", ""),
                "format": self.context.get("format", "")
            }
            return self.context
        except Exception as e:
            print(f"Warning: Failed to parse context JSON from Gemini. Raw output:\n{raw}\nError: {e}")
            return {
                "specific_topic": "unknown",
                "general_topic": "unknown",
                "format": speech_purpose
            }

    def retrieve_examples(self) -> str:
        """
        Searches the web for public speaking examples most closely related to
        the extracted context using Gemini's web search capabilities.
        Prioritizes specific topic and format, falls back to general topic.
        """
        specific_topic = self.context.get("specific_topic")
        general_topic = self.context.get("general_topic")
        speech_format = self.context.get("format")

        search_query = ""
        if specific_topic and specific_topic != "unknown":
            search_query = f"public speaking examples for '{specific_topic}' {speech_format}"
        elif general_topic and general_topic != "unknown":
            search_query = f"public speaking examples for '{general_topic}' {speech_format}"
        else:
            search_query = f"public speaking examples for '{speech_format}'"

        prompt = (
            f"Find compelling examples of public speaking that are highly relevant to the following context:\n"
            f"- Specific Topic: {specific_topic}\n"
            f"- General Topic: {general_topic}\n"
            f"- Format: {speech_format}\n\n"
            "Provide a brief summary (1-2 sentences) of each example and a URL if available. "
            "Prioritize examples that demonstrate excellent delivery for the specified format and topic. "
            "If no very specific examples are found, provide general excellent public speaking examples "
            "relevant to the 'format' or 'general topic'. List 3-5 examples. Present this in a readable, non-JSON format."
            "\n\nSearch Query for Gemini (for context only): " + search_query
        )
        print(f"TextEncoder: Calling Gemini for example retrieval with query: '{search_query}'...")
        try:
            response = self._call_generate(prompt)
            self.examples = response.text
        except Exception as e:
            print(f"Warning: Failed to retrieve examples from Gemini. Error: {e}")
            self.examples = "Could not retrieve specific examples. Focus on general public speaking best practices."
        return self.examples


    def grade_transcript(self, duration: float):
        """Send transcript + metrics to Gemini for rubric scoring."""

        # --- Step 1: compute speaking-length metrics ---
        words = self.transcript.split()
        word_count = len(words)
        words_per_minute = (word_count / (duration / 60.0)) if duration > 0 else 0.0

        # Adjust ideal WPM for non-native speakers or diverse communication styles
        # A slightly slower pace might be more appropriate for clarity
        ideal_min, ideal_max = 100.0, 140.0 # Adjusted from 120-150
        if ideal_min <= words_per_minute <= ideal_max:
            length_score = 1.0
        elif words_per_minute > ideal_max:
            length_score = ideal_max / words_per_minute
        else:
            length_score = words_per_minute / ideal_min

        speaking_length = {
            "word_count": word_count,
            "words_per_minute": words_per_minute,
            "length_score": round(length_score, 2)
        }

        # --- Step 2: build schema ---
        schema = {
            "content_quality": {
                "clarity_score": 0.0,
                "relevance_score": 0.0,
                "example_usage_score": 0.0
            },
            "structure": {
                "logical_flow_score": 0.0,
                "transition_score": 0.0,
                "balance_score": 0.0
            },
            "vocabulary_style": {
                "lexical_richness": 0.0,
                "word_appropriateness": 0.0,
                "repetition_score": 0.0
            },
            "grammar_fluency": {
                "grammar_correctness": 0.0,
                "sentence_fluency": 0.0,
                "filler_word_density": 0.0
            },
            "rhetoric_persuasion": {
                "rhetorical_device_score": 0.0,
                "call_to_action_score": 0.0,
                "emotional_valence": 0.0
            },
            "speaking_length": speaking_length,
            "video_duration_seconds": round(duration, 2)
        }

        # --- Step 3: Gemini call for grading ---
        prompt = (
            "You are a speech-grading assistant, focusing on constructive feedback for individuals "
            "who may have English as a second language, neurodivergence, or low confidence. "
            "Therefore, emphasize clarity, logical flow, and ease of understanding over highly complex vocabulary or advanced rhetorical devices. "
            "Return ONLY valid JSON, following this schema exactly. No explanations, no markdown fences. "
            "Each score should be between 0.0 and 1.0, use decimals up to the hundredths place. "
            "A higher score is better. For repetition_score and filler_word_density, a *lower* raw value is better, "
            "but the score should reflect how *good* the speech is (so low density/repetition should yield high scores).\n\n"
            f"Schema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Transcript:\n\"\"\"{self.transcript}\"\"\""
        )
        print("TextEncoder: Calling Gemini for transcript grading...")
        response = self._call_generate(prompt)

        # --- Step 4: Extract JSON safely ---
        raw = response.text or ""
        raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE)

        try:
            self.scores = json.loads(raw)
            # Ensure filler_word_density and repetition_score are inverted for 'goodness' if necessary
            if 'grammar_fluency' in self.scores and 'filler_word_density' in self.scores['grammar_fluency']:
                # Assuming Gemini returns a density. Invert it for a 'score'
                self.scores['grammar_fluency']['filler_word_density'] = round(1.0 - min(1.0, max(0.0, self.scores['grammar_fluency']['filler_word_density'])), 2)
            if 'vocabulary_style' in self.scores and 'repetition_score' in self.scores['vocabulary_style']:
                # Assuming Gemini returns a repetition metric. Invert it for a 'score'
                self.scores['vocabulary_style']['repetition_score'] = round(1.0 - min(1.0, max(0.0, self.scores['vocabulary_style']['repetition_score'])), 2)


        except Exception as e:
            print(f"Warning: Failed to parse Gemini output as JSON for grading. Raw output:\n{raw}\nError: {e}")
            # Fallback to a default structure to avoid breaking downstream
            self.scores = schema # Return the empty schema

    def _call_generate(self, prompt):
        """Helper to call the generative model in a way that's patch-friendly for tests.

        This will import/configure genai lazily and instantiate a GenerativeModel
        for each call so that test patches on
        `google.generativeai.GenerativeModel.generate_content` take effect.
        """
        _configure_genai_from_env()
        # Try to find a mocked module in sys.modules if the import didn't work
        import sys as _sys
        global genai
        if genai is None and 'google.generativeai' in _sys.modules:
            genai = _sys.modules['google.generativeai']

        if genai is None:
            # As a last resort, try importing; if still unavailable, create a
            # lightweight stub that will raise later when used.
            try:
                import google.generativeai as _genai  # type: ignore
                genai = _genai
            except Exception:
                genai = None

        if genai is None or not hasattr(genai, "GenerativeModel"):
            # Create a dumb object to call so tests that patch the method will
            # still be able to attach to the name via patching the path.
            class _Stub:
                def __init__(self, *a, **k):
                    pass
                def generate_content(self, *a, **k):
                    raise RuntimeError("GenerativeModel not available")
            model = _Stub()
            response = model.generate_content(prompt)
        else:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)

        # Coerce response.text into a real string if possible. Tests commonly
        # use MagicMock for responses; ensure downstream code receives a str.
        text_val = getattr(response, 'text', response)
        if not isinstance(text_val, (str, bytes)):
            try:
                text_val = str(text_val)
            except Exception:
                text_val = ''

        # Return an object with a `.text` attribute that's always a string.
        from types import SimpleNamespace
        return SimpleNamespace(text=text_val)

    def save_to_json(self, output_dir: str = "curr_data") -> str:
        """Save rubric scores and context to a JSON file inside output_dir."""
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"text_analysis.json")
        combined_output = {
            "transcript_scores": self.scores,
            "speech_context": self.context,
            "public_speaking_examples": self.examples,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(combined_output, f, indent=4)
        return out_path

    def encode_and_contextualize(self, transcript_file: str, duration: float, speech_purpose: str, output_dir: str = "curr_data") -> tuple[dict, dict, str]:
        """
        Wrapper: read transcript, extract context, retrieve examples, grade it,
        save JSON in output_dir, return scores, context, and examples.
        """
        self.read_transcript(transcript_file)
        self.context = self.extract_context(speech_purpose)
        self.examples = self.retrieve_examples()
        self.grade_transcript(duration)
        self.save_to_json(output_dir=output_dir)
        return self.scores, self.context, self.examples