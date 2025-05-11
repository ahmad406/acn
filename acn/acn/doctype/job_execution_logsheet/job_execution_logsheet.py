# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobExecutionLogsheet(Document):
	def on_submit(self):
		self.update_jb_plan()

	def on_cancel(self):
		self.update_jb_plan(cancel=1)

	def update_jb_plan(self, cancel=0):
		if self.job_plan_id:
			jb = frappe.get_doc("Job Plan Scheduler", self.job_plan_id)
			status = 0 if cancel else 1
			jb.db_set("job_execution", status)


	@frappe.whitelist()
	def set_job_plan_details(self):
		if self.job_plan_id:
			self.set("production_jobs",[])
			self.set("parameters",[])

			jb=frappe.get_doc("Job Plan Scheduler",self.job_plan_id)
			for d in jb.job_card_details:
				row=self.append("production_jobs",{})
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
			for k in jb.parameters_plan:
				row_2=self.append("parameters",{})
				row_2.control_parameter=k.control_parameter
				row_2.planned_value=k.planned_value
				row_2.actual_value=k.planned_value
				row_2.scale=k.scale

		return True



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def job_plan(doctype, txt, searchfield, start, page_len, filters):
    args = {
        'start': start,
        'page_len': page_len,
        'txt': f'%{txt}%'
    }
    
    job_plans = frappe.db.sql("""
        SELECT DISTINCT p.name 
        FROM `tabJob Plan Scheduler` p
        INNER JOIN `tabJob Card details` c ON p.name = c.parent
        WHERE p.docstatus = 1 
        AND p.job_execution = 0
        AND (
            -- Case 1: It's the first job in sequence (lot_no = 1)
            c.lot_no = 1
            OR
            -- Case 2: Previous job exists and is completed
            EXISTS (
                SELECT 1 
                FROM `tabJob Plan Scheduler` prev_p
                INNER JOIN `tabJob Card details` prev_c ON prev_p.name = prev_c.parent
                WHERE prev_p.docstatus = 1
                AND prev_p.job_execution = 1
                AND prev_c.job_card_id = c.job_card_id  -- Make sure this column exists in your table
                AND prev_c.lot_no = c.lot_no - 1
            )
        )
        AND p.name LIKE %(txt)s
        ORDER BY p.name
        LIMIT %(start)s, %(page_len)s
    """, args, as_dict=False)
    
    return job_plans