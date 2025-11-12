# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt




class JobExecutionLogsheet(Document):
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
				row.lot_no=d.lot_no
				
				row.planned_qty_in_nos=d.planned_qty_in_nos
				row.planned_qty_in_kgs=d.planned_qty_in_kgs
			for k in jb.parameters_plan:
				row_2=self.append("parameters",{})
				row_2.control_parameter=k.control_parameter
				row_2.planned_value=k.planned_value
				row_2.actual_value=k.planned_value
				row_2.scale=k.scale

		return True




	def on_submit(self):
		self.update_jb_plan()
		self.update_is_ready_for_next_lot(cancel=False)

	def on_cancel(self):
		frappe.throw("Canceling not Allowed For this Doctype")
		self.update_is_ready_for_next_lot(cancel=True)
		self.update_jb_plan(cancel=True)

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

		for d in self.production_jobs:
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


					
			

	def update_jb_plan(self, cancel=0):
		if self.job_plan_id:
			jb = frappe.get_doc("Job Plan Scheduler", self.job_plan_id)
			status = 0 if cancel else 1
			jb.db_set("job_execution", status)
			
		  
			


# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def job_plan(doctype, txt, searchfield, start, page_len, filters):
# 	internal_process_for = filters.get("internal_process_for")

# 	# ✅ Fetch all job plans:
# 	# - Docstatus = 1
# 	# - Not yet executed
# 	# - At least one Job Card detail is ready (ready_qty > 0)
# 	# - Exclude plans where all ready qtys are zero
# 	data = frappe.db.sql("""
# 		SELECT 
# 			p.name AS plan_id,
# 			c.job_card_id,
# 			c.lot_no,
# 			c.ready_qty_nos,
# 			c.ready_qty_kgs
# 		FROM `tabJob Plan Scheduler` p
# 		INNER JOIN `tabJob Card details` c 
# 			ON c.parent = p.name
# 		WHERE 
# 			p.docstatus = 1
# 			AND IFNULL(p.job_execution, 0) = 0
# 			AND p.internal_process_for = %s
# 			AND p.name LIKE %s
# 			AND (
# 				IFNULL(c.is_ready, 0) = 1
# 				OR IFNULL(c.ready_qty_nos, 0) > 0
# 				OR IFNULL(c.ready_qty_kgs, 0) > 0
# 			)
# 			-- optional: skip plans where all ready qtys are zero
# 			AND NOT (
# 				IFNULL(c.ready_qty_nos, 0) = 0
# 				AND IFNULL(c.ready_qty_kgs, 0) = 0
# 			)
# 		ORDER BY c.job_card_id, c.lot_no
# 		LIMIT %s, %s
# 	""", (internal_process_for, f"%{txt}%", start, page_len), as_dict=True)

# 	# ✅ Format results for Link field display
# 	return [
# 		(
# 			row.plan_id,
# 			f"{row.plan_id} | Lot {row.lot_no} | {row.job_card_id} | Ready: {row.ready_qty_nos or 0} Nos / {row.ready_qty_kgs or 0} Kg"
# 		)
# 		for row in data
# 	]

# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def job_plan(doctype, txt, searchfield, start, page_len, filters):
#     internal_process_for = filters.get("internal_process_for", "")

#     data = frappe.db.sql("""
#         SELECT 
#             p.name AS plan_id,
#             GROUP_CONCAT(DISTINCT c.job_card_id SEPARATOR ', ') AS job_cards,
#             COUNT(c.name) AS total_rows,
#             SUM(IF(c.is_ready=1,1,0)) AS ready_rows,
#             SUM(IFNULL(c.ready_qty_nos,0)) AS total_ready_nos,
#             SUM(IFNULL(c.ready_qty_kgs,0)) AS total_ready_kgs
#         FROM `tabJob Plan Scheduler` p
#         JOIN `tabJob Card details` c ON c.parent = p.name
#         WHERE 
#             p.docstatus = 1
#             AND IFNULL(p.job_execution, 0) = 0
#             AND (%s = '' OR LOWER(p.internal_process_for) = LOWER(%s))
#             AND p.name LIKE %s
#         GROUP BY p.name
#         HAVING 
#             (SUM(IFNULL(c.ready_qty_nos,0)) > 0 OR SUM(IFNULL(c.ready_qty_kgs,0)) > 0)
#         ORDER BY p.modified DESC
#         LIMIT %s, %s
#     """, (internal_process_for, internal_process_for, f"%{txt}%", start, page_len), as_dict=True)

#     return [
#         (
#             row.plan_id,
#             f"{row.plan_id} | Ready Lots: {row.ready_rows}/{row.total_rows} | Ready: {flt(row.total_ready_nos)} Nos / {flt(row.total_ready_kgs)} Kg"
#         )
#         for row in data
#     ]




@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def job_plan(doctype, txt, searchfield, start, page_len, filters):
    internal_process_for = filters.get("internal_process_for", "")

    data = frappe.db.sql("""
        SELECT 
            p.name AS plan_id,
            GROUP_CONCAT(DISTINCT c.job_card_id SEPARATOR ', ') AS job_cards,
            COUNT(c.name) AS total_rows,
            SUM(IF(c.is_ready=1,1,0)) AS ready_rows,
            SUM(IFNULL(c.ready_qty_nos,0)) AS total_ready_nos,
            SUM(IFNULL(c.ready_qty_kgs,0)) AS total_ready_kgs,
            SUM(IFNULL(c.planned_qty_in_nos,0)) AS total_planned_nos,
            SUM(IFNULL(c.planned_qty_in_kgs,0)) AS total_planned_kgs
        FROM `tabJob Plan Scheduler` p
        JOIN `tabJob Card details` c ON c.parent = p.name
        WHERE 
            p.docstatus = 1
            AND IFNULL(p.job_execution, 0) = 0
            AND (%s = '' OR LOWER(p.internal_process_for) = LOWER(%s))
            AND p.name LIKE %s
        GROUP BY p.name
        HAVING 
            (
                -- Only include when total ready qty fully equals planned qty
                (ROUND(SUM(IFNULL(c.ready_qty_nos,0)), 6) = ROUND(SUM(IFNULL(c.planned_qty_in_nos,0)), 6))
                AND
                (ROUND(SUM(IFNULL(c.ready_qty_kgs,0)), 6) = ROUND(SUM(IFNULL(c.planned_qty_in_kgs,0)), 6))
            )
        ORDER BY p.modified DESC
        LIMIT %s, %s
    """, (internal_process_for, internal_process_for, f"%{txt}%", start, page_len), as_dict=True)

    return [
        (
            row.plan_id,
            f"{row.plan_id} | Ready Lots: {row.ready_rows}/{row.total_rows} | Ready: {flt(row.total_ready_nos)} Nos / {flt(row.total_ready_kgs)} Kg"
        )
        for row in data
    ]
