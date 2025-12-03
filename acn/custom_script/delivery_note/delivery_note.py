
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt


def on_submit(self, method=None):
	update_qty(self, is_cancel=False)

def validate(self, method=None):
    errors = []

    for d in self.items:
        if not d.qty or d.qty <= 0:
            errors.append(f"Item {d.item_code}: Quantity must be greater than 0")
            continue

        if d.rate_uom == "Kgs":
            if d.qty > d.balance_qty_in_kgs:
                errors.append(
                    f"Item {d.item_code}: Quantity ({d.qty}) exceeds available Balance Qty in Kgs ({d.balance_qty_in_kgs})"
                )

        elif d.rate_uom == "Nos":
            if d.qty > d.balance_qty_in_nos:
                errors.append(
                    f"Item {d.item_code}: Quantity ({d.qty}) exceeds available Balance Qty in Nos ({d.balance_qty_in_nos})"
                )

        elif d.rate_uom == "Minimum":
            if d.qty != 1:
                errors.append(
                    f"Item {d.item_code}: Quantity must be exactly 1 when Rate UOM is 'Minimum'"
                )

        else:
            errors.append(
                f"Item {d.item_code}: Unknown Rate UOM '{d.rate_uom}' — expected 'Kgs', 'Nos', or 'Minimum'"
            )

    if errors:
        frappe.throw("The following items have quantity issues:\n\n" + "\n".join(errors))
def before_validate(self,method):
      calculate_service_and_gross_values(self)

def calculate_service_and_gross_values(self):
    for row in self.items:   

        rate = row.rate or 0
        service_value = 0

        if row.rate_uom == "Nos":
            service_value = (row.d_qty_in_nos or 0) * rate

        elif row.rate_uom == "Kgs":
            service_value = (row.d_qty_in_kgs or 0) * rate

        elif row.rate_uom == "Minimum":
            service_value = rate

        row.service_value = service_value


        e_rate = row.e_rate or 0
        gross_value_of_goods = 0

        if row.rate_uom == "Nos":
            gross_value_of_goods = (row.d_qty_in_nos or 0) * e_rate

        elif row.rate_uom == "Kgs":
            gross_value_of_goods = (row.d_qty_in_kgs or 0) * e_rate

        elif row.rate_uom == "Minimum":
            gross_value_of_goods = e_rate

        row.gross_value_of_goods = gross_value_of_goods


def on_cancel(self, method=None):
	update_qty(self, is_cancel=True)

def update_qty(self, is_cancel=False):
	for d in self.items:
		dc = frappe.get_doc("Customer DC", d.customer_dc_id)

		for c in dc.items:
			if c.part_no == d.part_no:
				# use same field for add/subtract to keep logic consistent
				change_nos = d.d_qty_in_nos or 0
				change_kgs = d.d_qty_in_kgs or 0

				if is_cancel:
					new_qty = c.delivered_qty - change_nos
					new_qty_kgs = c.delivery_qty_kgs - change_kgs
				else:
					new_qty = c.delivered_qty + change_nos
					new_qty_kgs = c.delivery_qty_kgs + change_kgs

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
			row_dict["customer_ref_no"] = d.customer_process_ref_no
			row_dict["customer_dc_no"] = d.customer_dc_no
			row_dict["process_name"] = d.process_name
			row_dict["e_rate"] = d.e_rate
			row_dict["rate"] = d.rate
			row_dict["gst_hsn_code"]=d.eway_bill_hsn
			row_dict["sales_oder"]=doc.sales_order_no
			row_dict["sales_oder_item"]=d.sales_order_item







			row_dict["so_date"] = doc.order_date

			






			
		   
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
			c.part_no,c.process_name,c.material,c.customer_process_ref_no,c.customer_dc_no
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
	# frappe.log_error(message=f"Query: {query}\nArgs: {args}", title="get_part_no Debug")

	return frappe.db.sql(query, args)


