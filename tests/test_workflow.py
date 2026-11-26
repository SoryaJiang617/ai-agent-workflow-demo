import io
import os
import sys
import unittest
from unittest.mock import Mock, patch

from main import main, run_agent_workflow
from services import openai_client


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        # Patch where each role looks up the shared model boundary.
        self.planner = self.patch("agents.planner.ask_gpt")
        self.worker = self.patch("agents.worker.ask_gpt")
        self.reviewer = self.patch("agents.reviewer.ask_gpt")
        self.output = self.patch("sys.stdout", new_callable=io.StringIO)

    def patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def test_simple_request_takes_three_model_calls(self):
        request = "Write an English email about a two-day delay in at most 100 words."
        self.planner.return_value = '["Draft the delay email"]'
        self.worker.return_value = "First draft for the customer."
        self.reviewer.return_value = "Your order will arrive two days later than expected."

        self.assertEqual(run_agent_workflow(request), self.reviewer.return_value)

        self.planner.assert_called_once()
        self.worker.assert_called_once()
        self.reviewer.assert_called_once()
        for role in (self.planner, self.worker, self.reviewer):
            self.assertIn(request, role.call_args.args[1])
        self.assertIn("Draft the delay email", self.worker.call_args.args[1])
        self.assertIn(self.worker.return_value, self.reviewer.call_args.args[1])
        self.assertIn("whitespace-separated words): 5", self.reviewer.call_args.args[1])

    def test_each_step_receives_original_request_and_latest_output(self):
        request = "Plan a weekend promotion for a coffee shop on a $200 budget."
        self.planner.return_value = '["Choose an audience", "Design an offer"]'
        self.worker.side_effect = ["Audience: nearby students.", "Offer: student discount."]
        self.reviewer.return_value = "Run a student discount this weekend."

        self.assertEqual(run_agent_workflow(request), self.reviewer.return_value)

        self.assertEqual(self.worker.call_count, 2)
        first, second = (call.args[1] for call in self.worker.call_args_list)
        self.assertIn("Choose an audience", first)
        self.assertIn("Design an offer", second)
        self.assertIn("Audience: nearby students.", second)
        self.reviewer.assert_called_once()
        review = self.reviewer.call_args.args[1]
        self.assertIn("Offer: student discount.", review)
        for prompt in (first, second, review):
            self.assertIn(request, prompt)
        self.assertLess(self.output.getvalue().index("2. Design an offer"),
                        self.output.getvalue().index("Running step 1"))

    def test_blank_input_stops_before_any_model_call(self):
        with self.assertRaises(ValueError):
            run_agent_workflow("  \t ")
        for role in (self.planner, self.worker, self.reviewer):
            role.assert_not_called()

    def test_cli_counts_the_reviewed_email_including_its_subject(self):
        self.patch("builtins.input", return_value="Draft an email under 100 words.")
        self.planner.return_value = '["Write the email"]'
        self.worker.return_value = "Draft " * 105
        self.reviewer.return_value = "Subject: Order update\n\nYour delivery is delayed."
        self.assertEqual(main(), 0)
        self.assertIn("whitespace-separated words): 105", self.reviewer.call_args.args[1])
        self.assertIn(self.reviewer.return_value, self.output.getvalue())
        self.assertIn("Word count (whitespace-separated): 7", self.output.getvalue())

    def test_invalid_plans_stop_before_execution(self):
        bad_plans = (
            "invalid JSON",
            '{"steps": ["draft"]}',
            "[]",
            '["  "]',
            '["draft", 5]',
            '["one", "two", "three", "four"]',
        )
        for plan in bad_plans:
            with self.subTest(plan=plan):
                self.planner.reset_mock()
                self.planner.return_value = plan
                with self.assertRaisesRegex(RuntimeError, "(?i)planning"):
                    run_agent_workflow("Draft an email.")
                self.planner.assert_called_once()
                self.worker.assert_not_called()
                self.reviewer.assert_not_called()

    def test_worker_failure_skips_remaining_steps_and_review(self):
        self.planner.return_value = '["List constraints", "Draft an email", "Add a subject"]'
        self.worker.side_effect = ["Constraints identified.", RuntimeError("Request timed out")]

        with self.assertRaisesRegex(RuntimeError, "Execution step 2 failed: Request timed out"):
            run_agent_workflow("Draft an email.")

        self.assertEqual(self.worker.call_count, 2)
        self.reviewer.assert_not_called()

    def test_reviewer_failure_identifies_review_stage(self):
        self.planner.return_value = '["Draft an email"]'
        self.worker.return_value = "An email draft."
        self.reviewer.side_effect = RuntimeError("Rate limit reached")

        with self.assertRaisesRegex(RuntimeError, "(?i)review"):
            run_agent_workflow("Draft an email.")
        self.reviewer.assert_called_once()


class ModelClientTests(unittest.TestCase):
    def setUp(self):
        # Stand-ins for the SDK and .env loader keep even the client tests offline.
        self.sdk = Mock()
        modules = patch.dict(sys.modules, {"openai": self.sdk, "dotenv": Mock()})
        modules.start()
        self.addCleanup(modules.stop)
        openai_client._get_client.cache_clear()
        self.addCleanup(openai_client._get_client.cache_clear)

    def test_missing_key_has_actionable_message(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
                openai_client.ask_gpt("system", "request")
        self.sdk.OpenAI.assert_not_called()

    def test_empty_model_response_is_reported(self):
        create = self.sdk.OpenAI.return_value.chat.completions.create
        for choices in ([], [Mock(message=Mock(content="   "))]):
            with self.subTest(choices=choices), patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}):
                create.reset_mock()
                create.return_value.choices = choices
                with self.assertRaisesRegex(RuntimeError, "empty response"):
                    openai_client.ask_gpt("system", "request")
                create.assert_called_once()

    def test_authentication_failure_stops_after_one_request(self):
        self.sdk.AuthenticationError = PermissionError
        create = self.sdk.OpenAI.return_value.chat.completions.create
        create.side_effect = PermissionError("Invalid credential")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}):
            with self.assertRaisesRegex(RuntimeError, "rejected the API key"):
                openai_client.ask_gpt("system", "request")
        self.assertEqual(self.sdk.OpenAI.call_args.kwargs["max_retries"], 0)
        create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
