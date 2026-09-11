import unittest

from article_qa.conversation import ConversationSession, build_system_prompt
from article_qa.gemini_client import GeminiChatClient
from article_qa.ingest import normalize_articles
from article_qa.tts import TTSEngine


class TestIngest(unittest.TestCase):
    def test_normalize_articles_combines_multiple_strings(self):
        text = normalize_articles(["First article.", "Second article."])
        self.assertIn("First article.", text)
        self.assertIn("Second article.", text)


class TestConversation(unittest.TestCase):
    def test_build_system_prompt_mentions_source_text(self):
        prompt = build_system_prompt("Article text here")
        self.assertIn("Article text here", prompt)
        self.assertIn("only from this source", prompt)

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


class TestTTSEngine(unittest.TestCase):
    def test_synthesizer_callable_is_used(self):
        engine = TTSEngine(synthesizer=lambda text: text.encode("utf-8"))
        payload = engine.synthesize("hello")
        self.assertEqual(payload, b"hello")


if __name__ == "__main__":
    unittest.main()
