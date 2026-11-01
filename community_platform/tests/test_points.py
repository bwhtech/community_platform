import frappe
from frappe.tests import IntegrationTestCase

from community_platform import points
from community_platform.ranking import rank_contributors
from community_platform.tests.helpers import make_contributor


class TestPoints(IntegrationTestCase):
	def setUp(self):
		self.alice = make_contributor("test-alice")
		self.bob = make_contributor("test-bob")

	def tearDown(self):
		# IntegrationTestCase only rolls back once per class.
		frappe.db.rollback()

	def award_pr(self, login, number, day="2026-10-10"):
		return points.award(
			login, "github_pr_merged", external_id=f"frappe/frappe#{number}", title="PR", event_date=day
		)

	def test_award_uses_rule_points_and_updates_total(self):
		row = self.award_pr(self.alice, 1)
		self.assertEqual(frappe.get_doc("Contributor", self.alice).total_points, 20)
		points.revoke(row, "spam")
		self.assertEqual(frappe.get_doc("Contributor", self.alice).total_points, 0)

	def test_contributor_needs_a_user(self):
		with self.assertRaises(frappe.MandatoryError):
			frappe.get_doc({"doctype": "Contributor", "github_login": "test-nouser"}).insert()

	def test_duplicate_activity_is_ignored(self):
		self.assertTrue(self.award_pr(self.alice, 2))
		self.assertIsNone(self.award_pr(self.alice, 2))

	def test_rule_change_does_not_touch_past_rows(self):
		self.award_pr(self.alice, 3)
		frappe.db.set_value("Point Rule", "github_pr_merged", "points", 99)
		self.award_pr(self.alice, 4)
		self.assertEqual(points.total_for(self.alice), 20 + 99)

	def test_revoke_adds_negative_row_once(self):
		row = self.award_pr(self.alice, 5)
		self.assertTrue(points.revoke(row, "spam"))
		self.assertIsNone(points.revoke(row, "again"))
		self.assertEqual(points.total_for(self.alice), 0)
		# A revoked activity can be earned again, e.g. a re-upvote.
		self.assertTrue(self.award_pr(self.alice, 5))

	def test_cap_limits_points_per_item(self):
		frappe.db.set_value("Point Rule", "request_upvote_received", "cap_per_target", 2)
		for voter in range(3):
			points.award(
				self.alice,
				"request_upvote_received",
				external_id=f"fr:1:v{voter}",
				cap_target="fr:1",
				title="Request",
				event_date="2026-10-10",
			)
		self.assertEqual(points.total_for(self.alice), 2)

	def test_disabled_rule_awards_nothing(self):
		frappe.db.set_value("Point Rule", "github_pr_merged", "enabled", 0)
		self.assertIsNone(self.award_pr(self.alice, 6))

	def test_first_merge_badge_is_awarded_and_kept(self):
		row = self.award_pr(self.alice, 7)
		badge = frappe.db.get_value("Badge", {"title": "First merge"})
		self.assertTrue(frappe.db.exists("Contributor Badge", {"contributor": self.alice, "badge": badge}))
		points.revoke(row, "reverted")
		self.assertTrue(frappe.db.exists("Contributor Badge", {"contributor": self.alice, "badge": badge}))

	def test_ranking_breaks_ties_by_who_got_there_first(self):
		self.award_pr(self.alice, 8, day="2026-10-05")
		self.award_pr(self.bob, 9, day="2026-10-02")
		ranked = [
			r["login"] for r in rank_contributors(month="2026-10") if r["login"] in (self.alice, self.bob)
		]
		self.assertEqual(ranked, [self.bob, self.alice])
