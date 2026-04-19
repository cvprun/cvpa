# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.apps.agent.token import parse_agent_token


class ParseAgentTokenTestCase(TestCase):
    def test_valid(self):
        slug, token = parse_agent_token("cvp_myslug_mytoken")
        self.assertEqual(slug, "myslug")
        self.assertEqual(token, "mytoken")

    def test_token_contains_underscores(self):
        slug, token = parse_agent_token("cvp_myslug_tok_en_parts")
        self.assertEqual(slug, "myslug")
        self.assertEqual(token, "tok_en_parts")

    def test_missing_prefix(self):
        with self.assertRaises(ValueError):
            parse_agent_token("myslug_mytoken")

    def test_missing_separator(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp_onlyslug")

    def test_empty_slug(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp__mytoken")

    def test_empty_token(self):
        with self.assertRaises(ValueError):
            parse_agent_token("cvp_myslug_")

    def test_empty_string(self):
        with self.assertRaises(ValueError):
            parse_agent_token("")


if __name__ == "__main__":
    main()
