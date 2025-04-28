# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabInspectionEntry(Document):
	@frappe.whitelist()
	def set_job_plan_details(self):
		if self.job_plan_id:
			self.set("inspection_qty_details",[])
			self.set("parameters",[])

			jb=frappe.get_doc("Job Plan Scheduler",self.job_plan_id)
			for d in jb.job_card_details:
				row=self.append("inspection_qty_details",{})
				row.job_card_id=d.job_card_id
				row.customer_dc_id=d.customer_dc_id
				row.item_code=d.item_code
				row.item_name=d.item_name
				row.part_no=d.part_no
				row.customer_code=d.customer_code
				row.customer_name=d.customer_name
				row.process_type=d.process_type
				row.process_name=d.process_name
				row.material=d.material
				row.customer_process_ref=d.customer_process_ref_no
				row.customer_dc_no=d.customer_dc_no
				row.planned_qty_in_nos=d.planned_qty_in_nos
				row.planned_qty_in_kgs=d.planned_qty_in_kgs
			# for k in self.inspection_qty_details:
			# 	row_2=self.append("parameters",{})
			# 	row_2.job_card_id=k.job_card_id
			# 	row_2.item_code=k.item_code
			# 	row_2.item_name=k.item_name
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no


		return True
	
	@frappe.whitelist()
	def set_plan(self):
		if self.job_plan_id:
			self.set("inspection_qty_details",[])
			self.set("parameters",[])

			jb=frappe.get_doc("Job Plan Scheduler",self.job_plan_id)
			for d in self.inspection_qty_details:
				row=self.append("parameters",{})
				row.job_card_id=d.job_card_id
				row.item_code=d.item_code
				row.item_name=d.item_name
				row.part_no=d.part_no
				row.control_parameter=d.control_parameter
				row.planned_value=d.customer_name
				row.result_value_from=d.process_type
				row.result_value_to=d.process_name
				row.scale=d.material
				row.customer_process_ref=d.customer_process_ref_no
				row.customer_dc_no=d.customer_dc_no
				row.planned_qty_in_nos=d.planned_qty_in_nos
				row.planned_qty_in_kgs=d.planned_qty_in_kgs
				for k in jb.parameters_plan:
					if k.control_parameter==d.control_parameter:
						row.planned_value=d.planned_value
						row.scale=d.scale
						break
			return True

