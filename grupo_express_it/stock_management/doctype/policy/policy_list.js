frappe.listview_settings["Policy"] = {

	// If this is set, we can manipulate those two indicators status
	has_indicator_for_draft: true,
	has_indicator_for_cancelled: true,

	onload(listview) {
		listview.page.add_action_item(__('Download as Excel'), () => {
			let docs = listview.get_checked_items(true);

			docs.forEach((doc, i) => {
				window.open('/api/method/grupo_express_it.stock_management.doctype.policy.excel.unique.download?policy=' + doc);
				frappe.show_progress(__('Downloading Policies'), i, docs.length + 1, 'Downloading ' + doc, true);
			});
		});

		listview.page.add_action_item(__('Download Consolidated Excel'), () => {
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
      get_label: () => __('Download as Excel'), get_description: () => '',
      action: (doc) => window.open('/api/method/grupo_express_it.stock_management.doctype.policy.excel.unique.download?policy=' + doc.name),
    }

}
