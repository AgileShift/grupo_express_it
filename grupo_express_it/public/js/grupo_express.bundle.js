import GridRow from "../../../../frappe/frappe/public/js/frappe/form/grid_row";

frappe.ui.form.ControlTable = class ControlTable extends frappe.ui.form.ControlTable {

	make() {
		super.make();

		if (!['Policy Item', 'Policy CIF Cost', 'Policy Nationalization Cost'].includes(this.df.options))
			return; // No Personalization. Default controller

		// At execution the grid fields are not yet set. Only html elements
		this.grid.df.on_setup = (grid) => {
			grid.form_grid.append('<div class="grid-footer-row disable-click bold"></div>'); // Make Footer Row for totals
		}

		// Override Grid Functions See: frappe/frappe/public/js/frappe/form/grid.js
		this.refresh_input = () => {
			super.refresh_input();                 // Call Super of the ControlTable
			this.grid_make_footer.call(this.grid); // We Use call to set the context to the grid
		};
	}

	grid_make_footer() {
		if (this.prevent_build) return; // See grid.make_head(). if (this.data.length === 0) return -> Avoided

		if (this.footer_row) {
			this.form_grid.find(".grid-footer-row .grid-row").remove(); // Remove to redraw. Created on df.on_setup()
		}

		if (!this.data.length > 0) return;

		this.total_columns = this.docfields
			.filter((df) => frappe.model.is_numeric_field(df.fieldtype) && !['exchange_rate', 'fob_unit_price', 'unit_price'].includes(df.fieldname))
			.map(df => df.fieldname);

		this.footer_row = new GridRow({
			parent: this.form_grid.find('.grid-footer-row'),
			parent_df: {}, // Hack, avoid call to: grid_row.js -> set_docfields -> frappe.meta.make_docfield_copy_for
			docfields: this.docfields,
			grid: this,
			doc: this.data.reduce((acc, d) => {
				this.total_columns.forEach((df) => {
					acc[df] = (acc[df] || 0) + (d[df] || 0); // TODO: Improve here the: (property || 0)
				});
				return acc;
			}, {idx: ''}) // If this.data.length is empty. the column gets 0 for values. Which is ok!
		});
	}

}
