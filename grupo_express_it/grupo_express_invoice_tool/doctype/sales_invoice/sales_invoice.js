frappe.ui.form.on("Sales Invoice", {
	setup(frm) {
		frm.page.sidebar.toggle(false);
	},

	onload(frm) {
		frm.set_query('item', 'items', (doc) => {
			if (!doc.customer) { // It's fastest to throw from here than server side code.
				frappe.throw(__('Please select the customer.') + ' ' + __('It is needed to fetch Item Details.'));
			}

			if (frm.doc.items.map(item => item.item_type).includes('Contenedor')) { // Is an invoice for a container
				return {
					filters: {type: 'Complemento'} // TODO: Add Extra Costs
				}
			}

			return {
				query: 'grupo_express_it.grupo_express_invoice_tool.doctype.sales_invoice.sales_invoice.items_with_pricing_rule_query',
				filters: {customer: doc.customer},
			}
		});
	},

	onload_post_render(frm) {
		frm.fields_dict['items'].grid.set_multiple_add('item'); // This uses our custom query.
	},

	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button('Enviar por WhatsApp', () => {

			if (frm.is_dirty()) {
				frappe.throw('Por favor guarda el documento antes de Enviarlo por WhatsApp.');
				return;
			}

			frappe.call({
				method: 'grupo_express_it.grupo_express_invoice_tool.doctype.sales_invoice.sales_invoice.send_sales_invoice',
				args: {
					doc_name: frm.doc.name,
					customer_name: frm.doc.customer
				},
				freeze: true,
				freeze_message: 'Conectando con Meta...',
				callback: () => {
					frm.refresh(); // This updates the connections
				}
			});
		});
	},

	customer(frm) {
		if (!frm.doc.customer) {
			frm.doc.customer_name = '';
		}
		frm.doc.in_words = '';
		frm.clear_table('items');

		frm.refresh_fields(); // Refresh all changes
	},

	calculate_invoice_total_and_words(frm) {
		frm.doc.total = frm.get_sum('items', 'amount');

		if (frm.doc.total) { // If the amount is valid and not zero.
			let decimals_in_total = frm.doc.total % 1;  // Getting decimal value

			if (decimals_in_total >= 0.35 && decimals_in_total < 0.50) {
				frm.doc.total = Math.round(frm.doc.total * 2) / 2;
			} else if (decimals_in_total >= 0.80) {
				frm.doc.total = Math.ceil(frm.doc.total);
			}

			frappe.call({
				method: 'grupo_express_it.grupo_express_invoice_tool.doctype.sales_invoice.sales_invoice.money_in_words',
				args: {number: frm.doc.total},
				callback: (r) => frm.doc.in_words = r.message,
				async: false  // TODO: 26 Dic 2023 -> check why this is needed
			});
		} else {
			frm.doc.in_words = '';
		}

		frm.refresh_fields(); // This finally refresh all the fields!
	},

	calculate_item_amount(frm, cdt, cdn, item_row = null) {
		// TODO: Make some option to dont recalculate if the same value is set OR if a field not used for calculation is set
		if (!item_row) item_row = locals[cdt][cdn]; // Getting item row being edited
		if (!item_row.item) return; // If the item has been deleted.

		if (item_row.margin_type === 'Sobre Factura' && item_row.invoiced_amount) {
			item_row.amount = (item_row.invoiced_amount / 100) * item_row.margin_rate_or_amount;
		} else if (item_row.margin_type === 'Cantidad Fija') {
			if (item_row.item_type === 'Contenedor') { // If is a container, then the amount if fixed!
				item_row.amount = item_row.margin_rate_or_amount;
			} else if (item_row.qty) { // If not a container but have a quantity then calculate.
				item_row.amount = (item_row.qty * item_row.margin_rate_or_amount);
			}
		} else if (item_row.margin_type === 'Valoracion' && item_row.qty) {
			// TODO: ASK, How it works here
			item_row.invoiced_amount = item_row.qty * item_row.valuation_rate;  // Calculate the invoice from valuation.
			item_row.amount = (item_row.invoiced_amount / 100) * item_row.margin_rate_or_amount;
		} else {
			return;
		}

		frm.events.calculate_invoice_total_and_words(frm);  // Recalculate the total because we have updated the items amount.
	}
});

frappe.ui.form.on("Sales Invoice Item", {

	items_remove(frm) {
		frm.events.calculate_invoice_total_and_words(frm);
	},

	item(frm, cdt, cdn) {
		let item_row = locals[cdt][cdn]; // Getting item row being edited
		if (!item_row.item) return;      // No item is selected

		if (item_row.item_type === 'Complemento') {
			frm.fields_dict['items'].grid.grid_rows_by_docname[item_row.name].toggle_editable('amount', true);
			return;
		}

		frappe.db.get_value('Pricing Rule', {
			'parent': frm.doc.customer, 'item': item_row.item
		}, ['uom', 'margin_type', 'margin_rate_or_amount', 'valuation_rate', 'extra_costs'], (price_rule) => {
			item_row.uom = price_rule.uom;
			item_row.margin_type = price_rule.margin_type;
			item_row.margin_rate_or_amount = price_rule.margin_rate_or_amount;
			item_row.valuation_rate = price_rule.valuation_rate;
			item_row.extra_costs = price_rule.extra_costs;
			frm.refresh_field('items'); // Refreshing the values in grid.

			frm.events.calculate_item_amount(frm, cdt, cdn, item_row); // This calculates the item amount and the total.
		}, 'Customer');
	},

	invoiced_amount(frm, cdt, cdn) {
		frm.events.calculate_item_amount(frm, cdt, cdn);
	},

	qty(frm, cdt, cdn) {
		frm.events.calculate_item_amount(frm, cdt, cdn);
	},

	amount(frm, cdt, cdn) {
		let item_row = locals[cdt][cdn];

		if (item_row.item_type === 'Complemento') {
			frm.events.calculate_invoice_total_and_words(frm);  // Recalculate the total because we have updated the items amount.
		}
	}
});
