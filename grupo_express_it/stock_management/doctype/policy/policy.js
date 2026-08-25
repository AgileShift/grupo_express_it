frappe.ui.form.on("Policy", {

	setup(frm) {
		frm.page.sidebar.toggle(false); // Hide Sidebar
	},

	before_load(frm) {
		if (frm.is_new()) {  // Adding default Rows
			frm.add_child('cif_costs', {type: 'Freight'});
			frm.add_child('cif_costs', {type: 'Insurance'});
			frm.add_child('nationalization_costs', {type: 'Customs Taxes'});
			frm.add_child('nationalization_costs', {type: 'Nationalization'});
		}
	},

	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Download as Excel'), () => {
				window.open(`/api/method/grupo_express_it.stock_management.doctype.policy.excel.unique.download?policy=${frm.doc.name}`);
			});
		}
	},

	// Sanitize Fields
	policy: (frm) => {
		frm.doc.policy = frm.doc.policy.trim().replace(/^.*?(\d+).*$/, 'L - $1'); // L - #####
		frm.refresh_field('policy');
	},
	invoice: (frm) => frm.events.sanitize_string_field(frm.doc, 'invoice'),
	provider: (frm) => frm.events.sanitize_string_field(frm.doc, 'provider'),
	exchange_rate: (frm) => frm.events.calculate_items_totals(frm),  // Recalculate on Exchange Rate Change

	// START Helpers
	sanitize_string_field(doc, field, child = false) {
		doc[field] = doc[field].trim().replace(/\s+/g, ' '); // Remove Extra Spaces
		if (!child)
			cur_frm.refresh_field(field);  // If not, Child refresh field(doc)
	},

	// START Custom Functions
	calculate_items_totals: frappe.utils.debounce(
		(frm, item_row = null) => {
			if (item_row) {
				item_row.qty = flt(item_row.qty); // FIXES: the issue with Paste event -> Sanitize Fields. Invalid returns 0
				item_row.fob_unit_price = flt(item_row.fob_unit_price);
			}

			frm.call('recalculate');
		}, 100
	),

	calculate_cif_costs(frm, cif_row = null) {
		if (cif_row) {
			cif_row.amount_usd = flt(cif_row.amount_usd); // FIXES: the issue with Paste event -> Sanitize Fields. Invalid returns 0
		}

		frm.events.calculate_items_totals(frm);  // Recalculate Items Totals
	},

	calculate_nationalization_costs(frm, nationalization_row = null) {
		if (nationalization_row) {
			nationalization_row.amount_usd = flt(nationalization_row.amount_usd);  // FIXES: the issue with Paste event -> Sanitize Fields. Invalid returns 0
			nationalization_row.exchange_rate = flt(nationalization_row.exchange_rate);
		}

		frm.events.calculate_items_totals(frm);  // Recalculate Items Totals
	}
});

frappe.ui.form.on("Policy Item", {
	items_remove: (frm) => frm.events.calculate_items_totals(frm),
	item: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'item', true),
	qty: (frm, cdt, cdn) => frm.events.calculate_items_totals(frm, locals[cdt][cdn]),
	fob_unit_price: (frm, cdt, cdn) => frm.events.calculate_items_totals(frm, locals[cdt][cdn])
});

frappe.ui.form.on("Policy CIF Cost", {
	cif_costs_remove: (frm) => frm.events.calculate_cif_costs(frm),
	cif_costs_add: (frm, cdt, cdn) => locals[cdt][cdn].exchange_rate = frm.doc.exchange_rate, // Set Exchange Rate on Row Add

	provider: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'provider', true),
	description: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'description', true),

	type: (frm, cdt, cdn) => frm.events.calculate_cif_costs(frm, locals[cdt][cdn]),
	amount_usd: (frm, cdt, cdn) => frm.events.calculate_cif_costs(frm, locals[cdt][cdn]) // Recalculate Totals(CIF and Items)
});

frappe.ui.form.on("Policy Nationalization Cost", {
	nationalization_costs_remove: (frm) => frm.events.calculate_nationalization_costs(frm),

	provider: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'provider', true),
	description: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'description', true),
	reference: (frm, cdt, cdn) => frm.events.sanitize_string_field(locals[cdt][cdn], 'reference', true),

	type: (frm) => frm.events.calculate_nationalization_costs(frm),
	amount_usd: (frm, cdt, cdn) => frm.trigger('amount_nio', cdt, cdn),
	exchange_rate: (frm, cdt, cdn) => frm.trigger('amount_nio', cdt, cdn),
	amount_nio: (frm, cdt, cdn) => frm.events.calculate_nationalization_costs(frm, locals[cdt][cdn]) // Recalculate Item Fields and Form Totals
});
