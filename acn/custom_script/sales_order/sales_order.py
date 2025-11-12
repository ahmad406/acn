
import frappe

def validate(self,method=None):
	for d in self.get("items"):
		d.custom_bal_qty_in_kgs=d.custom_qty_in_kgs
		d.custom_bal_qty_in_nos=d.custom_qty_in_nos

		# if d.custom_part_no and self.customer:
		# 	process_details = get_process_rate(d.custom_part_no, self.customer)
		# 	d.custom_process_type = process_details.process_type
		# 	d.custom_process_name = process_details.process_name
		# 	d.material = process_details.material
		# 	d.custom_rate_uom = process_details.rate_uom
		# 	d.item_code= process_details.item_code
		# 	d.rate = process_details.process_rate
		# 	d.custom_customer_process_ref_no = process_details.customer_ref
		# 	d.custom_bal_qty_in_kgs=d.custom_qty_in_kgs
		# 	d.custom_bal_qty_in_nos=d.custom_qty_in_nos
			# if process_details.rate_uom=="Minimum":
			# 	d.qty=1
			# elif process_details.rate_uom=="Nos":

			# 	d.qty=d.custom_qty_in_nos
			# elif process_details.rate_uom=="Kgs":
			# 	d.qty=d.custom_qty_in_kgs
			# else:
			# 	frappe.throw("Invalid Rate UOM: {0}".format(process_details.rate_uom))

@frappe.whitelist()
def before_submit(self, method=None):
    if self.reopen:
        frappe.throw("This Purchase Order is reopened. You cannot submit it. Please click on Re-Close first.")

@frappe.whitelist()
def reopen_order(name,docstatus=0):
    """
    Reopen a submitted Purchase Order by setting flags
    """
    try:
        docstatus = int(docstatus)
        po = frappe.get_doc("Sales Order", name)
        
      
        po.db_set("docstatus",docstatus)
        po.db_set("reopen", 0 if docstatus else 1)


        for d in  po.items:
            d.db_set("docstatus",docstatus)
        for d in  po.taxes:
            d.db_set("docstatus",docstatus)


        frappe.db.commit()

        return {"status": "success", "message": f"Sales  Order {name} reopened successfully."}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Reopen Sales Order Error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_process_rate(part_no, customer):
	result = frappe.db.sql("""
		SELECT c.process_rate, c.rate_uom,p.process_type,p.process_name,p.material,p.item_code,p.customer_ref,p.item_name,p.item_name
		FROM `tabCustomer Process` p
		INNER JOIN `tabPart No  Process Rate` c ON p.name = c.parent
		WHERE c.part_no = %s AND p.customer = %s
		LIMIT 1
	""", (part_no, customer), as_dict=True)
	if result:
		return result[0]
	else:
		frappe.throw("Customer Process not found for <b>Part:no {0}  and Customer: {1} </b>".format(part_no, customer))



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_part_no(doctype, txt, searchfield, start, page_len, filters):
    customer = filters.get('customer') if filters else None
    if not customer:
        return []

    args = {
        'start': start,
        'customer': customer,
        'page_len': page_len,
        'txt': '%%%s%%' % txt
    }

    part = frappe.db.sql("""
				
SELECT 
    p.name, 
    c.item_code, 
    c.item_name, 
    c.process_name, 
    c.customer_ref 
FROM 
    `tabPart no` p 
INNER JOIN 
    `tabPart No  Process Rate` pp ON p.name = pp.part_no 
INNER JOIN 
    `tabCustomer Process` c ON pp.parent = c.name
WHERE 
    pp.parenttype = 'Customer Process' and  p.customer= %(customer)s 
						 and p.name LIKE %(txt)s
ORDER BY p.name ASC


LIMIT %(start)s, %(page_len)s




        
    """, args)

    return part
