// Copyright (c) 2025, Ahmad Sayyed and contributors
// For license information, please see license.txt

frappe.ui.form.on("Subcontract Delivery Note", {
    refresh(frm) {

    },
    setup: function (frm) {
        cur_frm.set_query("work_order_no", function (frm) {
            return {
                filters: [
                    ['Purchase Order', 'naming_series', '=', 'WO.#####'],
                    ['Purchase Order', 'docstatus', '=', 1],
                    ['Purchase Order', 'supplier', '=', cur_frm.doc.subcontractor]

                ]
            }
        });
        cur_frm.set_query("service_name", "items", function (frm, cdt, cdn) {
            return {
                query: 'acn.acn.doctype.subcontract_delivery_note.subcontract_delivery_note.get_items',
                filters: { "work": cur_frm.doc.work_order_no }

            }
        });
        cur_frm.set_query("part_no", "items", function (frm, cdt, cdn) {
            let d = locals[cdt][cdn];
            return {
                query: 'acn.acn.doctype.subcontract_delivery_note.subcontract_delivery_note.get_part_no',
                filters: {
                    customer_dc_id: d.customer_dc_id
                }
            };
        });

    },
    subcontractor: function (frm) {
        cur_frm.set_value("work_order_no", undefined)
        cur_frm.set_value("items", [])
    }
});
frappe.ui.form.on("Subcontract Delivery Item", {
    service_name: function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];

        frappe.call({
            method: "get_item_details",
            doc: frm.doc,
            args: {
                "row": d
            },
            callback: function (r) {
                if (r.message) {

                    frappe.model.set_value(cdt, cdn, "rate", r.message.rate);
                    frappe.model.set_value(cdt, cdn, "rate_uom", r.message.rate_uom);
                    frappe.model.set_value(cdt, cdn, "description", r.message.description);
                    frappe.model.set_value(cdt, cdn, "item_tax_template", r.message.item_tax_template);
                    frappe.model.set_value(cdt, cdn, "expense_account", r.message.expense_account);
                    frappe.model.set_value(cdt, cdn, "sub_account", r.message.sub_account);
                    frappe.model.set_value(cdt, cdn, "cost_center", r.message.cost_center);


                    frm.refresh_field("items");
                }
            }
        });
    },
    customer_dc_id:function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        d.part_no=undefined
    },
    part_no:function (frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        frappe.call({
            method: "get_dc_details",
            doc: frm.doc,
            args: {
                "row": d
            },
            callback: function (r) {
                if (r.message) {
                     
                    frappe.model.set_value(cdt, cdn, "customer_name", r.message.customer_name);
                    frappe.model.set_value(cdt, cdn, "process_name", r.message.process_name);
                    frappe.model.set_value(cdt, cdn, "dc_qty_nos", r.message.dc_qty_nos);
                    frappe.model.set_value(cdt, cdn, "dc_qty_kgs", r.message.dc_qty_kgs);
            

                    frm.refresh_field("items");
                }
            }
        });


    },


})