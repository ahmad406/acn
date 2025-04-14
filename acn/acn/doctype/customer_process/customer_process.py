# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class CustomerProcess(Document):
	def validate(self):
		self.create_item()
		self.set_title()
		self.validate_duplicate()
		self.create_part_no()

	def create_part_no(self):
		for d in self.part_no__process_rate:
			if  d.part_no:
				if not frappe.db.exists("Part no", d.part_no):
					part_no = frappe.new_doc("Part no")
					part_no.part_no = d.part_no
					part_no.customer= self.customer
					part_no.save()


	def validate_duplicate(self):
		duplicate_exists = frappe.db.exists('Customer Process', {
        'customer': self.customer,
        'process_type': self.process_type,
        'item_code': self.item_code,
        'customer_ref': self.customer_ref,
        'name': ['!=', self.name]  
    })
    
		if duplicate_exists:
			frappe.throw(_('Duplicate entry found: Customer, Process Type, Item Code, and Customer Process Ref. No. combination must be unique.'))



	def set_title(self):
		self.title_data = "{0}-{1}-{2}-{3}".format(self.customer, self.process_type,self.item_code,self.customer_ref)
	def create_item(self):
		if not  frappe.db.exists("Item", self.item_code):
			stock=frappe.get_single("Stock Settings")
			item = frappe.new_doc("Item")
			item.item_code = self.item_code
			item.item_name = self.item_name
			item.item_group = "Customer item"
			item.is_stock_item=0
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


