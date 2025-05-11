# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TestCertificateentry(Document):
	def on_submit(self):
		self.update_certifed_status()
	def on_cancel(self):
		self.update_certifed_status(is_canceled=1)


	def update_certifed_status(self,is_canceled=0):
		status=1
		if is_canceled:
			status=0
		li=frappe.get_doc("Lab Inspection Entry",self.lab_inspection_id)
		for d in li.inspection_qty_details:
			if d.job_card_id==self.job_card_id:
				d.db_set("test_certified",status)
				break

	@frappe.whitelist()
	def get_details(self):
		if not self.lab_inspection_id:
			frappe.throw("Select Lab Inspection Id")
		if not self.job_card_id:
			frappe.throw("Select Job Card Id")

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
			row.other_detail_1=k.other_detail_1
			row.other_detail_2=k.other_detail_2
			row.other_detail_3=k.other_detail_3
			row.other_detail_4=k.other_detail_4
			row.other_detail_5=k.other_detail_5
			row.other_detail_6=k.other_detail_6
			row.other_detail_7=k.other_detail_7
			row.other_detail_8=k.other_detail_8
			row.other_detail_9=k.other_detail_9
			row.ref_standard=k.ref_standard


			row.core=k.core
			row.case=k.case


			row.case_depth_1_1=k.case_depth_1_1
			row.case_depth_1_2=k.case_depth_1_2
			row.case_depth_1_3=k.case_depth_1_3
			row.case_depth_1_4=k.case_depth_1_4
			row.case_depth_1_5=k.case_depth_1_5
			row.case_depth_1_6=k.case_depth_1_6
			row.case_depth_1_6=k.case_depth_1_6
			row.case_depth_1_7=k.case_depth_1_7
			row.case_depth_1_8=k.case_depth_1_8
			row.case_depth_1_9=k.case_depth_1_9
			row.case_depth_1_10=k.case_depth_1_10

			row.hardness_1_1=k.hardness_1_1
			row.hardness_1_2=k.hardness_1_2
			row.hardness_1_3=k.hardness_1_3
			row.hardness_1_4=k.hardness_1_4
			row.hardness_1_5=k.hardness_1_5
			row.hardness_1_6=k.hardness_1_6
			row.hardness_1_7=k.hardness_1_7
			row.hardness_1_8=k.hardness_1_8
			row.hardness_1_9=k.hardness_1_9
			row.hardness_1_10=k.hardness_1_10


			row.case_depth_2_1=k.case_depth_2_1
			row.case_depth_2_2=k.case_depth_2_2
			row.case_depth_2_3=k.case_depth_2_3
			row.case_depth_2_4=k.case_depth_2_4
			row.case_depth_2_5=k.case_depth_2_5
			row.case_depth_2_6=k.case_depth_2_6
			row.case_depth_2_7=k.case_depth_2_7
			row.case_depth_2_8=k.case_depth_2_8
			row.case_depth_2_9=k.case_depth_2_9
			row.case_depth_2_10=k.case_depth_2_10


			row.hardness_2_1=k.hardness_2_1
			row.hardness_2_2=k.hardness_2_2
			row.hardness_2_3=k.hardness_2_3
			row.hardness_2_4=k.hardness_2_4
			row.hardness_2_5=k.hardness_2_5
			row.hardness_2_6=k.hardness_2_6
			row.hardness_2_7=k.hardness_2_7
			row.hardness_2_8=k.hardness_2_8
			row.hardness_2_9=k.hardness_2_9
			row.hardness_2_10=k.hardness_2_10


			row.lab_entry_no=k.lab_entry_no
		jb=frappe.get_doc("Job Card for process",self.job_card_id)
		for f in jb.parameters_with_acceptance_criteria:
			rw=self.append("parameters",{})
			rw.internal_process=f.internal_process
			rw.control_parameter=f.control_parameter
			rw.minimum_value=f.minimum_value
			rw.maximum_value=f.maximum_value
			rw.scale=f.scale
			rw.microstructure_cutoff=f.microstructure_cutoff
			rw.information=f.information


		



			# row.measurement_from=
			# row.measurement_to=
		return True

	def get_standard(self,para):
		doc=frappe.get_doc("Internal Control Parameter",para)
		if doc.ref_std:
			if doc.ref_std[0].reference_standard:
				return  doc.ref_std[0].reference_standard
			else:
				return ""
		else:
			return ""