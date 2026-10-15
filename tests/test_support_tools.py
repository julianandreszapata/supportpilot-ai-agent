import unittest

from support_tools import (
    create_compensation_request,
    execute_tool,
    get_order_status,
    search_support_policy,
    transfer_to_human,
)


class SupportToolsTests(unittest.TestCase):
    def test_returns_known_order(self):
        result = get_order_status("dm-1002")
        self.assertEqual(result["status"], "found")
        self.assertEqual(result["order"]["status"], "Entregado con demora")

    def test_unknown_order_is_not_found(self):
        self.assertEqual(get_order_status("DM-9999")["status"], "not_found")

    def test_policy_search_finds_delay_policy(self):
        result = search_support_policy("Mi pedido llegó tarde y con demora")
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["matches"][0]["id"], "POL-01")

    def test_no_policy_recommends_human_review(self):
        result = search_support_policy("necesito algo que no está documentado")
        self.assertEqual(result["status"], "no_match")
        self.assertTrue(result["human_review"])

    def test_compensation_is_pending_and_never_financial(self):
        result = create_compensation_request("DM-1002", "Demora", sequence=3)
        self.assertEqual(result["status"], "pending_human_review")
        self.assertFalse(result["financial_action_executed"])

    def test_compensation_rejects_unknown_order(self):
        result = create_compensation_request("DM-9999", "Demora")
        self.assertEqual(result["status"], "not_created")

    def test_handoff_creates_simulated_ticket(self):
        result = transfer_to_human("El usuario lo solicita", "DM-1002", sequence=2)
        self.assertEqual(result["ticket_id"], "HUM-0002")
        self.assertIn("simulado", result["message"])

    def test_unknown_tool_is_rejected(self):
        result = execute_tool("delete_database", {}, sequence=1)
        self.assertEqual(result["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
