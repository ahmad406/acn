# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerProcess(Document):
	def validate(self):
		self.create_item()

	def create_item(self):
		if not  frappe.db.exists("Item", self.item_code):
			stock=frappe.get_single("Stock Settings")
			item = frappe.new_doc("Item")
			item.item_code = self.item_code
			item.item_name = self.item_code
			item.item_group = stock.item_group
			item.stock_uom = stock.stock_uom
			item.save()


