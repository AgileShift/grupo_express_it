frappe.ui.form.on("Customer", {
	setup(frm) {
		frm.page.sidebar.toggle(false);
	},

	onload(frm) {
		frm.set_query('item', 'pricing_rules', (doc) => {
			return {
				filters: {
					item_name: ['not in', doc.pricing_rules.map(p => p.item)], // Show products that are not the list
					type: ['not in', ['Complemento']]
				}
			};
		});
	},

	onload_post_render(frm) {
		frm.fields_dict['pricing_rules'].grid.set_multiple_add('item'); // This uses our custom query.
	}
});
