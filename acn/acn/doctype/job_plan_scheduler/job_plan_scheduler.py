# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class JobPlanScheduler(Document):
	def on_submit(self):
		self.update_jb_card()

	def on_cancel(self):
		self.update_jb_card(cancel=1)

	def update_jb_card(self, cancel=0):
		for d in self.job_card_details:
			jb = frappe.get_doc("Job Card for process", d.job_card_id)
			for j in jb.sequence_lot_wise_internal_process:
				if j.internal_process == self.internal_process:
					
					if cancel:
						new_nos = j.balance_qty_in_nos + d.planned_qty_in_nos
						new_kgs = j.balance_qty_in_kgs + d.planned_qty_in_kgs
					else:
						new_nos = j.balance_qty_in_nos - d.planned_qty_in_nos
						new_kgs = j.balance_qty_in_kgs - d.planned_qty_in_kgs

					if new_nos < 0 or new_kgs < 0:
						raise frappe.ValidationError(_("Balance quantity cannot go negative. Please check your inputs."))

					fullyis_planned = 1 if new_nos == 0 else 0

					j.db_set({
						"balance_qty_in_nos": new_nos,
						"balance_qty_in_kgs": new_kgs,
						"is_planned": fullyis_planned
					})

					break



					
	def validate(self):
		if self.is_new():
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
				if param.control_parameter in existing_processes:
					continue  

				existing_processes.add(param.control_parameter)

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
	def get_job_details(self,row):
		for d in self.job_card_details:
			if str(d.idx)==str(row.get("idx")):
				j=self.get_job(d.job_card_id)
				d.customer_dc_id=j.customer_dc
				d.item_code=j.item_code
				d.item_name=j.item_name
				d.part_no=j.part_no
				d.customer_code=j.customer_code
				d.customer_name=j.customer_name
				d.process_type=j.process_type
				d.process_name=j.process_name
				d.material=j.material
				d.customer_process_ref_no=j.customer_process_ref_no
				d.customer_dc_no=j.customer_dc_no
				d.commitment_date=j.commitment_date
				for k in j.sequence_lot_wise_internal_process:
					if k.internal_process == self.internal_process:
						d.balance_plan_qty_in_nos=k.balance_qty_in_nos
						d.balance_plan_qty_in_kgs=k.balance_qty_in_kgs
						d.planned_qty_in_nos=k.balance_qty_in_nos
						d.planned_qty_in_kgs=k.balance_qty_in_kgs
						break
		return True

	def get_job(self,job):
		doc=frappe.get_doc("Job Card for process",job)
		return doc
		

				



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
		return True
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
			c.is_planned = 0 and
			p.docstatus=1 and
			c.internal_process = %(internal_process)s
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

