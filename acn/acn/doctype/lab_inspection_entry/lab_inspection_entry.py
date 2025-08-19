# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LabInspectionEntry(Document):
	@frappe.whitelist()
	def save_inspection_data(self, data):
		import json

		data = json.loads(data) if isinstance(data, str) else data
		self.set("inspect_info", [])

		for row in data:
			self.append("inspect_info", {
				"header": row["header"],
				"to_check": row["to_check"],
				"result": row["result"],
				"remarks": row["remarks"],
				"image": row.get("image")
			})
		return True
		

	def before_insert(self):
		self.lab_inspection_entry_id = self.name

	def on_submit(self):
		self.update_jb_plan()
		self.update_job_card()

	def on_cancel(self):
		self.update_jb_plan(cancel=1)
		self.update_job_card(is_cancelled=1)
	@frappe.whitelist()
	def update_job_card(self, is_cancelled=0):
		for d in self.inspection_qty_details:
			if d.job_card_id:
				jb = frappe.get_doc("Job Card for process", d.job_card_id)

				if jb.sequence_lot_wise_internal_process:
					last_row = max(
						jb.sequence_lot_wise_internal_process,
						key=lambda x: int(x.lot_no or 0)
					)

					if last_row.internal_process == self.internal_process:
						qty = -d.planned_qty_in_nos if is_cancelled else d.planned_qty_in_nos
						new_qty = (last_row.inspection_qty or 0) + qty
						last_row.db_set("inspection_qty", new_qty)

				


	def update_jb_plan(self, cancel=0):
		if self.job_plan_id:
			jb = frappe.get_doc("Job Plan Scheduler", self.job_plan_id)
			status = 0 if cancel else 1
			jb.db_set("job_execution", status)
	@frappe.whitelist()
	def set_job_plan_details(self):
		if self.job_plan_id:
			self.set("inspection_qty_details",[])
			self.set("parameters",[])

			jb=frappe.get_doc("Job Plan Scheduler",self.job_plan_id)
			self.internal_process=jb.internal_process
			self.furnace_process=jb.furnace_process
			# self.furnace_code=jb.furnace_code
			# self.furnace_name=jb.furnace_name
			self.media=jb.media
			self.job_loading_plan_date=jb.job_loading_plan_date
			self.loading_plan_time=jb.loading_plan_time



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
				row.accepted_qty_in_nos=d.planned_qty_in_nos
				row.accepted_qty_in_kgs=d.planned_qty_in_kgs
			# for k in self.inspection_qty_details:
			# 	row_2=self.append("parameters",{})
			# 	row_2.job_card_id=k.job_card_id
			# 	row_2.item_code=k.item_code
			# 	row_2.item_name=k.item_name
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no
			# 	row_2.part_no=k.part_no

		self.set_plan()
		return True
	
	@frappe.whitelist()
	def set_plan(self):
		if self.job_plan_id:
			# self.set("inspection_qty_details",[])
			self.set("parameters",[])

			jb=frappe.get_doc("Job Plan Scheduler",self.job_plan_id)
			for k in jb.parameters_plan:
				for d in self.inspection_qty_details:
					row=self.append("parameters",{})
					row.job_card_id=d.job_card_id
					row.item_code=d.item_code
					row.item_name=d.item_name
					row.part_no=d.part_no
					row.control_parameter=k.control_parameter
					row.planned_value=d.customer_name
					row.result_value_from=d.process_type
					row.result_value_to=d.process_name
					row.material=d.material
					row.customer_process_ref=d.customer_process_ref
					row.customer_dc_no=d.customer_dc_no
					row.planned_qty_in_nos=d.planned_qty_in_nos
					row.planned_qty_in_kgs=d.planned_qty_in_kgs
					row.planned_value=k.planned_value
					row.scale=k.scale
					get_min_max(jb,row)
				
			return True
def get_min_max(jb,row):
	for d in jb.parameters_with_acceptance_criteria:
		if d.control_parameter==row.control_parameter:
			row.maximum_value=d.maximum_value	
			row.minimum_value=d.minimum_value
			row.furnace_code=d.furnace_code
			row.furnace_name=d.furnace_name
			return
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def job_plan(doctype, txt, searchfield, start, page_len, filters):
    args = {
        'start': start,
        'page_len': page_len,
        'txt': f'%{txt}%'
    }
    frappe.errprint("errp")
    job_plans = frappe.db.sql("""
        SELECT DISTINCT p.name 
			FROM `tabJob Plan Scheduler` p
			WHERE 
				p.docstatus = 1 
				AND p.job_execution = 0
				AND p.internal_process_for = 'Lab Inspection'
				AND NOT EXISTS (
					SELECT 1
					FROM `tabJob Card details` c
					WHERE c.parent = p.name
					AND NOT (
						c.lot_no = 1 OR
						EXISTS (
							SELECT 1 
							FROM `tabJob Plan Scheduler` prev_p
							INNER JOIN `tabJob Card details` prev_c ON prev_p.name = prev_c.parent
							WHERE prev_p.docstatus = 1
							AND prev_p.job_execution = 1
							AND prev_c.job_card_id = c.job_card_id
							AND prev_c.lot_no = c.lot_no - 1
						)
					)
				)

        AND p.name LIKE %(txt)s
        ORDER BY p.name
        LIMIT %(start)s, %(page_len)s
    """, args, as_dict=False)
    
    return job_plans



@frappe.whitelist()
def get_checklist(internal_process):
	
	return frappe.db.sql("""
		SELECT 
    p.header, 
    c.to_check,
    GROUP_CONCAT(m.value ORDER BY m.idx SEPARATOR ',') AS options,default_image
FROM 
    `tabChecklist Template` p
INNER JOIN 
    `tabTo be checked` c ON p.name = c.parent
INNER JOIN 
    `tabList method` m ON m.parent = c.applicable_method
INNER JOIN 
    `tabInternal Process List` i ON p.name = i.parent
WHERE 
   i.internal_process = %s
GROUP BY 
    p.header, c.to_check
ORDER BY 
    p.header, c.idx;

	""", (internal_process,), as_dict=True)