# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TestCertificateentry(Document):
	@frappe.whitelist()
	def get_details(self):
		self.set("test_parameters_details",[])
		self.customer_dc_id=""
		self.customer=""
		self.item=""
		self.part_no=""
		self.material=""
		self.accepted_qty_in_nos=""
		self.accepted_qty_in_kgs=""
		li=frappe.get_doc("Lab Inspection Entry",self.lab_inspection_id)
		for d in li.inspection_qty_details:
			if d.job_card_id==self.job_card_id:
				self.customer_dc_id=d.customer_dc_id
				self.customer=d.customer_name
				self.item=d.item_name
				self.part_no=d.part_no
				self.material=d.material
				self.accepted_qty_in_nos=d.accepted_qty_in_nos
				self.accepted_qty_in_kgs=d.accepted_qty_in_kgs

				break
		for k in li.parameters:
			row=self.append("test_parameters_details",{})
			row.test_parameters=k.control_parameter
			row.qty_checked=self.accepted_qty_in_nos

			row.reference_standard=self.get_standard(k.control_parameter)
			row.print_sequence_no = frappe.db.get_value('Internal Control Parameter', k.control_parameter, 'tc_order_no')


			row.acceptance_criteria_from=k.result_value_from
			row.acceptance_criteria_to=k.result_value_to
			row.scale=k.scale
			# row.measurement_from=
			# row.measurement_to=


def get_standard(self,para):
	doc=frappe.get_doc("Internal Control Parameter",para)
	if doc.ref_std:
		if doc.ref_std[0].reference_standard:
			return  doc.ref_std[0].reference_standard
		else:
			return ""
	else:
		return ""