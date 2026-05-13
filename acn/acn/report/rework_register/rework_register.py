# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("Customer DC No"),
            "fieldname": "customer_dc",
            "fieldtype": "Link",
            "options": "Customer DC",
            "width": 180
        },
		{
            "label": _("Job Card ID"),
            "fieldname": "job_card_id",
            "fieldtype": "Link",
            "options": "Job Card",
            "width": 180
        },
        {
            "label": _("Date"),
            "fieldname": "tran_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
       
        {
            "label": _("Part Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("Part No"),
            "fieldname": "part_no",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Qty Nos"),
            "fieldname": "qty_nos",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Qty Kgs"),
            "fieldname": "qty_kgs",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Non Conformance"),
            "fieldname": "non_conformance",
            "fieldtype": "Data",
            "width": 300
        },
        {
            "label": _("Type Of Rework"),
            "fieldname": "type_of_rework",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Gross Value Of Goods"),
            "fieldname": "gross_value_of_goods",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Root Cause"),
            "fieldname": "root_cause",
            "fieldtype": "Small Text",
            "width": 250
        },
        {
            "label": _("Action Plan"),
            "fieldname": "action_plan",
            "fieldtype": "Small Text",
            "width": 300
        },
        {
            "label": _("Responsibility"),
            "fieldname": "responsibility",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Commitment Date"),
            "fieldname": "commitment_date",
            "fieldtype": "Date",
            "width": 130
        },
        {
            "label": _("Effectiveness"),
            "fieldname": "effectiveness",
            "fieldtype": "Data",
            "width": 250
        },
        {
            "label": _("Remarks"),
            "fieldname": "rework_remarks",
            "fieldtype": "Small Text",
            "width": 250
        },
    ]


def get_data(filters):
    conditions = ""

    if filters.get("from_date"):
        conditions += " AND dc.tran_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND dc.tran_date <= %(to_date)s"

    data = frappe.db.sql(
        f"""
        SELECT
            dc.name AS customer_dc,
            dc.tran_date,
            dc.customer,

            jcp.name AS job_card_id,

            child.item_name,
            child.part_no,
            child.qty_nos,
            child.qty_kgs,
            child.non_conformance,
            child.type_of_rework,
            child.gross_value_of_goods,
            child.root_cause,
            child.action_plan,
            child.responsibility,
            child.commitment_date,
            child.effectiveness,
            child.rework_remarks

        FROM `tabCustomer DC child` child

        INNER JOIN `tabCustomer DC` dc
            ON dc.name = child.parent

        LEFT JOIN `tabJob Card for process` jcp
            ON jcp.customer_dc = dc.name

        WHERE
            dc.docstatus = 1
            {conditions}

        ORDER BY
            dc.tran_date DESC,
            dc.name DESC
        """,
        filters,
        as_dict=1
    )

    return data