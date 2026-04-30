frappe.ui.form.on("Proforma Invoice", {
    setup: function (frm) {
        frm.set_query("customer_dc_id", function () {
            return {
                query: "acn.acn.doctype.proforma_invoice.proforma_invoice.get_customer_dc_query",
                filters: {
                    docname: frm.doc.name || ""
                }
            };
        });
    },

    customer_dc_id: function (frm) {
        if (!frm.doc.customer_dc_id) {
            frm.clear_table("proforma_invoice_table");
            frm.refresh_field("proforma_invoice_table");
            return;
        }

        frappe.db.get_doc("Customer DC", frm.doc.customer_dc_id).then(dc_doc => {
            const sales_order_no = dc_doc.sales_order_no;

            if (!dc_doc.items || dc_doc.items.length === 0) {
                frappe.msgprint(__("No items found in the selected Customer DC."));
                return;
            }

            const fetch_and_populate = (so_doc) => {
                let so_items_map_composite = {};
                let so_items_map_item = {};

                if (so_doc) {
                    (so_doc.items || []).forEach(row => {
                        if (row.item_code && row.part_no) {
                            so_items_map_composite[`${row.item_code}||${row.part_no}`] = row;
                        }
                        if (row.item_code && !so_items_map_item[row.item_code]) {
                            so_items_map_item[row.item_code] = row;
                        }
                    });
                }

                // --- Populate items table ---
                frm.clear_table("proforma_invoice_table");
                let taxable_value = 0;

                dc_doc.items.forEach(dc_row => {
                    let child = frm.add_child("proforma_invoice_table");

                    child.item = dc_row.item_code;
                    child.item_name = dc_row.item_name;
                    child.hsn_code__sac_code = dc_row.hsn;
                    child.process_type = dc_row.process_type;
                    child.process_name = dc_row.process_name;
                    child.part_no = dc_row.part_no;
                    child.material = dc_row.material;
                    child.qty_nos = dc_row.qty_nos;
                    child.qty_kgs = dc_row.qty_kgs;
                    child.uom = dc_row.rate_uom;

                    let so_row = null;
                    if (dc_row.item_code && dc_row.part_no) {
                        so_row = so_items_map_composite[`${dc_row.item_code}||${dc_row.part_no}`] || null;
                    }
                    if (!so_row && dc_row.item_code) {
                        so_row = so_items_map_item[dc_row.item_code] || null;
                    }

                    if (so_row) {
                        child.rate = so_row.rate;
                        child.item_tax_template = so_row.item_tax_template;
                    }

                    // Calculate amount based on Rate UOM
                    const uom = (dc_row.rate_uom || "").toLowerCase();
                    let qty = 0;
                    if (uom === "nos") qty = dc_row.qty_nos || 0;
                    else if (uom === "kgs") qty = dc_row.qty_kgs || 0;
                    else if (uom === "minimum") qty = 1;
                    else qty = dc_row.qty_nos || dc_row.qty_kgs || 0;

                    child.amount = qty * (child.rate || 0);
                    taxable_value += child.amount;
                });

                frm.refresh_field("proforma_invoice_table");

                // --- Populate taxes table from SO ---
                frm.clear_table("taxes_and_charges");
                let total_taxes = 0;

                if (so_doc && so_doc.taxes && so_doc.taxes.length > 0) {
                    so_doc.taxes.forEach(tax_row => {
                        let tax_child = frm.add_child("taxes_and_charges");
                        tax_child.charge_type = tax_row.charge_type;
                        tax_child.account_head = tax_row.account_head;
                        tax_child.description = tax_row.description;
                        tax_child.rate = tax_row.rate;
                        tax_child.cost_center = tax_row.cost_center;
                        tax_child.included_in_print_rate = tax_row.included_in_print_rate;

                        const tax_amount = (taxable_value * (tax_row.rate || 0)) / 100;
                        tax_child.tax_amount = tax_amount;
                        tax_child.total = taxable_value + tax_amount;
                        total_taxes += tax_amount;
                    });
                }

                frm.refresh_field("taxes_and_charges");

                // --- Set calculated totals ---
                frm.doc.total_taxes_and_charges = total_taxes;
                frm.doc.grand_total = taxable_value + total_taxes;
                frm.refresh_field("total_taxes_and_charges");
                frm.refresh_field("grand_total");

                // --- Fetch address from SO ---
                if (so_doc) {
                    frm.set_value("customer_address", so_doc.customer_address || "");
                    frm.set_value("address", so_doc.address_display || "");
                }

                // --- Fetch Customer DC date and number from first row ---
                if (dc_doc.items && dc_doc.items.length > 0) {
                    const first_row = dc_doc.items[0];
                    frm.set_value("customer_dc_no", first_row.customer_dc_no || "");
                    frm.set_value("customer_dc_date", first_row.customer_dc_date || "");
                }
            };

            if (sales_order_no) {
                frappe.db.get_doc("Sales Order", sales_order_no).then(so_doc => {
                    fetch_and_populate(so_doc);
                }).catch((err) => {
                    console.error("SO fetch error:", err);
                    frappe.msgprint(__("Could not fetch Sales Order details. Populating from Customer DC only."));
                    fetch_and_populate(null);
                });
            } else {
                fetch_and_populate(null);
            }

        }).catch((err) => {
            console.error("DC fetch error:", err);
            frappe.msgprint(__("Could not fetch Customer DC details."));
        });
    }
});