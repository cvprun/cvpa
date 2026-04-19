# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.apps.agent.token import parse_agent_token


class ParseAgentTokenTestCase(TestCase):
    def test_valid(self):
        slug, token = parse_agent_token("cvp_abc123_myslug")
        self.assertEqual(slug, "myslug")
        self.assertEqual(token, "cvp_abc123")

    def test_slug_contains_underscores(self):
        slug, token = parse_agent_token("cvp_deadbeef_slug_with_parts")
        self.assertEqual(slug, "slug_with_parts")
        self.assertEqual(token, "cvp_deadbeef")

    def test_missing_prefix(self):
        with self.assertRaises(ValueError):
            parse_agent_token("abc123_myslug")

    def test_missing_separator(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp_onlyhex")

    def test_empty_hex(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp__myslug")

    def test_empty_slug(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp_abc123_")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            parse_agent_token("")


if __name__ == "__main__":
    main()
