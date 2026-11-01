# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from community_platform.points import clear_total


class PointLedger(Document):
	def on_update(self):
		clear_total(self.contributor)

	def on_trash(self):
		clear_total(self.contributor)
