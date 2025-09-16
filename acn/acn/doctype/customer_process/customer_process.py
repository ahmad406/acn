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
					part_no.image=d.part_image
					part_no.save()
	def validate_duplicate(self):
		for row in self.get("part_no__process_rate"):
			duplicates_in_doc = [r.part_no for r in self.get("part_no__process_rate") if r.part_no == row.part_no]
			if len(duplicates_in_doc) > 1:
				frappe.throw(_('Duplicate Part No. "{0}" found in this Customer Process.').format(row.part_no))

			duplicate_exists = frappe.db.sql("""
				SELECT 1
				FROM `tabCustomer Process` cp
				INNER JOIN `tabCustomer Process Item` cpi ON cpi.parent = cp.name
				WHERE cp.customer = %s
				AND cp.process_type = %s
				AND cp.item_code = %s
				AND cpi.part_no = %s
				AND cp.docstatus != 2
				AND cp.name != %s
				LIMIT 1
			""", (self.customer, self.process_type, self.item_code, row.part_no, self.name))

			if duplicate_exists:
				frappe.throw(_('Duplicate entry found: Customer "{0}", Process Type "{1}", Item Code "{2}", and Part No. "{3}" must be unique.')
							.format(self.customer, self.process_type, self.item_code, row.part_no))

	def after_insert(self):
		self.set_title()
		self.db_set("title_data", self.title_data)



	def set_title(self):
		self.customer_ref=self.name
		self.title_data = "{0}-{1}-{2}-{3}".format(self.customer_ref, self.process_type,self.item_code,self.customer_ref)




	def on_trash(self):
		self.remove_item()
	
	def remove_item(self):
		if self.item_code:
			if   frappe.db.exists("Item", self.item_code):
				item = frappe.get_doc("Item", self.item_code)
				if item:
					item.delete()
					frappe.msgprint(_("Item {0} deleted successfully").format(self.item_code))
		
	def create_item(self):
		if not  frappe.db.exists("Item", self.item_code):
			stock=frappe.get_single("Stock Settings")
			item = frappe.new_doc("Item")
			item.item_code = self.item_code
			item.item_name = self.item_name
			item.item_group = "Customer item"
			item.is_stock_item=0
			item.gst_hsn_code="998873"

			item.stock_uom = stock.stock_uom
			item.save()


	@frappe.whitelist()
	def start_delete_customer_process_in_background(self):
		frappe.enqueue(
			method=delete_customer_process_batch,   # no path needed
			queue='long',
			timeout=3600,
			now=False,
		)
		return "Deletion started in background ✅"


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








def delete_customer_process_batch():
    batch_size = 2000
    count = 0

    customer_process_names = frappe.get_all("Customer Process", pluck="name")

    frappe.logger().info(f"[Customer Process Deletion] Found {len(customer_process_names)} records to delete.")

    for name in customer_process_names:
        try:
            doc = frappe.get_doc("Customer Process", name)
            doc.delete()
            count += 1

            if count % batch_size == 0:
                frappe.db.commit()
                frappe.logger().info(f"[Customer Process Deletion] Committed after {count} deletes.")
        except Exception as e:
            frappe.logger().error(f"[Customer Process Deletion] Failed to delete {name}: {e}")

    frappe.db.commit()
    frappe.logger().info(f"[Customer Process Deletion] ✅ Completed {count} deletions.")
