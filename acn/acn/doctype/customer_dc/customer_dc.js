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
    setup:function(frm){
        cur_frm.cscript.onload = function   (){
            cur_frm.set_query("part_no", "items", function (frm, cdt, cdn) {
                var child = locals[cdt][cdn];
                    return {
                        query: 'acn.acn.doctype.customer_dc.customer_dc.get_part_no',
                        filters: {"sales_order":cur_frm.doc.sales_order_no
                        }
        
                    }
                });
            }

    },

    calculate_total: function (frm) {
        var total = 0;
        $.each(frm.doc.items || [], function (i, d) {
            if (d.qty) {
                total += d.qty;
            }
        });
        frm.set_value("total_qty", total);
    },
});


frappe.ui.form.on("Customer DC child", {
    qty_nos: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        console.log("qty_nos", item.qty_nos);

        item.qty = item.qty_nos;
        cur_frm.refresh()

    },
    qty_kgs: function (frm, cdt, cdn) {
        var item = locals[cdt][cdn];
        console.log("qty_kgs", item.qty_kgs);
        item.qty = item.qty_kgs;
        cur_frm.refresh()
    },
    part_no:function(frm,cdt,cdn){
        var d = locals[cdt][cdn];
        frappe.call({
            method: "set_part_no_details",
            args:{row:d},
			doc: cur_frm.doc,
            callback: function(r) {
                if (r.message) {
                   cur_frm.refresh()
                }
            }
        });


    }

});