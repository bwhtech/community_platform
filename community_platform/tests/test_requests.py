import frappe
from frappe.tests import IntegrationTestCase

from community_platform import points
from community_platform.api import requests
from community_platform.tests.helpers import make_contributor, make_user

DESCRIPTION = "A description that is long enough to pass validation."


class TestFeatureRequests(IntegrationTestCase):
	def setUp(self):
		self.author = make_contributor("test-author", make_user("author@example.com"))
		self.voter = make_contributor("test-voter", make_user("voter@example.com"))
		frappe.set_user("author@example.com")
		self.request_id = requests.create_request("A sensible request", DESCRIPTION, "frappe")

	def tearDown(self):
		frappe.set_user("Administrator")
		# IntegrationTestCase only rolls back once per class.
		frappe.db.rollback()

	def as_voter(self):
		frappe.set_user("voter@example.com")

	def test_author_upvote_is_automatic_and_earns_nothing(self):
		request = requests.get_request(self.request_id)
		self.assertEqual(request["upvotes"], 1)
		self.assertTrue(request["isMine"])
		self.assertEqual(points.total_for(self.author), 0)

	def test_upvote_awards_point_and_withdraw_revokes_it(self):
		self.as_voter()
		requests.toggle_upvote(self.request_id)
		self.assertEqual(points.total_for(self.author), 1)
		self.assertTrue(requests.get_request(self.request_id)["upvoted"])
		requests.toggle_upvote(self.request_id)
		self.assertEqual(points.total_for(self.author), 0)
		self.assertFalse(requests.get_request(self.request_id)["upvoted"])

	def test_author_cannot_delete_after_others_upvote(self):
		self.as_voter()
		requests.toggle_upvote(self.request_id)
		frappe.set_user("author@example.com")
		self.assertRaises(frappe.PermissionError, requests.delete_request, self.request_id)

	def test_only_moderators_can_hide(self):
		self.as_voter()
		self.assertRaises(frappe.PermissionError, requests.set_hidden, self.request_id, True)

	def test_hiding_revokes_upvote_points(self):
		self.as_voter()
		requests.toggle_upvote(self.request_id)
		frappe.set_user("Administrator")
		requests.set_hidden(self.request_id, True)
		self.assertEqual(points.total_for(self.author), 0)

	def test_reaction_toggles(self):
		self.as_voter()
		requests.toggle_reaction(self.request_id, "🚀")
		mine = [r for r in requests.get_request(self.request_id)["reactions"] if r["mine"]]
		self.assertEqual([r["emoji"] for r in mine], ["🚀"])
		requests.toggle_reaction(self.request_id, "🚀")
		self.assertFalse([r for r in requests.get_request(self.request_id)["reactions"] if r["mine"]])

	def test_guests_cannot_upvote(self):
		frappe.set_user("Guest")
		self.assertRaises(frappe.PermissionError, requests.toggle_upvote, self.request_id)
