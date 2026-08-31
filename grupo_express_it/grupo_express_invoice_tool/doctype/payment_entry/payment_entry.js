frappe.ui.form.on("Payment Entry", {

	onload: function(frm) {
		frm.set_currency_labels(['paid_amount', 'total_allocated_amount', 'unallocated_amount'], 'USD');
	},

	async customer(frm) {
		frm.clear_table('entries');
		frm.refresh_fields();

		await frm.events.allocate_received_amount_to_references(frm);
	},

	async received_amount(frm) {
		await frm.events.allocate_received_amount_to_references(frm);
	},

	async exchange_rate(frm) {
		await frm.events.allocate_received_amount_to_references(frm);
	},

	async mode_of_payment(frm) {
		frm.set_currency_labels(['received_amount'], frm.doc.currency);

		await frm.events.allocate_received_amount_to_references(frm);
	},

	allocate_received_amount_to_references(frm) {
		if (!frm.doc.customer || !frm.doc.currency) return;
		if (frm.doc.currency === "NIO" && Number(frm.doc.exchange_rate) <= 1) return;

		return frm.call("allocate_received_amount_to_references");
	},

	async calculate_payment_totals(frm) {
		if (!frm.doc.currency) return;

		await frm.call("calculate_payment_totals");
	},
});

frappe.ui.form.on("Payment Entry Line", {
	async reference_name(frm) {
		await frm.events.allocate_received_amount_to_references(frm);
	},

	async entries_remove(frm) {
		await frm.events.calculate_payment_totals(frm);
	},

	async allocated_amount(frm) {
		await frm.events.calculate_payment_totals(frm);
	},
});
