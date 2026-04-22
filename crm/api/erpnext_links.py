import frappe
from frappe import _


@frappe.whitelist()
def get_linked_docs(deal):
	result = {
		'quotations': [],
		'sales_orders': [],
		'invoices': [],
		'projects': [],
	}
	deal_quote_meta = {}

	if frappe.db.table_exists('CRM Deal'):
		deal_quote_meta = frappe.db.get_value(
			'CRM Deal',
			deal,
			['custom_current_quote', 'custom_quote_status'],
			as_dict=True,
		) or {}

	if frappe.db.table_exists('Quotation'):
		result['quotations'] = frappe.get_all(
			'Quotation',
			filters=[['crm_deal', '=', deal], ['docstatus', '!=', 2]],
			fields=['name', 'status', 'custom_docuseal_status', 'grand_total', 'currency', 'transaction_date'],
			order_by='transaction_date desc',
		) or frappe.get_all(
			'Quotation',
			filters=[['party_name', '=', deal], ['quotation_to', '=', 'CRM Deal'], ['docstatus', '!=', 2]],
			fields=['name', 'status', 'custom_docuseal_status', 'grand_total', 'currency', 'transaction_date'],
			order_by='transaction_date desc',
		)

		for quotation in result['quotations']:
			if (
				not quotation.get('custom_docuseal_status')
				and quotation.get('name') == deal_quote_meta.get('custom_current_quote')
				and deal_quote_meta.get('custom_quote_status')
			):
				quotation['custom_docuseal_status'] = deal_quote_meta.get('custom_quote_status')

	if frappe.db.table_exists('Sales Order'):
		result['sales_orders'] = frappe.get_all(
			'Sales Order',
			filters=[['crm_deal', '=', deal], ['docstatus', '!=', 2]],
			fields=['name', 'status', 'grand_total', 'currency', 'transaction_date'],
			order_by='transaction_date desc',
		)

	if frappe.db.table_exists('Sales Invoice'):
		result['invoices'] = frappe.get_all(
			'Sales Invoice',
			filters=[['crm_deal', '=', deal], ['docstatus', '!=', 2]],
			fields=['name', 'status', 'grand_total', 'currency', 'posting_date'],
			order_by='posting_date desc',
		)

	if frappe.db.table_exists('Project'):
		result['projects'] = frappe.get_all(
			'Project',
			filters={'crm_deal': deal},
			fields=['name', 'status', 'percent_complete'],
			order_by='creation desc',
		)


	if frappe.db.table_exists('Work Order'):
		invoice_names = [inv['name'] for inv in result['invoices']]
		result['work_orders'] = frappe.get_all(
			'Work Order',
			filters=[['sales_order', 'in', invoice_names], ['docstatus', '!=', 2]],
			fields=['name', 'status', 'production_item', 'qty', 'sales_order'],
			order_by='creation desc',
		) if invoice_names else []

	return result


@frappe.whitelist()
def create_project_from_deal(deal):
	if not frappe.db.table_exists('Project'):
		frappe.throw(_('ERPNext is required to create projects'))

	deal_doc = frappe.get_doc('CRM Deal', deal)

	existing = frappe.get_all('Project', filters={'crm_deal': deal}, limit=1)
	if existing:
		return existing[0].name

	project = frappe.new_doc('Project')
	project.project_name = deal_doc.organization or deal
	project.crm_deal = deal
	project.expected_start_date = frappe.utils.nowdate()
	if deal_doc.expected_closure_date:
		project.expected_end_date = deal_doc.expected_closure_date

	project.insert(ignore_permissions=True)
	frappe.db.commit()
	return project.name
