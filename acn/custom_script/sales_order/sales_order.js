erpnext.utils.update_child_items_sales_order = function (opts) {

	const frm = opts.frm;
	const cannot_add_row = typeof opts.cannot_add_row === "undefined" ? true : opts.cannot_add_row;
	const child_docname = typeof opts.cannot_add_row === "undefined" ? "items" : opts.child_docname;
	const child_meta = frappe.get_meta(`${frm.doc.doctype} Item`);
	const has_reserved_stock = opts.has_reserved_stock ? true : false;
	const get_precision = (fieldname) => child_meta.fields.find((f) => f.fieldname == fieldname).precision;

	this.data = frm.doc[opts.child_docname].map((d) => {
		return {
			docname: d.name,
			name: d.name,
			item_code: d.item_code,
			delivery_date: d.delivery_date,
			schedule_date: d.schedule_date,
			conversion_factor: d.conversion_factor,
			qty: d.qty,
			rate: d.rate,
			uom: d.uom,
			fg_item: d.fg_item,
			fg_item_qty: d.fg_item_qty,
			prevdoc_docname: d.prevdoc_docname,
		};
	});

	const fields = [
		{
			fieldtype: "Data",
			fieldname: "docname",
			read_only: 1,
			hidden: 1,
		},
		{
			fieldtype: "Link",
			fieldname: "item_code",
			options: "Item",
			in_list_view: 1,
			read_only: 0,
			disabled: 0,
			label: __("Item Code"),
			get_query: function () {
				let filters;
				if (frm.doc.doctype == "Sales Order") {
					filters = { is_sales_item: 1 };
				} else if (frm.doc.doctype == "Purchase Order") {
					if (frm.doc.is_subcontracted) {
						if (frm.doc.is_old_subcontracting_flow) {
							filters = { is_sub_contracted_item: 1 };
						} else {
							filters = { is_stock_item: 0 };
						}
					} else {
						filters = { is_purchase_item: 1 };
					}
				}
				return {
					query: "erpnext.controllers.queries.item_query",
					filters: filters,
				};
			},
			onchange: function () {
				const me = this;

				frm.call({
					method: "erpnext.stock.get_item_details.get_item_details",
					args: {
						doc: frm.doc,
						args: {
							item_code: this.value,
							set_warehouse: frm.doc.set_warehouse,
							customer: frm.doc.customer || frm.doc.party_name,
							quotation_to: frm.doc.quotation_to,
							supplier: frm.doc.supplier,
							currency: frm.doc.currency,
							is_internal_supplier: frm.doc.is_internal_supplier,
							is_internal_customer: frm.doc.is_internal_customer,
							conversion_rate: frm.doc.conversion_rate,
							price_list: frm.doc.selling_price_list || frm.doc.buying_price_list,
							price_list_currency: frm.doc.price_list_currency,
							plc_conversion_rate: frm.doc.plc_conversion_rate,
							company: frm.doc.company,
							order_type: frm.doc.order_type,
							is_pos: cint(frm.doc.is_pos),
							is_return: cint(frm.doc.is_return),
							is_subcontracted: frm.doc.is_subcontracted,
							ignore_pricing_rule: frm.doc.ignore_pricing_rule,
							doctype: frm.doc.doctype,
							name: frm.doc.name,
							qty: me.doc.qty || 1,
							uom: me.doc.uom,
							pos_profile: cint(frm.doc.is_pos) ? frm.doc.pos_profile : "",
							tax_category: frm.doc.tax_category,
							child_doctype: frm.doc.doctype + " Item",
							is_old_subcontracting_flow: frm.doc.is_old_subcontracting_flow,
						},
					},
					callback: function (r) {
						if (r.message) {
							const { qty, price_list_rate: rate, uom, conversion_factor, bom_no } = r.message;

							const row = dialog.fields_dict.trans_items.df.data.find(
								(doc) => doc.idx == me.doc.idx
							);
							if (row) {
								Object.assign(row, {
									conversion_factor: me.doc.conversion_factor || conversion_factor,
									uom: me.doc.uom || uom,
									qty: me.doc.qty || qty,
									rate: me.doc.rate || rate,
									bom_no: bom_no,
								});
								dialog.fields_dict.trans_items.grid.refresh();
							}
						}
					},
				});
			},
		},
		{
			fieldtype: "Link",
			fieldname: "uom",
			options: "UOM",
			read_only: 0,
			label: __("UOM"),
			reqd: 1,
			onchange: function () {
				frappe.call({
					method: "erpnext.stock.get_item_details.get_conversion_factor",
					args: { item_code: this.doc.item_code, uom: this.value },
					callback: (r) => {
						if (!r.exc) {
							if (this.doc.conversion_factor == r.message.conversion_factor) return;

							const docname = this.doc.docname;
							dialog.fields_dict.trans_items.df.data.some((doc) => {
								if (doc.docname == docname) {
									doc.conversion_factor = r.message.conversion_factor;
									dialog.fields_dict.trans_items.grid.refresh();
									return true;
								}
							});
						}
					},
				});
			},
		},
		{
			fieldtype: "Float",
			fieldname: "qty",
			default: 0,
			read_only: 0,
			in_list_view: 1,
			label: __("Qty"),
			precision: get_precision("qty"),
		},
		{
			fieldtype: "Currency",
			fieldname: "rate",
			options: "currency",
			default: 0,
			read_only: 0,
			in_list_view: 1,
			label: __("Rate"),
			precision: get_precision("rate"),
		},
	];

	const has_quotation = frm.doc.items.some(d => d.prevdoc_docname);

	if (has_quotation) {
		fields.splice(2, 0, {
			fieldtype: "Link",
			fieldname: "prevdoc_docname",
			options: "Quotation",
			in_list_view: 1,
			label: __("Quotation"),
		});
	}


	if (frm.doc.doctype == "Sales Order" || frm.doc.doctype == "Purchase Order") {
		fields.splice(2, 0, {
			fieldtype: "Date",
			fieldname: frm.doc.doctype == "Sales Order" ? "delivery_date" : "schedule_date",
			in_list_view: 1,
			label: frm.doc.doctype == "Sales Order" ? __("Delivery Date") : __("Reqd by date"),
			reqd: 1,
		});
		fields.splice(3, 0, {
			fieldtype: "Float",
			fieldname: "conversion_factor",
			label: __("Conversion Factor"),
			precision: get_precision("conversion_factor"),
		});
	}

	if (
		frm.doc.doctype == "Purchase Order" &&
		frm.doc.is_subcontracted &&
		!frm.doc.is_old_subcontracting_flow
	) {
		fields.push(
			{
				fieldtype: "Link",
				fieldname: "fg_item",
				options: "Item",
				reqd: 1,
				in_list_view: 0,
				read_only: 0,
				disabled: 0,
				label: __("Finished Good Item"),
				get_query: () => {
					return {
						filters: {
							is_stock_item: 1,
							is_sub_contracted_item: 1,
							default_bom: ["!=", ""],
						},
					};
				},
			},
			{
				fieldtype: "Float",
				fieldname: "fg_item_qty",
				reqd: 1,
				default: 0,
				read_only: 0,
				in_list_view: 0,
				label: __("Finished Good Item Qty"),
				precision: get_precision("fg_item_qty"),
			},
		);
	}

	let dialog = new frappe.ui.Dialog({
		title: __("Update Items"),
		size: "extra-large",
		fields: [
			{
				fieldname: "trans_items",
				fieldtype: "Table",
				label: "Items",
				cannot_add_rows: cannot_add_row,
				in_place_edit: false,
				reqd: 1,
				data: this.data,
				get_data: () => {
					return this.data;
				},
				fields: fields,
			},
		],
		primary_action: function () {
			if (frm.doctype == "Sales Order" && has_reserved_stock) {
				this.hide();
				frappe.confirm(
					__(
						"The reserved stock will be released when you update items. Are you certain you wish to proceed?"
					),
					() => this.update_items()
				);
			} else {
				this.update_items();
			}
		},
		update_items: function () {
			const trans_items = this.get_values()["trans_items"].filter((item) => !!item.item_code);
			frappe.call({
				method: "erpnext.controllers.accounts_controller.update_child_qty_rate",
				freeze: true,
				args: {
					parent_doctype: frm.doc.doctype,
					trans_items: trans_items,
					parent_doctype_name: frm.doc.name,
					child_docname: child_docname,
				},
				callback: function () {
					frm.reload_doc();
				},
			});
			this.hide();
			refresh_field("items");
		},
		primary_action_label: __("Update"),
	});

	dialog.show();


};

frappe.ui.form.on('Sales Order', {
	refresh: function (frm) {
		frm.remove_custom_button(__("Update Items"));

		if (frm.doc.docstatus === 1) {

			frm.add_custom_button(__("Update Items"), () => {

				erpnext.utils.update_child_items_sales_order({
					frm: frm,
					child_docname: "items",
					child_doctype: "Sales Order Detail",
					cannot_add_row: false,
					has_reserved_stock: frm.doc.__onload?.has_reserved_stock
				});

			});

		}
		if (frm.doc.open_order && frm.doc.reopen === 1) {

			frm.add_custom_button(__('Re-Close Order'), function () {
				frappe.call({
					method: "acn.custom_script.sales_order.sales_order.reopen_order",
					args: { name: frm.doc.name, docstatus: 1 }, // keep as submitted
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(r.message);
							frm.reload_doc();
						}
					}
				});
			});
		}
		if (frm.doc.open_order && frm.doc.docstatus == 1) {
			frm.add_custom_button(__('Reopen Order'), function () {
				frappe.call({
					method: "acn.custom_script.sales_order.sales_order.reopen_order",
					args: { name: frm.doc.name, docstatus: 0 }, // set back to draft
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(r.message);
							frm.reload_doc();
						}
					}
				});
			});
		}
	},

	setup: function (frm) {
		frm.fields_dict['items'].grid.get_field('custom_part_no').get_query = function (doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			let selected_part_no = (cur_frm.doc.items || [])
				.map(d => d.custom_part_no)
				.filter(Boolean);
			return {
				query: 'acn.custom_script.sales_order.sales_order.get_part_no',
				filters: {
					"customer": cur_frm.doc.customer,
					"exclude_part_no": selected_part_no
				}

			}
		};


		// $(frm.wrapper).on("grid-row-render", function (e, grid_row) {
		// 	if (
		// 		in_list(["Sales Order Item"], grid_row.doc.doctype)
		// 	) {
		// 		let cl = grid_row.columns_list;
		// 		if (grid_row.doc.custom_rate_uom == "Kgs") {

		// 			if ('custom_qty_in_nos' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 1;
		// 			}
		// 			if ('custom_qty_in_kgs' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 0;
		// 			}
		// 		}
		// 		if (grid_row.doc.custom_rate_uom == "Nos") {
		// 			if ('custom_qty_in_kgs' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 1;
		// 			}
		// 			if ('custom_qty_in_nos' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 0;
		// 			}
		// 		}
		// 		if (grid_row.doc.custom_rate_uom == "Minimum") {
		// 			if ('custom_qty_in_kgs' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_kgs.column_index].df.read_only = 1;
		// 			}
		// 			if ('custom_qty_in_nos' in grid_row.columns) {
		// 				cl[grid_row.columns.custom_qty_in_nos.column_index].df.read_only = 1;
		// 			}
		// 		}
		// 	}


		// });

	}

});


frappe.ui.form.on('Sales Order Item', {
	custom_part_no: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (row.custom_part_no && frm.doc.customer) {
			frappe.call({
				method: "acn.custom_script.sales_order.sales_order.get_process_rate",
				args: {
					part_no: row.custom_part_no,
					customer: frm.doc.customer
				},
				callback: function (r) {
					console.log(r)
					if (r.message) {

						frappe.model.set_value(cdt, cdn, "custom_rate_uom", r.message.rate_uom);
						// frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);
						row.custom_process_type = r.message.process_type
						row.custom_process_name = r.message.process_name
						row.custom_material = r.message.material
						row.custom_rate_uom = r.message.rate_uom
						row.eway_bill_hsn = r.message.eway_bill_hsn

						row.custom_customer_process_ref_no = r.message.customer_ref
						if (cur_frm.doc.docstatus == 0) {
							frappe.model.set_value(cdt, cdn, "item_code", r.message.item_code);

							if (r.message.rate_uom == "Minimum") {
								frappe.model.set_value(cdt, cdn, "qty", 1);
							}
							setTimeout(() => {

								frappe.model.set_value(cdt, cdn, "rate", r.message.process_rate);
							}, 900);
						}
						if (cur_frm.doc.docstatus == 1) {
							row.item_code = r.message.item_code
							row.item_name = r.message.item_name
						}

						cur_frm.refresh()

					}
				}
			});
		}
	},
	custom_qty_in_nos: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_rate_uom == "Nos") {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_nos);
		}
	},
	custom_qty_in_kgs: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.custom_rate_uom == "Kgs") {
			frappe.model.set_value(cdt, cdn, "qty", row.custom_qty_in_kgs);

		}
	}
});


