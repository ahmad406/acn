# Copyright (c) 2026, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import money_in_words

class ProformaInvoice(Document):
    def before_save(self):
        self.calculate_amounts()
        self.in_words = money_in_words(self.grand_total or 0, "INR")

    def calculate_amounts(self):
        taxable_value = 0

        for row in self.proforma_invoice_table:
            uom = (row.uom or "").lower()

            if uom == "nos":
                qty = row.qty_nos or 0
            elif uom == "kgs":
                qty = row.qty_kgs or 0
            elif uom == "minimum":
                qty = 1
            else:
                qty = row.qty_nos or row.qty_kgs or 0

            row.amount = qty * (row.rate or 0)
            taxable_value += row.amount

        # Calculate tax amounts
        total_taxes = 0
        for tax in self.taxes_and_charges:
            tax.tax_amount = (taxable_value * (tax.rate or 0)) / 100
            tax.total = taxable_value + tax.tax_amount
            total_taxes += tax.tax_amount

        self.total_taxes_and_charges = total_taxes
        self.grand_total = taxable_value + total_taxes


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_dc_query(doctype, txt, searchfield, start, page_len, filters):
    docname = filters.get("docname") or ""

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