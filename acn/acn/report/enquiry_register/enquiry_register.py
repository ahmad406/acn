import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data


def get_columns():
	return [
		{"label": "Date of Enquiry", "fieldname": "transaction_date", "fieldtype": "Date",     "width": 120},
		{"label": "Enquiry Type",    "fieldname": "enquiry_type",     "fieldtype": "Data",     "width": 120},
		{"label": "Source",          "fieldname": "source",           "fieldtype": "Data",     "width": 110},
		{"label": "Customer Name",   "fieldname": "customer_name",    "fieldtype": "Link",     "options": "Lead", "width": 160},
		{"label": "Sector",          "fieldname": "industry",         "fieldtype": "Data",     "width": 120},
		{"label": "Territory",       "fieldname": "territory",        "fieldtype": "Data",     "width": 120},
		{"label": "Contact Person",  "fieldname": "contact_person",   "fieldtype": "Data",     "width": 140},
		{"label": "Contact No",      "fieldname": "mobile_no",        "fieldtype": "Data",     "width": 120},
		{"label": "E-Mail ID",       "fieldname": "email_id",         "fieldtype": "Data",     "width": 160},
		{"label": "Process",         "fieldname": "process",          "fieldtype": "Data",     "width": 180},
		{"label": "Quotation",       "fieldname": "quotation_name",   "fieldtype": "Link",     "options": "Quotation", "width": 140},
		{"label": "Rates Quoted",    "fieldname": "rates_quoted",     "fieldtype": "Currency", "width": 130},
		{"label": "Total Value",     "fieldname": "total_value",      "fieldtype": "Currency", "width": 130},
		{"label": "Enq Status",      "fieldname": "status",           "fieldtype": "Data",     "width": 120},
		{"label": "Remarks",         "fieldname": "remarks",          "fieldtype": "Data",     "width": 240},
	]


def get_data():
	leads = frappe.db.sql("""
		SELECT
			l.name       AS lead_id,
			l.first_name AS customer_name,
			l.creation   AS transaction_date,
			l.enquiry_type,
			l.source,
			l.industry,
			l.territory,
			l.first_name AS contact_person,
			l.mobile_no,
			l.email_id,
			l.status
		FROM `tabLead` l
		ORDER BY l.creation DESC
	""", as_dict=True)

	if not leads:
		return []

	lead_ids = [l.lead_id for l in leads]
	ph_leads = ", ".join(["%s"] * len(lead_ids))

	opp_meta_map  = {}
	opp_items_map = {}
	lead_opps_map = {}

	opp_rows = frappe.db.sql("""
		SELECT
			o.name               AS opp_id,
			o.party_name         AS lead_id,
			o.opportunity_amount AS total_value,
			oi.item_name         AS process
		FROM `tabOpportunity` o
		LEFT JOIN `tabOpportunity Item` oi ON oi.parent = o.name
		WHERE o.opportunity_from = 'Lead'
		  AND o.party_name IN ({ph})
		ORDER BY o.name, oi.idx
	""".format(ph=ph_leads), lead_ids, as_dict=True)

	for o in opp_rows:
		if o.opp_id not in opp_meta_map:
			opp_meta_map[o.opp_id] = {
				"lead_id":     o.lead_id,
				"total_value": o.total_value
			}
			lead_opps_map.setdefault(o.lead_id, [])
			if o.opp_id not in lead_opps_map[o.lead_id]:
				lead_opps_map[o.lead_id].append(o.opp_id)
		if o.process:
			opp_items_map.setdefault(o.opp_id, []).append(o.process)

	qtn_map = {}

	opp_ids = list(opp_meta_map.keys())
	if opp_ids:
		ph_opps = ", ".join(["%s"] * len(opp_ids))

		qtn_rows = frappe.db.sql("""
			SELECT
				q.name AS quotation_name,
				q.opportunity AS opp_id,
				qi.rate AS rates_quoted
			FROM `tabQuotation` q
			LEFT JOIN `tabQuotation Item` qi
				ON qi.parent = q.name AND qi.idx = 1
			WHERE q.opportunity IN ({ph})
			  AND q.docstatus != 2
		""".format(ph=ph_opps), opp_ids, as_dict=True)

		for q in qtn_rows:
			qtn_map.setdefault(q.opp_id, []).append(q)

	remarks_map = {}

	if opp_ids:
		ph_opps = ", ".join(["%s"] * len(opp_ids))

		task_rows = frappe.db.sql("""
			SELECT
				reference_name AS opp_id,
				GROUP_CONCAT(description ORDER BY creation SEPARATOR ' | ') AS val
			FROM `tabTask`
			WHERE reference_type = 'Opportunity'
			  AND reference_name IN ({ph})
			GROUP BY reference_name
		""".format(ph=ph_opps), opp_ids, as_dict=True)

		comment_rows = frappe.db.sql("""
			SELECT
				reference_name AS opp_id,
				GROUP_CONCAT(content ORDER BY creation SEPARATOR ' | ') AS val
			FROM `tabComment`
			WHERE reference_doctype = 'Opportunity'
			  AND comment_type      = 'Comment'
			  AND reference_name   IN ({ph})
			GROUP BY reference_name
		""".format(ph=ph_opps), opp_ids, as_dict=True)

		for row in task_rows + comment_rows:
			if row.val:
				remarks_map.setdefault(row.opp_id, []).append(row.val)

	result = []

	for lead in leads:
		opp_ids_for_lead = lead_opps_map.get(lead.lead_id)

		if not opp_ids_for_lead:
			result.append(make_row(lead, None, None, None, ""))
			continue

		for opp_id in opp_ids_for_lead:
			meta    = opp_meta_map[opp_id]
			items   = opp_items_map.get(opp_id) or [None]
			qtns    = qtn_map.get(opp_id) or [None]
			remarks = " | ".join(remarks_map.get(opp_id, []))

			for item in items:
				for qtn in qtns:
					result.append(make_row(lead, meta, item, qtn, remarks))

	return result


def make_row(lead, opp_meta, item, qtn, remarks):
	return {
		"transaction_date": lead.transaction_date,
		"enquiry_type":     lead.enquiry_type,
		"source":           lead.source,
		"customer_name":    lead.lead_id,
		"industry":         lead.industry,
		"territory":        lead.territory,
		"contact_person":   lead.contact_person,
		"mobile_no":        lead.mobile_no,
		"email_id":         lead.email_id,
		"process":          item or "",
		"quotation_name":   qtn.quotation_name if qtn else "",
		"rates_quoted":     qtn.rates_quoted   if qtn else 0,
		"total_value":      opp_meta["total_value"] if opp_meta else 0,
		"status":           lead.status,
		"remarks":          remarks,
	}