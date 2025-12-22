# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class JobCardforprocess(Document):
	def validate(self):
		for d  in self.sequence_lot_wise_internal_process:
			if d.idx==1:
				d.balance_qty_in_nos=self.qty_in_nos
				d.balance_qty_in_kgs=self.qty_in_kgs
import json

@frappe.whitelist()
def get_item_tax_rate(doc, account):
    if not doc or not account:
        return ""

    if not hasattr(doc, "items") or not doc.items:
        return ""

    item_tax_rate = doc.items[0].item_tax_rate
    if not item_tax_rate:
        return ""

    try:
        tax_map = json.loads(item_tax_rate) if isinstance(item_tax_rate, str) else item_tax_rate
    except Exception:
        return ""

    rate = tax_map.get(account)

    # 🔑 IMPORTANT FIX
    if not rate or rate <= 0:
        return ""

    return "@ {0}%".format(int(rate))

@frappe.whitelist()
def get_dispatch_details(doc):
	sql="""SELECT
		CASE WHEN rn = 1 THEN job_card ELSE "" END AS job_card,
		CASE WHEN rn = 1 THEN test_certificate ELSE "" END AS test_certificate,
		delivery_note,
		CASE WHEN rn = 1 THEN sales_invoice ELSE "" END AS sales_invoice,
		CASE WHEN rn = 1  THEN DATE_FORMAT(invoice_date, '%d-%m-%Y') ELSE "" END AS invoice_date,
        	 CASE WHEN rn = 1 THEN kgs ELSE NULL END AS kgs,
    CASE WHEN rn = 1 THEN nos ELSE NULL END AS nos
	FROM (
		SELECT
			jc.name        AS job_card,
			tc.name        AS test_certificate,
			dli.parent     AS delivery_note,
			si.name        AS sales_invoice,
			si.posting_date AS invoice_date,
                   round(tc.accepted_qty_in_nos,2) AS nos,
        round(tc.accepted_qty_in_kgs,2) AS kgs,

			ROW_NUMBER() OVER (
				PARTITION BY dli.parent
				ORDER BY si.posting_date DESC
			) AS si_rank,

			ROW_NUMBER() OVER (
				PARTITION BY jc.name
				ORDER BY dli.parent
			) AS rn

		FROM `tabJob Card for process` jc

		LEFT JOIN `tabTest Certificate entry` tc
			ON tc.job_card_id = jc.name
			AND tc.docstatus = 1

		LEFT JOIN `tabDelivery Note Item` dli
			ON dli.customer_dc_id = jc.customer_dc
			AND dli.part_no = jc.part_no
			AND dli.docstatus = 1

		LEFT JOIN `tabSales Invoice Item` sie
			ON sie.customer_dc_id = jc.customer_dc
			AND sie.part_no = jc.part_no
			AND sie.docstatus = 1

		LEFT JOIN `tabSales Invoice` si
			ON si.name = sie.parent
			AND si.docstatus = 1

		WHERE jc.name = "{0}"
	) x
	WHERE si_rank = 1          
	ORDER BY delivery_note;
	""".format(doc.name)
		
	return frappe.db.sql(sql,as_dict=1)
