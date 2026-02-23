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


import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_dispatch_details(doc):

    if isinstance(doc, str):
        jc = frappe.get_doc("Job Card for process", doc)
    else:
        jc = doc

    tcs = frappe.get_all(
        "Test Certificate entry",
        filters={
            "job_card_id": jc.name,
            "docstatus": 1
        },
        fields=["name"],
        order_by="name"
    )

    dns = frappe.db.sql("""
        SELECT DISTINCT parent
        FROM `tabDelivery Note Item`
        WHERE customer_dc_id = %s
        AND part_no = %s
        AND docstatus = 1
        ORDER BY parent
    """, (jc.customer_dc, jc.part_no), as_dict=True)

    sis = frappe.db.sql("""
        SELECT 
            si.name,
            si.posting_date,
            sie.d_qty_in_nos,
            sie.d_qty_in_kgs
        FROM `tabSales Invoice Item` sie
        JOIN `tabSales Invoice` si ON si.name = sie.parent
        WHERE sie.customer_dc_id = %s
        AND sie.part_no = %s
        AND si.docstatus = 1
        ORDER BY si.posting_date
    """, (jc.customer_dc, jc.part_no), as_dict=True)

    max_len = max(len(tcs), len(dns), len(sis))

    result = []

    for i in range(max_len):
        row = {}

        row["test_certificate"] = tcs[i]["name"] if i < len(tcs) else ""

        row["delivery_note"] = dns[i]["parent"] if i < len(dns) else ""

        if i < len(sis):
            row["sales_invoice"] = sis[i]["name"]
            row["invoice_date"] = (
                sis[i]["posting_date"].strftime("%d-%m-%Y")
                if sis[i]["posting_date"] else ""
            )
            row["nos"] = flt(sis[i]["d_qty_in_nos"], 2)
            row["kgs"] = flt(sis[i]["d_qty_in_kgs"], 2)
        else:
            row["sales_invoice"] = ""
            row["invoice_date"] = ""
            row["nos"] = ""
            row["kgs"] = ""

        result.append(row)

    return result

# @frappe.whitelist()
# def get_dispatch_details(doc):
# 	sql="""SELECT
# 		CASE WHEN rn = 1 THEN job_card ELSE "" END AS job_card,
# 		CASE WHEN rn = 1 THEN test_certificate ELSE "" END AS test_certificate,
# 		delivery_note,
# 		CASE WHEN rn = 1 THEN sales_invoice ELSE "" END AS sales_invoice,
# 		CASE WHEN rn = 1  THEN DATE_FORMAT(invoice_date, '%d-%m-%Y') ELSE "" END AS invoice_date,
#         	 CASE WHEN rn = 1 THEN kgs ELSE NULL END AS kgs,
#     CASE WHEN rn = 1 THEN nos ELSE NULL END AS nos
# 	FROM (
# 		SELECT
# 			jc.name        AS job_card,
# 			tc.name        AS test_certificate,
# 			dli.parent     AS delivery_note,
# 			si.name        AS sales_invoice,
# 			si.posting_date AS invoice_date,
#                    round(tc.accepted_qty_in_nos,2) AS nos,
#         round(tc.accepted_qty_in_kgs,2) AS kgs,

# 			ROW_NUMBER() OVER (
# 				PARTITION BY dli.parent
# 				ORDER BY si.posting_date DESC
# 			) AS si_rank,

# 			ROW_NUMBER() OVER (
# 				PARTITION BY jc.name
# 				ORDER BY dli.parent
# 			) AS rn

# 		FROM `tabJob Card for process` jc

# 		LEFT JOIN `tabTest Certificate entry` tc
# 			ON tc.job_card_id = jc.name
# 			AND tc.docstatus = 1

# 		LEFT JOIN `tabDelivery Note Item` dli
# 			ON dli.customer_dc_id = jc.customer_dc
# 			AND dli.part_no = jc.part_no
# 			AND dli.docstatus = 1

# 		LEFT JOIN `tabSales Invoice Item` sie
# 			ON sie.customer_dc_id = jc.customer_dc
# 			AND sie.part_no = jc.part_no
# 			AND sie.docstatus = 1

# 		LEFT JOIN `tabSales Invoice` si
# 			ON si.name = sie.parent
# 			AND si.docstatus = 1

# 		WHERE jc.name = "{0}"
# 	) x
# 	WHERE si_rank = 1          
# 	ORDER BY delivery_note;
# 	""".format(doc.name)
		
# 	return frappe.db.sql(sql,as_dict=1)
