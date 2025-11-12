# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt,cint



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
		self.validate_test_result()
		self.update_jb_plan()
		self.update_job_card()
		self.update_is_ready_for_next_lot(cancel=False)

		
	def validate(self):
		for row in self.inspection_qty_details:
				if flt(row.samplingcheckqty) > 0:
					row.checked_qty_in_nos = flt(row.samplingcheckqty)
				
		
	def validate_test_result(self):
		
		missing_rows = []
		for d in self.test_results: 
			if not d.result_vaule:
				missing_rows.append(str(d.idx))

		if missing_rows:
			frappe.throw(
				"Test Results are not updated in Row number(s): {}".format(", ".join(missing_rows))
			) 

	def on_cancel(self):
		# frappe.throw("Canceling not Allowed For this Doctype")
		self.update_jb_plan(cancel=1)
		self.update_job_card(is_cancelled=1)
		self.update_is_ready_for_next_lot(cancel=True)

	@frappe.whitelist()
	def update_is_ready_for_next_lot(self, cancel=False):
		"""
		EXECUTION PHASE (Job Execution Submit)
		--------------------------------------
		When a lot is executed:
			✅ Marks next-lot(s) as ready based on executed qty (nos/kgs).
			✅ Keeps leftover (if any) as balance in the executed lot.
			✅ Prevents readiness from exceeding planned qty.
			✅ Handles cancel rollback cleanly.
		"""

		plan = frappe.get_doc("Job Plan Scheduler", self.job_plan_id)

		for d in self.inspection_qty_details:
			current_lot = cint(d.lot_no)

			# 🛑 --- CANCEL PROTECTION ---
			if cancel:
				later_lots = frappe.db.sql("""
					SELECT name,parent 
					FROM `tabJob Card details`
					WHERE parenttype='Job Plan Scheduler'
						AND job_card_id=%s
						AND lot_no > %s
						AND docstatus=1
						AND (
							is_ready=1
							OR EXISTS(
								SELECT 1 
								FROM `tabJob Plan Scheduler`
								WHERE name=`tabJob Card details`.parent
									AND job_execution=1
									AND docstatus=1
							)
						)
				""", (d.job_card_id, current_lot), as_dict=True)

				if later_lots:
					frappe.throw(f"❌ Cannot cancel Lot {current_lot} — later lots are already ready or executed. {later_lots[0].parent}")

				# 🔄 Revert readiness added to *all* next lot(s)
				next_lot_rows = frappe.db.sql("""
					SELECT name, ready_qty_nos, ready_qty_kgs
					FROM `tabJob Card details`
					WHERE parenttype='Job Plan Scheduler'
						AND job_card_id=%s
						AND lot_no > %s
						AND docstatus=1
				""", (d.job_card_id, current_lot), as_dict=True)

				for row in next_lot_rows:
					to_sub_nos = min(flt(d.planned_qty_in_nos or 0), flt(row.ready_qty_nos or 0))
					to_sub_kgs = min(flt(d.planned_qty_in_kgs or 0), flt(row.ready_qty_kgs or 0))

					frappe.db.sql("""
						UPDATE `tabJob Card details`
						SET 
							ready_qty_nos = GREATEST(ready_qty_nos - %s, 0),
							ready_qty_kgs = GREATEST(ready_qty_kgs - %s, 0),
							is_ready = IF(ready_qty_nos > 0 OR ready_qty_kgs > 0, 1, 0)
						WHERE name = %s
					""", (to_sub_nos, to_sub_kgs, row.name))
				continue

			# ✅ --- EXECUTION FLOW ---
			executed_qty_nos = flt(d.planned_qty_in_nos or 0)
			executed_qty_kgs = flt(d.planned_qty_in_kgs or 0)

			# Fetch *all* next-lot(s) across all future plans (not just +1)
			next_lot_rows = frappe.db.sql("""
				SELECT 
					c.name,
					c.planned_qty_in_nos,
					c.planned_qty_in_kgs,
					COALESCE(c.ready_qty_nos,0) AS current_ready_nos,
					COALESCE(c.ready_qty_kgs,0) AS current_ready_kgs,
					c.lot_no,
					c.parent AS plan_id
				FROM `tabJob Card details` c
				INNER JOIN `tabJob Plan Scheduler` p ON p.name = c.parent
				WHERE 
					c.parenttype='Job Plan Scheduler'
					AND c.job_card_id=%s
					AND c.lot_no > %s
					AND p.docstatus=1
					AND IFNULL(p.job_execution,0)=0
				ORDER BY c.lot_no ASC, p.creation ASC
			""", (d.job_card_id, current_lot), as_dict=True)

			remaining_nos = executed_qty_nos
			remaining_kgs = executed_qty_kgs
			distributed_nos = 0
			distributed_kgs = 0

			# 🧮 --- DISTRIBUTE READY QTY TO NEXT LOT(S) ---
			for row in next_lot_rows:
				planned_nos = flt(row.planned_qty_in_nos or 0)
				planned_kgs = flt(row.planned_qty_in_kgs or 0)
				current_ready_nos = flt(row.current_ready_nos or 0)
				current_ready_kgs = flt(row.current_ready_kgs or 0)

				# Capacity still available in that row
				alloc_nos = max(0, planned_nos - current_ready_nos)
				alloc_kgs = max(0, planned_kgs - current_ready_kgs)

				if alloc_nos <= 0 and alloc_kgs <= 0:
					continue  # already full, skip

				ready_nos = min(remaining_nos, alloc_nos)
				ready_kgs = min(remaining_kgs, alloc_kgs)

				# ✅ Atomic update with cap (never exceed planned qty)
				frappe.db.sql("""
					UPDATE `tabJob Card details` AS c
					JOIN (
						SELECT 
							name,
							LEAST(planned_qty_in_nos, COALESCE(ready_qty_nos,0) + %s) AS new_ready_nos,
							LEAST(planned_qty_in_kgs, COALESCE(ready_qty_kgs,0) + %s) AS new_ready_kgs
						FROM `tabJob Card details`
						WHERE name = %s
					) AS tmp ON tmp.name = c.name
					SET 
						c.is_ready = IF(tmp.new_ready_nos > 0 OR tmp.new_ready_kgs > 0, 1, 0),
						c.ready_qty_nos = tmp.new_ready_nos,
						c.ready_qty_kgs = tmp.new_ready_kgs,
						c.balance_ready_qty_nos = 0,
						c.balance_ready_qty_kgs = 0
				""", (ready_nos, ready_kgs, row.name))

				remaining_nos -= ready_nos
				remaining_kgs -= ready_kgs
				distributed_nos += ready_nos
				distributed_kgs += ready_kgs

				# ✅ Keep break only when actual remaining = 0
				if remaining_nos <= 0 and remaining_kgs <= 0:
					break

			# ✅ --- Compute Remaining Balance (leftover from executed lot) ---
			balance_nos = max(remaining_nos, 0)
			balance_kgs = max(remaining_kgs, 0)

			# 🧾 --- UPDATE CURRENT EXECUTED LOT ---
			frappe.db.sql("""
				UPDATE `tabJob Card details`
				SET 
					is_ready = 0,
					ready_qty_nos = 0,
					ready_qty_kgs = 0,
					balance_ready_qty_nos = %s,
					balance_ready_qty_kgs = %s
				WHERE parenttype='Job Plan Scheduler'
					AND parent=%s
					AND job_card_id=%s
					AND lot_no=%s
			""", (balance_nos, balance_kgs, plan.name, d.job_card_id, current_lot))

			# 🪣 --- LOG ANY REMAINDER ---
			if (balance_nos > 0 or balance_kgs > 0) and not next_lot_rows:
				frappe.logger().info(
					f"[CarryForward] Lot {current_lot}: Remaining {balance_nos} nos, {balance_kgs} kgs unallocated."
				)



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
				row.location_image=d.location_image
				row.fixturing_image=d.fixturing_image
				row.lot_no=d.lot_no

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
		# self.set_check_qty()
		return True
	


	
	@frappe.whitelist()
	def set_plan(self):
		if self.job_plan_id:
			# self.set("inspection_qty_details",[])
			self.set("parameters",[])
			self.set("test_results",[])


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
					row.testing_method=k.testing_method
					row.customer_process=k.customer_process
					row.checked_qty_in_nos=0

					self.set_checked_qty(row)

					get_min_max(jb,row)
					self.insert_row_base_onchecked_Qty(row)
			self.update_job_card_counts()

				
			return True
	

	def update_job_card_counts(self):
		from collections import defaultdict
		counts = defaultdict(int)
		for row in self.test_results:
			if row.job_card_id:
				counts[row.job_card_id] += 1

		for row in self.inspection_qty_details:
			if row.job_card_id in counts:
				row.checked_qty_in_nos = counts[row.job_card_id]
				row.samplingcheckqty=row.checked_qty_in_nos
			else:
				
				row.checked_qty_in_nos = 0
				row.samplingcheckqty=row.checked_qty_in_nos


	def insert_row_base_onchecked_Qty(self, d):
		for _ in range(int(d.checked_qty_in_nos)):
			row = self.append("test_results", {})
			row.job_card_id = d.job_card_id
			row.control_parameters = d.control_parameter
			row.minimum_value = d.minimum_value
			row.maximum_value = d.maximum_value
			row.scale = d.scale
			row.testing_qty = 1

	def set_checked_qty(self, row):
		if row.testing_method:
			if row.testing_method == "100% checking":
				row.checked_qty_in_nos = row.planned_qty_in_nos

			elif row.testing_method == "As per Sampling Plan":
				qty = get_sample_plan_frm_scale(
					row.scale, row.planned_qty_in_nos, self.internal_process
				)
				row.checked_qty_in_nos = qty or 0 

			elif row.testing_method == "As per Customer Contract":
				qty = get_sample_plan_frm_process(
					row, self.internal_process
				)
				row.checked_qty_in_nos = qty or 0 

def get_sample_plan_frm_process(row, process):
	doc = frappe.get_doc("Customer Process", row.customer_process)
	for child in doc.testing_slab_method:
		if (
			child.internal_process == process
			and child.batch_qty_from <= row.planned_qty_in_nos <= child.batch_qty_to
			and child.scale == row.scale
		):
			return child.sample_qty_for_testing
	return None

def get_sample_plan_frm_scale(scale, qty, process):
	doc = frappe.get_doc("Scale", scale)
	if doc.test_req:
		for row in doc.scale_sample:
			if (
				row.internal_process == process
				and row.batch_qty_from <= qty <= row.batch_qty_to
			):
				return row.sample_qty_for_testing
	return None 

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





	