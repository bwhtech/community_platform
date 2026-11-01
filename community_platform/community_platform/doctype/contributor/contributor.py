# Copyright (c) 2026, BWH and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from community_platform.points import cached_total


class Contributor(Document):
	@property
	def total_points(self) -> int:
		return cached_total(self.name)
