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

    recipient = doc.contact_email
    if not recipient:
        frappe.log_error(f"No contact_email on {doc.name}, skipping notification", "Quotation Email")
        return

    frappe.sendmail(
        recipients=[recipient],
        subject=f"Quotation {doc.name} from {doc.company}",
        message=get_email_body(doc),
        attachments=[{
            "fname": f"{doc.name}.pdf",
            "fcontent": pdf_content
        }]
    )


def get_email_body(doc):
    valid_till = frappe.utils.formatdate(doc.valid_till) if doc.valid_till else "—"
    transaction_date = frappe.utils.formatdate(doc.transaction_date)

    return f"""
<p>Dear {doc.contact_person},</p>
<p>Thank you for your enquiry. We have studied your requirements of heat treatment and our confident of undertaking the same to your satisfaction.</br></p>
The detailed price offer is as follows:</br>
<ul>
  <li><b>Quotation No:</b> {doc.name} (Please find attached)</li>
  <li><b>Date:</b> {transaction_date}</li>
  <li><b>Valid Till:</b> {valid_till}</li>
</ul>
</br>
<p>We hope our offer is competitive and look forward to your valuable purchase order</p></br></br>
<div style="font-style: italic; line-height: 1.5;">
Regards,<br>
<b>Sunny William</b><br>
Marketing & Sales<br>
<b>Cell:</b> <a href="tel:+917411918957">7411918957</a><br>
<b style="font-size:16px;">ACE CARBO NITRIDERS</b><br>
No.145-A, 3 rd. Cross, 1 st. Stage, Peenya Industrial Estate<br>
BANGALORE-56058.<br>
<a href="mailto:marketing@acecarbo.in">E-Mail</a> | 
<a href="http://www.acecarbo.in/">Website</a> | 
<a href="https://youtu.be/aadWZJSjH5Y">YouTube</a> | 
<a href="https://www.facebook.com/acecarbonitri">Facebook</a> | 
<a href="https://www.linkedin.com/in/ace-carbo-nitriders-acn-392602232">LinkedIn</a>
</div>
"""