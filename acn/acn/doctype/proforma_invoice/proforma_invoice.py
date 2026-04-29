# Copyright (c) 2026, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProformaInvoice(Document):
	pass



import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_dc_query(doctype, txt, searchfield, start, page_len, filters):
    docname = filters.get("docname") or ""

    # DC IDs already used in other Proforma Invoices (not cancelled)
    used = frappe.get_all(
        "Proforma Invoice",
        filters=[
            ["customer_dc_id", "!=", ""],
            ["name", "!=", docname],
            ["docstatus", "!=", 2]
        ],
        fields=["customer_dc_id"],
        limit=0
    )
    used_ids = [d.customer_dc_id for d in used if d.customer_dc_id]

    # Build NOT IN clause safely
    not_in_clause = ""
    if used_ids:
        placeholders = ", ".join(["%s"] * len(used_ids))
        not_in_clause = f"AND name NOT IN ({placeholders})"

    values = [f"%{txt}%", 1] + used_ids 

    return frappe.db.sql(f"""
        SELECT name
        FROM `tabCustomer DC`
        WHERE ({searchfield} LIKE %s)
          AND docstatus = %s
          {not_in_clause}
        ORDER BY name
        LIMIT %s OFFSET %s
    """, values + [page_len, start])