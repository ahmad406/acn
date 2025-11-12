# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import cint, flt


from datetime import datetime, timedelta
 

class JobPlanScheduler(Document):
	def validate(self):
		# Step 1: Ensure job parameters are set
		if not self.parameters_with_acceptance_criteria:
			frappe.throw("Click on 'Set Job Parameters' button and update Planned Value in Parameters Plan grid")

		# Step 2: Validate parameter values
		for k in self.parameters_plan:
			if flt(k.planned_value) < 0:
				frappe.throw(f"Planned value cannot be negative for parameter: {k.parameter or 'Unknown'}")

	


	
	@frappe.whitelist()
	def update_if_ready(self, cancel=False):
		"""
		PLANNING PHASE (Job Plan Scheduler)
		-----------------------------------
		- Determines 'ready_qty' for each lot based on balance from the previous executed lot.
		- Deducts reserved (ready) qty from previous lot balance immediately.
		- Does NOT allow negative balances.
		"""

		rows = sorted(self.job_card_details, key=lambda r: (cint(r.lot_no), r.idx or 0))

		for d in rows:
			lot_no = cint(d.lot_no)

			# 🔒 Cancel mode: clear readiness and re-add balance
			if cancel:
				if cint(d.lot_no) > 1:
					prev_lot_no = lot_no - 1
					# Add back previously deducted balance
					frappe.db.sql("""
						UPDATE `tabJob Card details`
						SET 
							balance_ready_qty_nos = balance_ready_qty_nos + %s,
							balance_ready_qty_kgs = balance_ready_qty_kgs + %s
						WHERE parenttype='Job Plan Scheduler'
							AND job_card_id=%s
							AND lot_no=%s
							AND docstatus=1
					""", (d.ready_qty_nos, d.ready_qty_kgs, d.job_card_id, prev_lot_no))
				d.is_ready = 0
				d.ready_qty_nos = 0
				d.ready_qty_kgs = 0
				d.balance_ready_qty_nos = 0
				d.balance_ready_qty_kgs = 0
				continue

			# 🟢 Lot 1 always ready
			if lot_no == 1:
				d.is_ready = 1
				d.ready_qty_nos = flt(d.planned_qty_in_nos or 0)
				d.ready_qty_kgs = flt(d.planned_qty_in_kgs or 0)
				d.balance_ready_qty_nos = 0
				d.balance_ready_qty_kgs = 0
				continue

			prev_lot_no = lot_no - 1

			# 1️⃣ Get executed balance
			executed = frappe.db.sql("""
				SELECT
					COALESCE(SUM(c.balance_ready_qty_nos), 0) AS nos,
					COALESCE(SUM(c.balance_ready_qty_kgs), 0) AS kgs
				FROM `tabJob Card details` c
				INNER JOIN `tabJob Plan Scheduler` p ON p.name = c.parent
				WHERE
					p.docstatus=1
					AND IFNULL(p.job_execution,0)=1
					AND c.job_card_id=%s
					AND c.lot_no=%s
			""", (d.job_card_id, prev_lot_no), as_dict=True)

			executed_nos = flt(executed[0].nos) if executed else 0
			executed_kgs = flt(executed[0].kgs) if executed else 0

			# 2️⃣ Compute how much is still free (no need for reserved query if we deduct live)
			available_nos = max(0, executed_nos)
			available_kgs = max(0, executed_kgs)

			# 3️⃣ Allocate to this plan
			planned_nos = flt(d.planned_qty_in_nos or 0)
			planned_kgs = flt(d.planned_qty_in_kgs or 0)
			ready_nos = max(0, min(available_nos, planned_nos))
			ready_kgs = max(0, min(available_kgs, planned_kgs))

			d.is_ready = 1 if (ready_nos > 0 or ready_kgs > 0) else 0
			d.ready_qty_nos = ready_nos
			d.ready_qty_kgs = ready_kgs
			d.balance_ready_qty_nos = 0
			d.balance_ready_qty_kgs = 0

			# 4️⃣ Deduct immediately from previous lot balance
			if not cancel:

				if ready_nos > 0 or ready_kgs > 0:
					frappe.db.sql("""
						UPDATE `tabJob Card details`
						SET 
							balance_ready_qty_nos = GREATEST(balance_ready_qty_nos - %s, 0),
							balance_ready_qty_kgs = GREATEST(balance_ready_qty_kgs - %s, 0)
						WHERE parenttype='Job Plan Scheduler'
							AND job_card_id=%s
							AND lot_no=%s
							AND docstatus=1
					""", (ready_nos, ready_kgs, d.job_card_id, prev_lot_no))
			else:
				if d.ready_qty_nos > 0 or d.ready_qty_kgs > 0:
					frappe.db.sql("""
						UPDATE `tabJob Card details`
						SET 
							balance_ready_qty_nos = balance_ready_qty_nos + %s,
							balance_ready_qty_kgs = balance_ready_qty_kgs + %s
						WHERE parenttype='Job Plan Scheduler'
							AND job_card_id=%s
							AND lot_no=%s
							AND docstatus=1
					""", (d.ready_qty_nos, d.ready_qty_kgs, d.job_card_id, prev_lot_no))



	@frappe.whitelist()
	def calculated_end(self):
		total_minutes = 0
		for d in self.parameters_plan:
			if d.scale == "mins":
				total_minutes += float(d.planned_value or 0)

		if self.job_loading_plan_date:
			# Convert to datetime if it's a string
			if isinstance(self.job_loading_plan_date, str):
				job_start = datetime.strptime(self.job_loading_plan_date, "%Y-%m-%d %H:%M:%S")
			else:
				job_start = self.job_loading_plan_date

			self.job_ending_plan_date = job_start + timedelta(minutes=total_minutes)
		return True



	def before_submit(self):
		self.update_jb_card()
			# Step 3: Update readiness flags for lots
		self.update_if_ready()

	def before_cancel(self):
		self.update_jb_card(cancel=1)
		self.update_if_ready(cancel=True)
		self.validate_lot_cancel_restriction() 
	

	def validate_lot_cancel_restriction(self):
		""" Prevent cancelling this Job Plan if any later lot of the same Job Card is marked ready."""
		for d in self.job_card_details:
			current_lot = cint(d.lot_no)

			# 🔍 Check for any later lot that is marked ready (is_ready = 1)
			later_lots = frappe.db.sql("""
				SELECT c.name
				FROM `tabJob Card details` c
				WHERE 
					c.parenttype = 'Job Plan Scheduler'
					AND c.job_card_id = %s
					AND c.lot_no > %s
					AND c.is_ready = 1
			""", (d.job_card_id, current_lot), as_dict=True)

			if later_lots:
				frappe.throw(
					f"Cannot cancel Job Plan {self.name} because a later lot for Job Card {d.job_card_id} "
					f"is already marked as ready."
				)

	def update_jb_card(self, cancel=0):
		for d in self.job_card_details:
			jb = frappe.get_doc("Job Card for process", d.job_card_id)
			process_list = jb.sequence_lot_wise_internal_process
			for idx, j in enumerate(process_list):
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

					if idx + 1 < len(process_list):
						next_row = process_list[idx + 1]
						if cancel:
							new_next_nos = next_row.balance_qty_in_nos - d.planned_qty_in_nos
							new_next_kgs = next_row.balance_qty_in_kgs - d.planned_qty_in_kgs
						else:
							new_next_nos = next_row.balance_qty_in_nos + d.planned_qty_in_nos
							new_next_kgs = next_row.balance_qty_in_kgs + d.planned_qty_in_kgs


						next_row.db_set({
							"balance_qty_in_nos": new_next_nos,
							"balance_qty_in_kgs": new_next_kgs,
						})

					break



					
	# def validate(self):
	# 	pass
		# if self.is_new():
		# 	self.update_job_card_table()
	@frappe.whitelist()		
	def update_job_card_table(self):
		self.set_job_paramenters()
		self.set_consolidatedjob_paramenters()
		return True
	def set_job_paramenters(self):
		jobs = list({d.job_card_id for d in self.job_card_details if d.job_card_id})

		if not jobs:
			return

		self.set("parameters_with_acceptance_criteria", [])

		for job_id in jobs:
			job_doc = frappe.get_doc("Job Card for process", job_id)
			for param in job_doc.parameters_with_acceptance_criteria:
				if param.internal_process == self.internal_process:
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
					row.testing_method=param.testing_method

					row.customer_process=param.customer_process



	def set_consolidatedjob_paramenters(self):
		jobs = list({d.job_card_id for d in self.job_card_details if d.job_card_id})

		if not jobs:
			return

		self.set("parameters_plan", [])

		existing_processes = set()

		for job_id in jobs:
			job_doc = frappe.get_doc("Job Card for process", job_id)
			for param in job_doc.parameters_with_acceptance_criteria:
				if param.internal_process == self.internal_process:
					
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
					row.testing_method=param.testing_method
					row.customer_process=param.customer_process



	@frappe.whitelist()
	def get_job_details(self,row):
		for d in self.job_card_details:
			if str(d.idx)==str(row.get("idx")):
				if d.job_card_id:
					j=self.get_job(d.job_card_id)
					d.customer_dc_id=j.customer_dc
					d.item_code=j.item_code
					d.item_name=j.item_name
					d.customer_requirements=j.customer_req
					d.part_no=j.part_no
					d.customer_code=j.customer_code
					d.customer_name=j.customer_name
					d.process_type=j.process_type
					d.process_name=j.process_name
					d.material=j.material
					d.customer_process_ref_no=j.customer_process_ref_no
					d.customer_dc_no=j.customer_dc_no
					d.commitment_date=j.commitment_date
					d.location_image=j.location_image
					# d.fixturing_image=j.fixturing_image
					for k in j.sequence_lot_wise_internal_process:
						if k.internal_process == self.internal_process:

							d.balance_plan_qty_in_nos=k.balance_qty_in_nos
							d.balance_plan_qty_in_kgs=k.balance_qty_in_kgs
							d.planned_qty_in_nos=k.balance_qty_in_nos
							d.planned_qty_in_kgs=k.balance_qty_in_kgs
							d.lot_no=k.lot_no
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
						c.internal_process,c.furnace_process,c.media,c.lot_no
					FROM 
						`tabJob Card for process` p
					INNER JOIN 
						`tabSequence Lot wise Internal Process` c 
						ON p.name = c.parent
					WHERE 
						 c.internal_process="{0}"
						limit 1

			""".format(self.internal_process)
		result = frappe.db.sql(query, as_dict=True)
		if result:
			self.furnace_process= result[0].furnace_process
			self.media = result[0].media
			self.lot_no =result[0].lot_no
		return True
	# c.is_planned = 0
	# 					AND NOT EXISTS (
	# 						SELECT 1 
	# 						FROM `tabSequence Lot wise Internal Process` c2
	# 						WHERE 
	# 							c2.parent = c.parent
	# 							AND c2.is_planned = 0
	# 							AND c2.lot_no < c.lot_no
	# 					)
	# 					AND
	# @frappe.whitelist()
	# def get_furnace_code_details(self):



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_internal_process(doctype, txt, searchfield, start, page_len, filters):
	args = {
		'start': start,
		'page_len': page_len,
		'txt': f"%{txt}%"
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
			c.balance_qty_in_nos > 0 and
			
			p.docstatus=1 
		
			AND c.internal_process LIKE %(txt)s
		GROUP BY c.internal_process
		ORDER BY c.internal_process
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
			p.name,p.customer_name,p.part_no,p.material,p.item_name,p.customer_dc
		FROM 
			`tabJob Card for process` p
		INNER JOIN 
			`tabSequence Lot wise Internal Process` c 
			ON p.name = c.parent
		WHERE 
			
			p.docstatus=1 and
			c.internal_process = %(internal_process)s and
				c.balance_qty_in_nos > 0
			
			AND p.name LIKE %(txt)s
	
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
	c.furnace_code,
	f.furnace_name
FROM 
	`tabFurnace Process` p
INNER JOIN 
	`tabFurnace Details` c 
	ON p.name = c.parent
INNER JOIN
	`tabFurnace` f 
	ON c.furnace_code = f.name

		WHERE 
			p.name = %(furnace_process)s
			AND c.furnace_code LIKE %(txt)s
		
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)

