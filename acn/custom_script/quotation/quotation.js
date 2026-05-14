frappe.ui.form.on("Quotation Item", {
    uom_rate: function (frm, cdt, cdn) {
        set_main_qty(frm, cdt, cdn);
    },
    qty_in_nos: function (frm, cdt, cdn) {
        set_main_qty(frm, cdt, cdn);
    },
    qty_in_kgs: function (frm, cdt, cdn) {
        set_main_qty(frm, cdt, cdn);
    }
});

function set_main_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.uom_rate == "Nos") {
        frappe.model.set_value(cdt, cdn, "qty", row.qty_in_nos || 0);

    } else if (row.uom_rate == "Kgs") {
        frappe.model.set_value(cdt, cdn, "qty", row.qty_in_kgs || 0);

    } else if (row.uom_rate == "Minimum") {
        frappe.model.set_value(cdt, cdn, "qty", 1);
    }
}