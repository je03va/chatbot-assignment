import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from article_qa.conversation import ConversationSession, build_system_prompt
from article_qa.gemini_client import GeminiChatClient
from article_qa.ingest import load_article_text, normalize_articles
from article_qa.tts import TTSEngine


class TestIngest(unittest.TestCase):
    def test_normalize_articles_combines_multiple_strings(self):
        text = normalize_articles(["First article.", "Second article."])
        self.assertIn("First article.", text)
        self.assertIn("Second article.", text)

    def test_load_article_text_supports_pdf_files(self):
        fake_page = MagicMock()
        fake_page.extract_text.return_value = "PDF article text."

        with TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "article.pdf"
            pdf_path.write_bytes(b"%PDF-1.4")

            with patch("pypdf.PdfReader") as mock_reader:
                mock_reader.return_value.pages = [fake_page]
                text = load_article_text([str(pdf_path)])

            self.assertIn("PDF article text.", text)


class TestConversation(unittest.TestCase):
    def test_build_system_prompt_mentions_source_text(self):
        prompt = build_system_prompt("Article text here")
        self.assertIn("Article text here", prompt)
        self.assertIn("only from this source", prompt)

    def test_build_system_prompt_strips_markdown_formatting(self):
        prompt = build_system_prompt("# First article\n\n**Traditional Algorithms Tested:**\n- FCFS\n- Max-Min\n\nRL is proposed.")
        self.assertNotIn("#", prompt)
        self.assertNotIn("**", prompt)
        self.assertNotIn("- FCFS", prompt)
        self.assertIn("First article", prompt)
        self.assertIn("RL is proposed", prompt)

    def test_session_tracks_history(self):
        session = ConversationSession("Article text here")
        session.ask("What is the main point?")
        session.record_answer("The main point is clarity.")
        self.assertEqual(len(session.messages), 2)
        self.assertEqual(session.messages[0]["role"], "user")
        self.assertEqual(session.messages[1]["role"], "assistant")


class TestGeminiClient(unittest.TestCase):
    def test_build_request_includes_system_instruction_and_messages(self):
        client = GeminiChatClient(api_key="demo-key", model="gemini-2.5-flash")
        request = client.build_request("System prompt", [{"role": "user", "content": "Question"}])
        self.assertEqual(request["model"], "gemini-2.5-flash")
        self.assertEqual(request["system_instruction"], "System prompt")
        self.assertEqual(request["contents"][0]["content"], "Question")

    def test_default_model_uses_env_override(self):
        with patch.dict("os.environ", {"GEMINI_MODEL": "gemini-3.6-flash"}, clear=False):
            client = GeminiChatClient(api_key="demo-key")
        self.assertEqual(client.model, "gemini-3.6-flash")


class TestTTSEngine(unittest.TestCase):
    def test_synthesizer_callable_is_used(self):
        engine = TTSEngine(synthesizer=lambda text: text.encode("utf-8"))
        payload = engine.synthesize("hello")
        self.assertEqual(payload, b"hello")

    @patch("article_qa.tts.subprocess.run")
    @patch("article_qa.tts.shutil.which")
    @patch("article_qa.tts.platform.system", return_value="Darwin")
    def test_play_uses_system_player(self, mock_system, mock_which, mock_run):
        mock_which.return_value = "/usr/bin/afplay"

        with patch("article_qa.tts.tempfile.NamedTemporaryFile") as mock_tempfile:
            handle = MagicMock()
            handle.__enter__.return_value = handle
            handle.name = "/tmp/output.mp3"
            mock_tempfile.return_value = handle

            with patch("article_qa.tts.os.unlink"):
                TTSEngine().play(b"audio-bytes")

        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args.args[0][0], "afplay")


if __name__ == "__main__":
    unittest.main()
