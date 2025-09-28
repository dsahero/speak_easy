import os
import json
from datetime import datetime
from typing import List, Union, Dict, Any
import re
import torch
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*a, **k):
        return False

# Try to import the optional Google Generative AI client. During unit tests
# the test harness injects a mock into sys.modules['google.generativeai']
# before importing this module. Guard the import so tests can run without
# the real package installed.
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    raise ImportError("google.generativeai package not found. Install it before continuing.")

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
    print("configure_genai_from_env worked. genai is", "configured" if genai is not None else "not available")


class TextEncoder:
    """
    A text encoder that processes transcripts, extracts context,
    finds public speaking examples, and produces rubric scores.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", device: str = "cpu"):
        self.device = device
        # Store model name and defer creating model instances until call-time so
        # unit tests can patch `google.generativeai.GenerativeModel.generate_content`.
        self.model_name = model_name
        self.model = None
        self.transcript = ""
        self.scores = {}
        self.context = {}
        self.examples = {} # Store raw text examples or URLs
        print(f"TextEncoder initialized with model {model_name} on device {device}")

    def __call__(self, texts: Union[str, List[str]]) -> torch.Tensor:
        """Allow batch calls returning dummy tensors."""
        if isinstance(texts, str):
            batch = [texts]
        elif isinstance(texts, (list, tuple)):
            batch = texts
        else:
            raise ValueError("Input to TextEncoder must be str or list of str")
        print(f"TextEncoder: Encoding dummy features for batch of size {len(batch)}")
        return torch.zeros(len(batch), self.feat_dim, device=self.device)

    def read_transcript(self, transcript_file: str):
        """Load transcript text from a file."""
        try:
            with open(transcript_file, "r", encoding="utf-8") as f:
                self.transcript = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Transcript file not found: {transcript_file}")
        print(f"TextEncoder: Loaded transcript from {transcript_file}, length {len(self.transcript)} characters")

    def extract_context(self, speech_purpose: str):
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
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE)

        try:
            self.context = json.loads(raw)
            # Ensure all keys are present, even if empty
            self.context = {
                "specific_topic": self.context.get("specific_topic", ""),
                "general_topic": self.context.get("general_topic", ""),
                "format": self.context.get("format", "")
            }
        except Exception as e:
            print(f"Warning: Failed to parse context JSON from Gemini. Raw output:\n{raw}\nError: {e}")
            return {
                "specific_topic": "unknown",
                "general_topic": "unknown",
                "format": speech_purpose
            }
        print(f"TextEncoder: Extracted context: {self.context}")

    def retrieve_examples(self):
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

        json_schema = {
            "examples": [
                {
                    "title": "string",
                    "summary": "string",
                    "url": "string",
                    "relevance": ["string", "string"]
                }
            ]
        }

        print(f"TextEncoder: Building prompt for example retrieval with search query: '{search_query}'")


        prompt = (
            f"Find compelling examples of public speaking that are highly relevant to the following context:\n"
            f"- Specific Topic: {specific_topic}\n"
            f"- General Topic: {general_topic}\n"
            f"- Format: {speech_format}\n\n"
            "Provide exactly 3 examples in JSON format following this schema:\n"
            f"{json.dumps(json_schema, indent=2)}\n\n"
            "Rules:\n"
            "- Each 'summary' should be 2-3 sentences.\n"
            "- Each 'relevance' field should contain 2-3 bullet points explaining why the example was chosen.\n"
            "- If no very specific examples are found, provide general excellent public speaking examples relevant to the format or general topic.\n"
            "- Return ONLY valid JSON. No explanations, no markdown fences.\n\n"
            f"Search Query for Gemini (for context only): {search_query}"
        )
        print(f"TextEncoder: Calling Gemini for example retrieval with query: '{search_query}'...")
        try:
            # Step 4 — Call Gemini
            response = self._call_generate(prompt)
            raw_output = response.text or ""

            # Step 5 — Attempt to parse JSON safely
            try:
                examples = json.loads(raw_output.strip())
            except json.JSONDecodeError:
                print("Warning: Gemini output is not valid JSON. Wrapping raw output.")
                examples = {"examples": [{"title": "Parsing error", "summary": raw_output, "url": "", "relevance": []}]}

            self.examples = examples

        except Exception as e:
            print(f"Warning: Failed to retrieve examples from Gemini. Error: {e}")
            self.examples = {
                "examples": [
                    {
                        "title": "General Public Speaking Best Practices",
                        "summary": "Fallback advice since no examples were retrieved.",
                        "url": "",
                        "relevance": ["Focus on clarity", "Engage the audience", "Practice pacing"]
                    }
                ]
            }
            print(f"TextEncoder: Using fallback examples: {self.examples}")


    def grade_transcript(self, word_count, words_per_minute):
        """Send transcript + metrics to Gemini for rubric scoring."""

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
            "video_duration_seconds": round((word_count / words_per_minute) * 60, 2),
            "word_count": word_count,
            "words_per_minute": words_per_minute
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

        # If a concrete model instance was assigned to the encoder (tests do
        # this), prefer calling it directly. This avoids picking up the
        # global genai.GenerativeModel mock in sys.modules which may retain
        # side effects across tests.
        if getattr(self, 'model', None) is not None:
            response = self.model.generate_content(prompt)
            # Coerce to object with .text below
            text_val = getattr(response, 'text', response)
            if not isinstance(text_val, (str, bytes)):
                try:
                    text_val = str(text_val)
                except Exception:
                    text_val = ''
            from types import SimpleNamespace
            return SimpleNamespace(text=text_val)
        
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


    def encode_and_contextualize(self, transcript_file, word_count, words_per_minute, speech_purpose) -> tuple[dict, dict, str]:
        """
        Wrapper: read transcript, extract context, retrieve examples, grade it, return scores, context, and examples.
        """
        self.read_transcript(transcript_file)
        self.extract_context(speech_purpose)
        self.retrieve_examples()
        self.grade_transcript(word_count, words_per_minute)
        return self.scores, self.context, self.examples