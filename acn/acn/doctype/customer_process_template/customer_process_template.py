# Copyright (c) 2025, Ahmad Sayyed and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document


class CustomerProcesstemplate(Document):
	@frappe.whitelist()
	def get_parameter(self):
		if self.process_type:
			p_type=frappe.get_doc("Process Type",self.process_type)
			self.set("parameters_with_acceptance_criteria",[])
			for d in p_type.process_parameter:
				row=self.append("customer_requirements",{})
				row.process_parameter=d.process_parameter
		return True


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_param(doctype, txt, searchfield, start, page_len, filters):
    args = {
        "start": start,
        "process_type": filters.get("process_type"),
        "page_len": page_len,
        "txt": f"%{txt}%",  # This is the correct way to use wildcards
    }

    param = frappe.db.sql(
        """
        SELECT DISTINCT c.process_parameter 
        FROM `tabProcess Type` p 
        INNER JOIN `tabProcess Parameter` c ON p.name = c.parent 
        WHERE p.name = %(process_type)s 
        AND c.process_parameter LIKE %(txt)s
        LIMIT %(start)s, %(page_len)s
        """,
        args,
    )

    return param

