# Copyright (c) 2026, Ahmad Sayyed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CAPA(Document):

	def on_submit(self):

		for row in self.corrective_action:	

			user_id = frappe.db.get_value(
				"Employee",
				row.action_responsible,
				"user_id"
			)

			if not user_id:
				continue

			todo = frappe.new_doc("ToDo")
			todo.description = f"""
			CAPA: {self.name}

			Corrective Action:
			{row.corrective_action_note}
			"""

			todo.allocated_to = user_id
			todo.reference_type = "CAPA"
			todo.reference_name = self.name
			todo.status = "Open"

			todo.insert(ignore_permissions=True)
		
		frappe.db.set_value("Customer Complaint",self.customer_complaint_id,"capa_no",self.name)
