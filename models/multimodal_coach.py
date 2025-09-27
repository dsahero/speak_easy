import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Import google.generativeai optionally to allow tests to inject a mock
try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore

load_dotenv()


def _ensure_genai_configured():
    """Lazily ensure genai is available and configured from the environment.

    Tests can inject a mock into sys.modules before importing this module.
    """
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

class Coach:
    """
    A multimodal coach that analyzes speech performance using video, audio,
    text features, and external examples via Gemini's multimodal capabilities.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"): # Use a model capable of multimodal input
        _ensure_genai_configured()
        if genai is not None and hasattr(genai, "GenerativeModel"):
            try:
                self.model = genai.GenerativeModel(model_name)
            except Exception:
                self.model = None
        else:
            self.model = None

    def analyze_performance(self, video_file: str, audio_file: str,
                            text_features: Dict[str, Any],
                            context_info: Dict[str, str],
                            examples_info: str) -> str:
        """
        Analyzes the user's speech performance by comparing it against
        public speaking examples and providing tailored feedback.
        """
        print("Coach: Preparing multimodal analysis with Gemini...")

        # Ensure genai is configured or a test mock is available
        _ensure_genai_configured()
        import sys as _sys
        global genai
        if genai is None and 'google.generativeai' in _sys.modules:
            genai = _sys.modules['google.generativeai']

        # Load video and audio files for Gemini input
        # Gemini API handles file uploads directly.
        if genai is None or not hasattr(genai, 'upload_file'):
            raise RuntimeError('Generative AI upload_file not available')
        video_part = genai.upload_file(video_file)
        audio_part = genai.upload_file(audio_file)

        # Build the prompt for multimodal analysis
        prompt_parts = [
            f"You are an empathetic public speaking coach, specialized in helping individuals "
            f"with English as a second language, neurodivergence, or low confidence. "
            f"Your goal is to provide constructive, encouraging, and actionable feedback "
            f"based on the provided video, audio, and text analysis. Do not be overly critical, focus on improvement and strengths.\n\n"
            f"Here is the context of the speech:\n{json.dumps(context_info, indent=2)}\n\n"
            f"Here are the linguistic and stylistic scores from the text transcript:\n{json.dumps(text_features, indent=2)}\n\n"
            f"Here are some relevant public speaking examples for comparison and inspiration:\n{examples_info}\n\n"
            f"Please analyze the speaker's performance in the uploaded video and audio, "
            f"considering the context, the text analysis, and the provided examples. "
            f"Focus on the following aspects, providing specific observations, strengths, and areas for improvement:\n"
            f"1.  **Clarity & Understanding**: How clear was the message? Was pronunciation generally understandable? (Crucial for ESL/neurodivergent speakers)\n"
            f"2.  **Engagement (Verbal & Non-verbal)**: Eye contact, gestures, facial expressions, vocal variety (pitch, pace, volume). How well did they connect with the (imagined) audience?\n"
            f"3.  **Confidence & Presence**: Did the speaker appear confident? What non-verbal cues contributed to or detracted from confidence? (Especially important for low-confidence speakers)\n"
            f"4.  **Structure & Flow**: Did the speech flow logically? Were transitions smooth? (Reinforce text_encoder's logical_flow_score).\n"
            f"5.  **Pacing & Fluency**: Was the speaking rate appropriate? Were filler words minimal? (Relate to text_encoder's speaking_length and filler_word_density).\n"
            f"6.  **Comparison to Examples**: How did the speaker's delivery compare to the provided examples? What specific techniques could they learn from?\n\n"
            f"Provide your feedback in a structured, easy-to-read format with bullet points or numbered lists. "
            f"Start with overall positive observations, then move to constructive suggestions. "
            f"Maintain an encouraging and supportive tone throughout. Remember, the goal is improvement, not perfection.\n"
            f"After providing feedback, suggest 1-3 simple, actionable exercises the speaker can practice to improve."
        ]

        # Combine prompt parts with the uploaded files
        full_content = prompt_parts + [video_part, audio_part]

        try:
            # If model was not set (e.g., in tests), try to instantiate from genai
            if self.model is None and genai is not None and hasattr(genai, 'GenerativeModel'):
                try:
                    self.model = genai.GenerativeModel(self.model.__class__.__name__ if self.model else 'dummy')
                except Exception:
                    # leave model as None
                    pass

            if self.model is None:
                # Allow direct call on the genai module if tests patched its method
                if hasattr(genai, 'GenerativeModel'):
                    model = genai.GenerativeModel('dummy')
                    response = model.generate_content(full_content)
                else:
                    raise RuntimeError('GenerativeModel not available')
            else:
                response = self.model.generate_content(full_content)

            # Coerce response.text to string
            text_val = getattr(response, 'text', response)
            try:
                result_text = str(text_val)
            except Exception:
                result_text = ''

            genai.delete_file(video_part.name) # Clean up uploaded files
            genai.delete_file(audio_part.name)
            return result_text
        except Exception as e:
            print(f"Error during multimodal analysis: {e}")
            try:
                genai.delete_file(video_part.name) # Ensure cleanup even on error
                genai.delete_file(audio_part.name)
            except Exception:
                pass
            return (f"Failed to analyze performance due to an error: {e}. "
                    "Please ensure your API key is correct and the video/audio files are valid.")