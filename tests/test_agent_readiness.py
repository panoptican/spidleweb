import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.body_depth = 0
        self.ignored_depth = 0
        self.headings = []
        self._heading = None
        self._heading_text = []
        self.body_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.body_depth += 1
        if tag in {"script", "style", "template"}:
            self.ignored_depth += 1
        if self.body_depth and self.ignored_depth == 0 and re.fullmatch(r"h[1-6]", tag):
            self._heading = tag
            self._heading_text = []

    def handle_endtag(self, tag):
        if self._heading == tag:
            self.headings.append((int(tag[1]), " ".join(self._heading_text).strip()))
            self._heading = None
            self._heading_text = []
        if tag in {"script", "style", "template"} and self.ignored_depth:
            self.ignored_depth -= 1
        if tag == "body" and self.body_depth:
            self.body_depth -= 1

    def handle_data(self, data):
        if not self.body_depth or self.ignored_depth:
            return
        self.body_text.append(data)
        if self._heading is not None:
            self._heading_text.append(data)


class AgentReadinessTests(unittest.TestCase):
    def test_homepage_has_meaningful_raw_html_and_sequential_headings(self):
        parser = HomepageParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        body_text = " ".join(" ".join(parser.body_text).split())

        self.assertGreaterEqual(len(body_text), 500)
        h1s = [" ".join(text.split()) for level, text in parser.headings if level == 1]
        self.assertEqual(len(h1s), 1)
        self.assertIn("Jason Spidle", h1s[0])
        self.assertIn("Principal Product Designer", h1s[0])

        levels = [level for level, _ in parser.headings]
        self.assertTrue(all(current <= previous + 1 for previous, current in zip(levels, levels[1:])))

    def test_openapi_describes_public_document_endpoints(self):
        document = json.loads((ROOT / "openapi.json").read_text(encoding="utf-8"))

        self.assertEqual(document["openapi"], "3.1.1")
        self.assertEqual(document["servers"], [{"url": "https://spidleweb.net"}])
        expected_paths = {
            "/",
            "/work/expert-insights",
            "/work/campaign-sim",
            "/work/everag",
            "/work/vidscrip",
            "/work/conservis",
            "/work/plinth",
            "/robots.txt",
            "/sitemap.xml",
            "/openapi.json",
            "/.well-known/oauth-protected-resource",
        }
        self.assertTrue(expected_paths.issubset(document["paths"]))
        for path, item in document["paths"].items():
            self.assertIn("get", item, path)
            self.assertIn("200", item["get"]["responses"], path)

    def test_protected_resource_metadata_declares_read_scope(self):
        metadata = json.loads(
            (ROOT / ".well-known/oauth-protected-resource").read_text(encoding="utf-8")
        )

        self.assertEqual(metadata["resource"], "https://spidleweb.net")
        self.assertEqual(metadata["scopes_supported"], ["site:read"])
        self.assertEqual(metadata["bearer_methods_supported"], [])

    def test_cloudflare_headers_and_agent_runbook_cover_machine_access(self):
        headers = (ROOT / "_headers").read_text(encoding="utf-8")
        self.assertIn('rel="service-desc"', headers)
        self.assertIn("Content-Type: application/json; charset=utf-8", headers)

        runbook = (ROOT / "docs/agents/agent-access.md").read_text(encoding="utf-8")
        for user_agent in (
            "ChatGPT-User",
            "ClaudeBot",
            "Google-Extended",
            "DeepSeekBot",
            "ora-agent",
            "GPTBot",
            "PerplexityBot",
            "Applebot-Extended",
        ):
            self.assertIn(user_agent, runbook)


if __name__ == "__main__":
    unittest.main()
