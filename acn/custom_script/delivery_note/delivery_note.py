
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


def on_submit(self, method=None):
	update_qty(self, is_cancel=False)

def on_cancel(self, method=None):
	update_qty(self, is_cancel=True)

def update_qty(self, is_cancel=False):
	for d in self.items:
		dc = frappe.get_doc("Customer DC", d.customer_dc_id)
		for c in dc.items:
			if c.part_no == d.part_no:
				new_qty = c.delivered_qty - d.qty if is_cancel else c.delivered_qty + d.qty
				c.db_set("delivered_qty", new_qty)

			
		

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_dc(doctype, txt, searchfield, start, page_len, filters):
	args = {
		'start': start,
		'page_len': page_len,
		'txt': f"%{txt}%"
	}

	query = """
		SELECT 
			p.name
		FROM 
			`tabCustomer DC` p
		INNER JOIN 
			`tabCustomer DC child` c 
			ON p.name = c.parent
		WHERE 
			c.delivered_qty < c.qty_nos
			AND p.name LIKE %(txt)s
		GROUP BY p.name
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_part_no(doctype, txt, searchfield, start, page_len, filters):
	customer_dc = filters.get('customer_dc')
	args = {
		'start': start,
		'page_len': page_len,
		'customer_dc': customer_dc,
		'txt': f"%{txt}%"
	}
	query = """
		SELECT 
			c.part_no
		FROM 
			`tabCustomer DC` p
		INNER JOIN 
			`tabCustomer DC child` c 
			ON p.name = c.parent
		WHERE 
			p.name=%(customer_dc)s
			AND c.part_no LIKE %(txt)s
		GROUP BY c.part_no
		LIMIT %(start)s, %(page_len)s
	"""

	return frappe.db.sql(query, args)

