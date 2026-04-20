import re

import frappe
from frappe import _


def _ensure_raven_installed():
	if "raven" not in frappe.get_installed_apps():
		frappe.throw(_("Raven is not installed on this site."))


def _get_linked_channel(organization: str):
	channel_name = frappe.db.get_value(
		"Raven Channel",
		{"linked_doctype": "CRM Organization", "linked_document": organization},
		"name",
	)
	if channel_name:
		return frappe.get_doc("Raven Channel", channel_name)

	stored_channel = frappe.db.get_value("CRM Organization", organization, "raven_channel")
	if stored_channel and frappe.db.exists("Raven Channel", stored_channel):
		return frappe.get_doc("Raven Channel", stored_channel)

	return None


def _get_workspace():
	workspaces = frappe.get_all("Raven Workspace", fields=["name", "workspace_name", "type"])
	if not workspaces:
		frappe.throw(_("No Raven workspace found."))

	if len(workspaces) == 1:
		return workspaces[0].name

	default_company = frappe.db.get_single_value("Global Defaults", "default_company")
	normalized_company = _normalize_workspace_label(default_company)
	if normalized_company:
		matches = [
			workspace
			for workspace in workspaces
			if _workspace_matches_company(workspace, normalized_company)
		]
		if len(matches) == 1:
			return matches[0].name

	member_workspaces = {
		row.workspace
		for row in frappe.get_all(
			"Raven Workspace Member",
			filters={"user": frappe.session.user},
			fields=["workspace"],
		)
	}
	available_member_workspaces = [workspace for workspace in workspaces if workspace.name in member_workspaces]
	if len(available_member_workspaces) == 1:
		return available_member_workspaces[0].name

	non_generic_workspaces = [
		workspace for workspace in workspaces if _normalize_workspace_label(workspace.workspace_name or workspace.name) != "raven"
	]
	if len(non_generic_workspaces) == 1:
		return non_generic_workspaces[0].name

	frappe.throw(
		_(
			"Multiple Raven workspaces exist and CRM could not determine which one to use automatically."
		)
	)


def _normalize_workspace_label(value: str | None) -> str:
	value = re.sub(r"\([^)]*\)", "", (value or "").strip().lower())
	value = re.sub(r"[^a-z0-9]+", " ", value)
	return re.sub(r"\s{2,}", " ", value).strip()


def _workspace_matches_company(workspace, normalized_company: str) -> bool:
	workspace_labels = {
		_normalize_workspace_label(workspace.name),
		_normalize_workspace_label(workspace.workspace_name),
	}
	return any(
		label
		and (
			label == normalized_company
			or label in normalized_company
			or normalized_company in label
		)
		for label in workspace_labels
	)


def _get_channel_name(organization: str) -> str:
	channel_name = re.sub(r"[^a-z0-9]+", "-", organization.strip().lower())
	channel_name = re.sub(r"-{2,}", "-", channel_name).strip("-")
	return channel_name or f"organization-{frappe.generate_hash(length=6).lower()}"


def _serialize_channel(channel):
	return {
		"name": channel.name,
		"channel_name": channel.channel_name,
		"type": channel.type,
		"workspace": channel.workspace,
		"route": f"/raven/channel/{channel.name}",
	}


@frappe.whitelist()
def get_linked_raven_channel(organization: str):
	frappe.has_permission("CRM Organization", doc=organization, throw=True)
	_ensure_raven_installed()

	channel = _get_linked_channel(organization)
	if not channel:
		return {"channel": None}

	if frappe.db.get_value("CRM Organization", organization, "raven_channel") != channel.name:
		frappe.db.set_value("CRM Organization", organization, "raven_channel", channel.name, update_modified=False)

	return {"channel": _serialize_channel(channel)}


@frappe.whitelist()
def create_public_raven_channel(organization: str):
	frappe.has_permission("CRM Organization", doc=organization, ptype="write", throw=True)
	_ensure_raven_installed()

	channel = _get_linked_channel(organization)
	created = False

	if not channel:
		channel = frappe.get_doc(
			{
				"doctype": "Raven Channel",
				"channel_name": _get_channel_name(organization),
				"type": "Public",
				"linked_doctype": "CRM Organization",
				"linked_document": organization,
				"workspace": _get_workspace(),
			}
		)
		channel.insert(ignore_permissions=True)
		created = True

	frappe.db.set_value("CRM Organization", organization, "raven_channel", channel.name, update_modified=False)

	return {
		"channel": _serialize_channel(channel),
		"created": created,
	}
