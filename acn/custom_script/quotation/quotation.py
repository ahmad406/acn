import frappe
from frappe.utils.pdf import get_pdf

def send_quotation_with_letterhead(doc, method):
    letter_head = frappe.db.get_value("Letter Head", {"is_default": 1}, "name")

    html = frappe.get_print(
        doc.doctype,
        doc.name,
        print_format="Quotation-New",
        letterhead=letter_head
    )
    pdf_content = get_pdf(html)

    # Fetch notification
    notification = frappe.get_doc("Notification", "quotation")

    recipient = doc.contact_email
    if not recipient:
        frappe.log_error(f"No contact_email on {doc.name}, skipping notification", "Quotation Email")
        return

    # Fetch CC from notification recipients row
    cc = []
    for r in notification.recipients:
        if r.cc:
            cc_emails = [e.strip() for e in r.cc.split("\n") if e.strip()]
            cc.extend(cc_emails)

    # Start attachments with letterhead PDF
    attachments = [{
        "fname": f"{doc.name}.pdf",
        "fcontent": pdf_content
    }]

    # Fetch all files attached to this Quotation
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
        f"Recipients: {[recipient]}\nCC: {cc}\nAttachments: {[a['fname'] for a in attachments]}",
        "Quotation Email Debug"
    )

    frappe.sendmail(
        recipients=[recipient],
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