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
			item.item_group = "Customer item"
			item.stock_uom = stock.stock_uom
			item.save()

	@frappe.whitelist()
	def fetch_customer_process_template(self):
		if self.customer_process_template:
			doc = frappe.get_doc("Customer Process template", self.customer_process_template)
			self.set("customer_requirements",[])
			self.set("sequence_lot_wise_internal_process",[])
			self.set("parameters_with_acceptance_criteria",[])

			for c in  doc.customer_requirements:
				row_c=self.append("customer_requirements", {})
				row_c.process_parameter=c.process_parameter
				row_c.maximum_value=c.maximum_value
				row_c.minimum_value=c.minimum_value
				row_c.scale=c.scale
				row_c.microstructure_cutoff=c.microstructure_cutoff
			for s in doc.sequence_lot_wise_internal_process:
				row_s=self.append("sequence_lot_wise_internal_process", {})
				row_s.furnace_process=s.furnace_process
				row_s.internal_process=s.internal_process
				row_s.lot_no=s.lot_no
				row_s.media=s.media
			for p in doc.parameters_with_acceptance_criteria:
				row_p=self.append("parameters_with_acceptance_criteria", {})
				row_p.lot_no=p.lot_no
				row_p.internal_process=p.internal_process
				row_p.control_parameter=p.control_parameter
				row_p.minimum_value=p.minimum_value
				row_p.maximum_value=p.maximum_value
				row_p.scale=p.scale
				row_p.microstructure_cutoff=p.microstructure_cutoff
				row_p.information=p.information



		return True


