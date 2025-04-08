frappe.ui.form.on("Customer Process template", {
    process_type: function(frm) {
        // if (!frm.doc.process_type) {
        //     return;
        // }

        // frappe.call({
        //     method: "get_parameter",
        //     doc: frm.doc,
        //     callback: function(r) {
        //         frm.dirty()
        //         frm.refresh_fields();
        //     }
        // });
    },
    refresh: function(frm) {
        // setTimeout(() => {

           
            frm.fields_dict["parameters_with_acceptance_criteria"].grid.wrapper.find('.grid-add-row, .grid-add-multiple-rows').hide();
    // }, 200);

    },
    onload: function(frm) {
        const observer = new MutationObserver((mutationsList) => {
            mutationsList.forEach((mutation) => {
                if (
                    mutation.type === 'attributes' &&
                    mutation.attributeName === 'disabled'
                ) {
                    const target = mutation.target;
        
                    // Check if target is INPUT and specific to lot_no field in a child table
                    if (
                        target.tagName === 'INPUT' &&
                        target.getAttribute('data-fieldname') === 'lot_no'
                    ) {
                        $(target).prop('readonly', true).prop('disabled', false);
                    }
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true, subtree: true });
       
    },

    'onload_post_render': function (frm, cdt, cdn) {
        
       
            frm.fields_dict["sequence_lot_wise_internal_process"].grid.wrapper.on('dblclick', '.grid-body .grid-row', function(e) {
                const row_index = $(e.currentTarget).data("idx");
    
                // Get the child row
                const child = frm.doc.sequence_lot_wise_internal_process.find(row => row.idx === row_index);
    
                if (child) {
                    let new_row = frm.add_child("parameters_with_acceptance_criteria");
                    new_row.lot_no =child.lot_no;
                    new_row.internal_process=child.internal_process;
            
                    frm.refresh();
                 
                }
            });
    
    },

     setup: function(frm) {
        frm.fields_dict["customer_requirements"].grid.get_field("process_parameter").get_query = function(doc, cdt, cdn) {
            return {
                query: "acn.acn.doctype.customer_process_template.customer_process_template.get_param",
                filters: { "process_type": frm.doc.process_type || "" }
            };
        };
    }
});


frappe.ui.form.on("Sequence Lot wise Internal Process", {
    sequence_lot_wise_internal_process_add: function(frm, cdt, cdn) {
        let d = locals[cdt][cdn];
        d.lot_no=d.idx
        cur_frm.refresh_fields();

    }



})
