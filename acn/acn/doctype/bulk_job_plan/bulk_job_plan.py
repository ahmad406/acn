import frappe
from frappe.model.document import Document
from collections import defaultdict
from frappe.utils  import today


class BulkJobPlan(Document):

    def on_submit(self):
        self.create_job_plan_schedulers()

    def before_submit(self):
        self.keep_only_planned_rows()



    def create_job_plan_schedulers(self):

        planned_rows = [d for d in self.bulk_planning if d.planned]

        if not planned_rows:
            frappe.throw("Please mark at least one row as Planned")

        process_map = defaultdict(list)

        for row in planned_rows:
            process_map[row.internal_process].append(row)

        created_docs = []

        #  create one scheduler per process
        for process, rows in process_map.items():

            scheduler = frappe.new_doc("Job Plan Scheduler")

            scheduler.internal_process = process
            scheduler.planned_date = today()

            scheduler.get_internal_process_details()

            # copy plan date if needed
            if rows and rows[0].job_loading_plan_date:
                scheduler.job_loading_plan_date = rows[0].job_loading_plan_date

            #  append job cards
            for r in rows:
                job_card = frappe.get_doc("Job Card for process", r.job_card_id)
                scheduler.append("job_card_details", {
                "job_card_id": r.job_card_id,
                "job_card_for_process":r.process_name,
                "planned_qty_in_nos": r.plan_qty_in_nos,
                "planned_qty_in_kgs": r.plan_qty_in_kgs,
                "balance_plan_qty_in_nos": r.balance_plan_qty_in_nos,
                "balance_plan_qty_in_kgs": r.balance_plan_qty_in_kgs,
                "customer_dc_id": r.customer_dc_no,
                "customer_process_ref_no": job_card.customer_process_ref_no,
                "customer_dc_no": job_card.customer_dc_no,
                "fixturing_image": job_card.fixturing_image,
                "location_image": job_card.location_image,
                "customer_code":r.customer_code,
                "customer_name": r.customer_name,
                "commitment_date":job_card.commitment_date,
                "item_code": r.item_code,
                "item_name": r.item_name,
                "part_no": r.part_number,
                "material": r.material,
                "process_type": r.process_type,
                "process_name": r.process_name,
                "lot_no": r.lot_no,
                "customer_requirements":r.customer_requirement
            })


            # CRITICAL (reuse existing logic)
            scheduler.update_job_card_table()
            scheduler.calculated_end()

            # save as draft only
            scheduler.insert(ignore_permissions=True)

            created_docs.append(scheduler.name)

        frappe.msgprint(
            f"Created Job Plan Scheduler(s): {', '.join(created_docs)}"
        )

    def keep_only_planned_rows(self):
        rows = [d.as_dict() for d in self.bulk_planning if d.planned]
        self.set("bulk_planning", rows)



@frappe.whitelist()
def get_bulk_data(internal_process=None, customer=None, job_card=None,mrn_no=None):

    conditions = ["p.docstatus = 1","c.balance_qty_in_nos > 0"]

    if internal_process:
        conditions.append("c.internal_process = %(internal_process)s")

    if customer:
        conditions.append("p.customer_name = %(customer)s")

    if job_card:
        conditions.append("p.name = %(job_card)s")

    if mrn_no:
        conditions.append("p.customer_dc = %(mrn_no)s")

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(f"""
        SELECT
            p.customer_dc AS customer_dc_no,
            p.name AS job_card_id,
            p.item_code,
			p.item_name,
            p.customer_code,
			p.customer_name,
            p.part_no AS part_number,
            p.material,
			p.process_type,
			p.process_name,
			p.item_code,
            p.customer_req AS customer_requirement,
            p.qty_in_nos AS mrn_qty_in_nos,
            p.qty_in_kgs AS mrn_qty_in_kgs,
			c.internal_process,
            c.lot_no,
            c.balance_qty_in_nos AS balance_plan_qty_in_nos,
            c.balance_qty_in_kgs AS balance_plan_qty_in_kgs
        FROM `tabJob Card for process` p
        INNER JOIN `tabSequence Lot wise Internal Process` c
            ON p.name = c.parent
        WHERE {where_clause}
        ORDER BY c.lot_no, c.internal_process
    """, {
        "internal_process": internal_process,
        "customer": customer,
        "job_card": job_card,
        "mrn_no": mrn_no
    }, as_dict=True)

    return data


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_job_card_bulk(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""
        SELECT p.name
        FROM `tabJob Card for process` p
        INNER JOIN `tabSequence Lot wise Internal Process` c
            ON p.name = c.parent
        WHERE
            p.docstatus = 1
            AND COALESCE(c.balance_qty_in_nos,0) > 0
            AND p.name LIKE %s
        GROUP BY p.name
        LIMIT %s, %s
    """, (f"%{txt}%", start, page_len))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_active_customers(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""
        SELECT DISTINCT p.customer_name
        FROM `tabJob Card for process` p
        INNER JOIN `tabSequence Lot wise Internal Process` c
            ON p.name = c.parent
        WHERE
            p.docstatus = 1
            AND COALESCE(c.balance_qty_in_nos,0) > 0
            AND p.customer_name LIKE %s
        LIMIT %s, %s
    """, (f"%{txt}%", start, page_len))


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_active_mrn(doctype, txt, searchfield, start, page_len, filters):

    return frappe.db.sql("""
        SELECT DISTINCT p.customer_dc
        FROM `tabJob Card for process` p
        INNER JOIN `tabSequence Lot wise Internal Process` c
            ON p.name = c.parent
        WHERE
            p.docstatus = 1
            AND COALESCE(c.balance_qty_in_nos,0) > 0
            AND p.customer_dc LIKE %s
        ORDER BY p.customer_dc
        LIMIT %s, %s
    """, (f"%{txt}%", start, page_len))
