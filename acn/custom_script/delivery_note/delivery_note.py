
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


def on_submit(self, method=None):
	update_qty(self, is_cancel=False)

def validate(self, method=None):
    errors = []

    for d in self.items:
        if d.qty > d.balance_qty_in_nos:
            errors.append(
                f"Item {d.item_code}: Quantity ({d.qty}) exceeds available Balance Qty ({d.balance_qty_in_nos})"
            )
        elif d.qty < d.balance_qty_in_nos:
            errors.append(
                f"Item {d.item_code}: Quantity ({d.qty}) is less than the available Balance Qty ({d.balance_qty_in_nos})"
            )

    if errors:
        frappe.throw(
            "The following items have quantity issues:\n\n" + "\n".join(errors)
        )



def on_cancel(self, method=None):
	update_qty(self, is_cancel=True)

def update_qty(self, is_cancel=False):
	for d in self.items:
		dc = frappe.get_doc("Customer DC", d.customer_dc_id)
		for c in dc.items:
			frappe.errprint([ c.part_no == d.part_no, c.part_no , d.part_no])
			if c.part_no == d.part_no:

				new_qty = c.delivered_qty - d.qty if is_cancel else c.delivered_qty + d.qty
				new_qty_kgs = c.delivery_qty_kgs - d.d_qty_in_kgs if is_cancel else c.delivery_qty_kgs + d.d_qty_in_kgs
				c.db_set("delivered_qty", new_qty)
				c.db_set("delivery_qty_kgs", new_qty_kgs)


@frappe.whitelist()
def get_part_no_details(part_no, customer_dc):
	if not customer_dc or not part_no:
		return None  
	try:
		doc = frappe.get_doc("Customer DC", customer_dc)
	except frappe.DoesNotExistError:
		return None

	for d in doc.items:
		if d.part_no == part_no:
			
			row_dict = d.as_dict()
			item_doc = frappe.get_doc("Item", d.item_code)
			d.uom = item_doc.stock_uom
			delivery_qty = float(d.delivered_qty)
			delivery_qty_kgs = float(d.delivery_qty_kgs)

			balance_qty_nos = d.balance_qty_nos - delivery_qty
			balance_qty_kgs = d.balance_qty_kgs - delivery_qty_kgs

			

			
			row_dict["uom"] = item_doc.stock_uom
			row_dict["balance_qty_nos"] = balance_qty_nos
			row_dict["balance_qty_kgs"] = balance_qty_kgs
			row_dict["balance_qty_kgs"] = balance_qty_kgs
			row_dict["customer_ref_no"] = doc.ref_no
			row_dict["so_date"] = doc.ref_date






			
		   
			return row_dict

	return None



			
		
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_customer_dc(doctype, txt, searchfield, start, page_len, filters):
	customer = filters.get('customer')

	args = {
		"start": start,
		"page_len": page_len,
		"txt": f"%{txt}%",
		"customer": customer
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
			 c.balance_qty_nos- c.delivered_qty >0
			AND p.customer = %(customer)s
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
		   c.balance_qty_nos- c.delivered_qty >0 and
			p.name = %(customer_dc)s
			AND c.part_no LIKE %(txt)s
		GROUP BY c.part_no
		LIMIT %(start)s, %(page_len)s
	"""

	# Debug: log the query and args in Frappe error log
	frappe.log_error(message=f"Query: {query}\nArgs: {args}", title="get_part_no Debug")

	return frappe.db.sql(query, args)


