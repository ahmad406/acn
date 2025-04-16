# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobPlanScheduler(Document):
	def on_validate(self):
		self.set_job_paramenters()
		self.set_consolidatedjob_paramenters()

	def set_job_paramenters(self):
		jobs = list({d.job_card_id for d in self.job_card_details if d.job_card_id})

		if not jobs:
			return

		self.set("parameters_with_acceptance_criteria", [])

		for job_id in jobs:
			job_doc = frappe.get_doc("Job Card for process", job_id)
			for param in job_doc.parameters_with_acceptance_criteria:
				row = self.append("parameters_with_acceptance_criteria", {})
				row.job_card_id = job_doc.name
				row.lot_no = param.lot_no
				row.internal_process = param.internal_process
				row.control_parameter = param.control_parameter
				row.minimum_value = param.minimum_value
				row.maximum_value = param.maximum_value
				row.scale = param.scale
				row.microstructure_cutoff = param.microstructure_cutoff
				row.information = param.information

	def set_consolidatedjob_paramenters(self):
		jobs = list({d.job_card_id for d in self.job_card_details if d.job_card_id})

		if not jobs:
			return

		self.set("parameters_plan", [])

		existing_processes = set()

		for job_id in jobs:
			job_doc = frappe.get_doc("Job Card for process", job_id)
			for param in job_doc.parameters_with_acceptance_criteria:
				if param.internal_process in existing_processes:
					continue  

				existing_processes.add(param.internal_process)

				row = self.append("parameters_plan", {})
				row.job_card_id = job_doc.name
				row.lot_no = param.lot_no
				row.internal_process = param.internal_process
				row.control_parameter = param.control_parameter
				row.minimum_value = param.minimum_value
				row.maximum_value = param.maximum_value
				row.scale = param.scale
				row.microstructure_cutoff = param.microstructure_cutoff
				row.information = param.information




	@frappe.whitelist()
	def get_internal_process_details(self):
		if self.internal_process:
			query = """
			SELECT 
						c.internal_process,c.furnace_process,c.media
					FROM 
						`tabJob Card for process` p
					INNER JOIN 
						`tabSequence Lot wise Internal Process` c 
						ON p.name = c.parent
					WHERE 
						c.is_planned = 0
						AND NOT EXISTS (
							SELECT 1 
							FROM `tabSequence Lot wise Internal Process` c2
							WHERE 
								c2.parent = c.parent
								AND c2.is_planned = 0
								AND c2.lot_no < c.lot_no
						)
						AND c.internal_process="{0}"
						limit 1

			""".format(self.internal_process)
		result = frappe.db.sql(query, as_dict=True)
		if result:
			self.furnace_process= result[0].furnace_process
			self.media= result[0].media
	# @frappe.whitelist()
	# def get_furnace_code_details(self):



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_internal_process(doctype, txt, searchfield, start, page_len, filters):
	args = {
		'start': start,
		'page_len': page_len,
		'txt': f"%{txt}%",
	}

	query = """
		SELECT 
			c.internal_process
		FROM 
			`tabJob Card for process` p
		INNER JOIN 
			`tabSequence Lot wise Internal Process` c 
			ON p.name = c.parent
		WHERE 
			c.is_planned = 0
			AND NOT EXISTS (
				SELECT 1 
				FROM `tabSequence Lot wise Internal Process` c2
				WHERE 
					c2.parent = c.parent
					AND c2.is_planned = 0
					AND c2.lot_no < c.lot_no
			)
			AND c.internal_process LIKE %(txt)s
		GROUP BY c.internal_process
		ORDER BY c.internal_process
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def furnace_code(doctype, txt, searchfield, start, page_len, filters):
	furnace_process = filters.get('furnace_process')
	args = {
		'start': start,
		'page_len': page_len,
		'furnace_process': furnace_process,
		'txt': f"%{txt}%",
	}

	query = """
		SELECT 
			c.furnace_code
		FROM 
			`tabFurnace Process`  p 
			inner join `tabFurnace Details` c on p.name = c.parent
		
		WHERE 
			p.name = %(furnace_process)s
			AND c.furnace_code LIKE %(txt)s
		
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_job_card(doctype, txt, searchfield, start, page_len, filters):
	internal_process = filters.get('internal_process')
	args = {
		'start': start,
		'page_len': page_len,
		'internal_process': internal_process,
		'txt': f"%{txt}%",
	}

	query = """
		SELECT 
			p.name
		FROM 
			`tabJob Card for process` p
		INNER JOIN 
			`tabSequence Lot wise Internal Process` c 
			ON p.name = c.parent
		WHERE 
			c.is_planned = 0
			c.p.name = %(internal_process)s
			AND NOT EXISTS (
				SELECT 1 
				FROM `tabSequence Lot wise Internal Process` c2
				WHERE 
					c2.parent = c.parent
					AND c2.is_planned = 0
					AND c2.lot_no < c.lot_no
			)
			AND c.internal_process LIKE %(txt)s
		GROUP BY c.internal_process
		ORDER BY c.internal_process
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)

