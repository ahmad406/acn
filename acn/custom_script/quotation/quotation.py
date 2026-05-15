import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import flt



def update_opportunity_amount(doc):
	try:
		if not doc.opportunity:
			return

		amount = sum(
			flt(item.opportunity_value)
			for item in doc.items
		)

		valuation_type = (
			"High Value"
			if amount >= 100000
			else "Low Value"
		)

		frappe.db.set_value(
			"Opportunity",
			doc.opportunity,
			{
				"opportunity_amount": amount,
				"opportunity_valuation_type": valuation_type
			}
		)

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Opportunity Update Failed - {doc.name}"
		)


def send_quotation_with_letterhead(doc, method):


    update_opportunity_amount(doc)

    letter_head = frappe.db.get_value("Letter Head", {"is_default": 1}, "name")

    html = frappe.get_print(
        doc.doctype,
        doc.name,
        print_format="Quotation-New",
        letterhead=letter_head
    )
    pdf_content = get_pdf(html)

    notification = frappe.get_doc("Notification", "quotation")

    # Parse comma-separated emails into a clean list
    if not doc.contact_email:
        frappe.log_error(f"No contact_email on {doc.name}, skipping notification", "Quotation Email")
        return

    recipients = [e.strip() for e in doc.contact_email.split(",") if e.strip()]

    if not recipients:
        frappe.log_error(f"No valid emails parsed from contact_email on {doc.name}", "Quotation Email")
        return

    # Fetch CC from notification recipients row
    cc = []
    for r in notification.recipients:
        if r.cc:
            cc_emails = [e.strip() for e in r.cc.split("\n") if e.strip()]
            cc.extend(cc_emails)

    attachments = [{
        "fname": f"{doc.name}.pdf",
        "fcontent": pdf_content
    }]

    attached_files = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": doc.doctype,
            "attached_to_name": doc.name
        },
        fields=["name", "file_name"]
    )

    for f in attached_files:
        file_doc = frappe.get_doc("File", f.name)
        attachments.append({
            "fname": f.file_name,
            "fcontent": file_doc.get_content()
        })

    frappe.log_error(
        f"Recipients: {recipients}\nCC: {cc}\nAttachments: {[a['fname'] for a in attachments]}",
        "Quotation Email Debug"
    )

    frappe.sendmail(
        recipients=recipients,
        cc=cc,
        subject=f"Quotation {doc.name} from {doc.company}",
        message=get_email_body(doc),
        attachments=attachments,
        expose_recipients="header"
    )


def get_email_body(doc):
    notification = frappe.get_doc("Notification", "quotation")
    context = frappe.get_doc("Quotation", doc.name).as_dict()
    return frappe.render_template(notification.message, {"doc": context, "frappe": frappe})



def reset_opportunity_amount(doc, method=None):
	try:
		if not doc.opportunity:
			return

		frappe.db.set_value(
			"Opportunity",
			doc.opportunity,
			{
				"opportunity_amount": 0,
				"opportunity_valuation_type": "Low Value"
			}
		)

	except Exception:
		frappe.log_error(
			frappe.get_traceback(),
			f"Opportunity Reset Failed - {doc.name}"
        )