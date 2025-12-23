frappe.ui.form.on("Customer DC", {
    refresh: function (frm) {
        cur_frm.trigger("calculate_total");
        // if (frm.doc.docstatus == 0) {
        //     frm.add_custom_button(__('Sales Order'), function () {
        //         if (!frm.doc.sales_order_no) {
        //             frappe.throw({
        //                 title: __("Mandatory"),
        //                 message: __("Please select a Sales Order before fetching items.")
        //             });
        //         }
        //         cur_frm.doc.items = []
        //         erpnext.utils.map_current_doc({
        //             method: "acn.acn.doctype.customer_dc.customer_dc.map_sales_order_to_customer_dc",
        //             source_doctype: "Sales Order",
        //             target: frm,
        //             allow_multiple: false,
        //             setters: {
        //                 customer: frm.doc.customer,
        //             },
        //             get_query_filters: {
        //                 name: frm.doc.sales_order_no,
        //                 docstatus: 1
        //             }
        //         });

        //     }, __("Get Items From"));
        // }
    },
    setup: function (frm) {
        cur_frm.cscript.onload = function () {
            cur_frm.set_query("part_no", "items", function (frm, cdt, cdn) {
                var child = locals[cdt][cdn];
                let selected_parts = [];
                (cur_frm.doc.items || []).forEach(row => {
                    if (row.part_no && row.name !== cdn) {
                        selected_parts.push(row.part_no);
                    }
                });
                console.log(selected_parts)

                return {
                    query: 'acn.acn.doctype.customer_dc.customer_dc.get_part_no',
                    filters: {
                        sales_order: cur_frm.doc.sales_order_no,
                        exclude_parts: selected_parts
                    }

                }
            });

        }
        cur_frm.set_query("sales_order_no", function (frm) {
            return {
                filters: {
                    customer: cur_frm.doc.customer,
                    docstatus: 1
                }
            };
        });


    },

    calculate_total: function (frm) {
        if (cur_frm.doc.docstatus == 0) {
            var total_nos = 0;
            var total_kgs = 0;

            $.each(frm.doc.items || [], function (i, d) {
                if (d.qty_nos) {
                    total_nos += d.qty_nos;
                }
                if (d.qty_kgs) {
                    total_kgs += d.qty_kgs;
                }
            });

            frm.set_value("total_qty__nos", total_nos);
            frm.set_value("total_qty", total_kgs);
        }
    },
});


frappe.ui.form.on("Customer DC child", {
    qty_nos: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        console.log("qty_nos", item.qty_nos);

        item.qty = item.qty_nos;
        calculate_eway_bill_rate(frm, cdt, cdn);
        cur_frm.refresh()

    },
    qty_kgs: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        console.log("qty_kgs", item.qty_kgs);
        item.qty = item.qty_kgs;
        calculate_eway_bill_rate(frm, cdt, cdn);
        cur_frm.refresh()
    },
    part_no: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        frappe.call({
            method: "set_part_no_details",
            args: { row: d },
            doc: cur_frm.doc,
            callback: function (r) {
                if (r.message) {
                    calculate_eway_bill_rate(frm, cdt, cdn);
                    cur_frm.refresh()
                }
            }
        });


    },
    rate_uom: function (frm, cdt, cdn) {
        calculate_eway_bill_rate(frm, cdt, cdn);
        cur_frm.refresh()

    },
    gross_value_of_goods: function (frm, cdt, cdn) {
        calculate_eway_bill_rate(frm, cdt, cdn);
        cur_frm.refresh()

    },

});




function calculate_eway_bill_rate(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    // console.log("in", row.rate_uom)
    let gross = row.gross_value_of_goods || 0;
    let rate = 0;

    if (row.rate_uom === "Nos") {
        rate = row.qty_nos
            ? gross / row.qty_nos
            : 0;

    } else if (row.rate_uom === "Kgs") {
        rate = row.qty_kgs
            ? gross / row.qty_kgs
            : 0;

    } else if (row.rate_uom === "Minimum") {
        rate = gross;

    }


    frappe.model.set_value(cdt, cdn, "e_rate", rate);
}
