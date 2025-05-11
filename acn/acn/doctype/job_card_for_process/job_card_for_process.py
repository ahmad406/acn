# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class JobCardforprocess(Document):
	def validate(self):
		for d  in self.sequence_lot_wise_internal_process:
			if d.idx==1:
				d.balance_qty_in_nos=self.qty_in_nos
				d.balance_qty_in_kgs=self.qty_in_kgs
