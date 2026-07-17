frappe.listview_settings["Policy"] = {

	// If this is set, we can manipulate those two indicators status
	has_indicator_for_draft: true,
	has_indicator_for_cancelled: true,

	onload(listview) {
		listview.page.add_action_item('Descargar Excel Individual', () => {
			let docs = listview.get_checked_items(true);

			docs.forEach((doc, i) => {
				window.open('/api/method/grupo_express_it.stock_management.doctype.policy.excel.unique.download?policy=' + doc);
				frappe.show_progress('Descargando Polizas', i, docs.length + 1, 'Descargando ' + doc, true);
			});
		});

		listview.page.add_action_item('Descargar Excel Consolidado', () => {
			let docs = listview.get_checked_items(true);

			window.open('/api/method/grupo_express_it.stock_management.doctype.policy.excel.consolidated.download?policies=' + docs);
		});
	},

	get_indicator: (doc) => [__(doc.status), {
		'Draft': 'red',
		'Not Billed': 'orange',
		'Partly Billed': 'yellow',
		'Fully Billed': 'green',
		'Cancelled': 'red',
	}[doc.status], 'status,=,' + doc.status],

	button: {
      show: () => true,
      get_label: () => 'Excel', get_description: () => '',
      action: (doc) => window.open('/api/method/grupo_express_it.stock_management.doctype.policy.excel.unique.download?policy=' + doc.name),
    }

}
