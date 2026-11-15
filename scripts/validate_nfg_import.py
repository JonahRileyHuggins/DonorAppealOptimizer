"""Check LHoR import CSVs against the NFG data-entry SOP.

Reads organizations and individuals files and reports header, identifier,
email, date, and amount problems. Exit code 0 means the files match the SOP.
"""

from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = [
    ROOT / "examples" / "nfg-import" / "LHoR_organizations_2026-10-22.csv",
    ROOT / "examples" / "nfg-import" / "LHoR_individuals_2026-10-22.csv",
]

INDIVIDUAL_COLUMNS = [
    "external user id",
    "first name",
    "last name",
    "email",
    "address",
    "city",
    "state",
    "zip code",
    "mobile phone",
    "amount",
    "donation_date",
    "payment_method",
    "campaign",
    "designation",
    "description",
    "custom donation field sponsorship",
]

ORGANIZATION_COLUMNS = [
    "organization_external_id",
    "organization_name",
    "organization_email",
    "organization_phone",
    "organization_address",
    "organization_city",
    "organization_state",
    "organization_zip_code",
    "contact_first_name",
    "contact_last_name",
    "contact_work_email",
    "amount",
    "donation_date",
    "payment_method",
    "campaign",
    "designation",
    "description",
    "custom donation field sponsorship",
]

DONATION_COLUMNS = [
    "amount",
    "donation_date",
    "payment_method",
    "campaign",
    "designation",
    "description",
]

PAYMENT_METHODS = {
    "ach",
    "cash",
    "cash_app",
    "check",
    "credit_card",
    "direct",
    "gift_card",
    "givecard",
    "in_kind",
    "invoice",
    "match",
    "other",
    "paypal",
    "payroll",
    "square",
    "venmo",
    "zelle",
}

EMAIL_COLUMNS = {
    "individuals": ["email"],
    "organizations": ["organization_email", "contact_work_email"],
}


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv] if argv else DEFAULT_FILES
    errors: list[str] = []
    emails: dict[str, str] = {}
    donation_ids: dict[str, str] = {}

    for path in paths:
        if not path.is_file():
            errors.append(f"{path}: file not found")
            continue
        kind, file_errors, file_emails, file_donation_ids = validate_file(path)
        errors.extend(file_errors)
        collect_unique(emails, file_emails, errors, "email")
        collect_unique(donation_ids, file_donation_ids, errors, "donation id")
        if kind is None and not file_errors:
            errors.append(f"{path}: header is not an organizations or individuals file")

    if errors:
        for message in errors:
            print(message)
        print(f"{len(errors)} problem(s).")
        return 1

    print(f"OK: {len(paths)} file(s) match the import SOP.")
    return 0


def validate_file(path: Path):
    errors: list[str] = []
    emails: dict[str, str] = {}
    donation_ids: dict[str, str] = {}

    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    kind = file_kind(fieldnames)
    if kind == "individuals":
        expected = INDIVIDUAL_COLUMNS
        id_column = "external user id"
        id_label = "LHOR-IND-####"
        stable_columns = INDIVIDUAL_COLUMNS[:9]
    elif kind == "organizations":
        expected = ORGANIZATION_COLUMNS
        id_column = "organization_external_id"
        id_label = "LHOR-ORG-####"
        stable_columns = ORGANIZATION_COLUMNS[:11]
    else:
        errors.append(
            f"{path.name}: row 1 must be the individuals or organizations header"
        )
        return None, errors, emails, donation_ids

    if fieldnames != expected:
        errors.append(f"{path.name}: header must be exactly: {', '.join(expected)}")
        return kind, errors, emails, donation_ids

    seen_contact: dict[str, dict[str, str]] = {}
    for index, row in enumerate(rows, start=2):
        where = f"{path.name}: row {index}"
        record_id = (row.get(id_column) or "").strip()
        if not matches_id(record_id, id_label):
            errors.append(f"{where}: {id_column} must look like {id_label}")
        else:
            contact = {column: (row.get(column) or "").strip() for column in stable_columns}
            prior = seen_contact.get(record_id)
            if prior is None:
                seen_contact[record_id] = contact
            elif prior != contact:
                errors.append(f"{where}: contact columns for {record_id} differ from the first row")

        if kind == "individuals":
            for column in ("first name", "last name"):
                if not (row.get(column) or "").strip():
                    errors.append(f"{where}: {column} is required")
        else:
            if not (row.get("organization_name") or "").strip():
                errors.append(f"{where}: organization_name is required")
            contact_values = [
                (row.get(column) or "").strip()
                for column in ("contact_first_name", "contact_last_name", "contact_work_email")
            ]
            if any(contact_values) and not contact_values[0]:
                errors.append(f"{where}: contact_first_name is required when a contact person is entered")
            org_email = (row.get("organization_email") or "").strip()
            work_email = (row.get("contact_work_email") or "").strip()
            if org_email and work_email and org_email.casefold() == work_email.casefold():
                errors.append(f"{where}: contact_work_email must differ from organization_email")

        check_state(row, "state" if kind == "individuals" else "organization_state", where, errors)
        check_zip(row, "zip code" if kind == "individuals" else "organization_zip_code", where, errors)
        check_email_columns(path, row, kind, record_id, where, emails, errors)
        check_donation(path, row, where, donation_ids, errors)

    return kind, errors, emails, donation_ids


def file_kind(fieldnames: list[str]) -> str | None:
    if fieldnames == INDIVIDUAL_COLUMNS:
        return "individuals"
    if fieldnames == ORGANIZATION_COLUMNS:
        return "organizations"
    if fieldnames and fieldnames[0] == "external user id":
        return "individuals"
    if fieldnames and fieldnames[0] == "organization_external_id":
        return "organizations"
    return None


def matches_id(value: str, label: str) -> bool:
    prefix = label.split("-####")[0]
    parts = value.split("-")
    return (
        len(parts) == 3
        and f"{parts[0]}-{parts[1]}" == prefix
        and len(parts[2]) == 4
        and parts[2].isdigit()
    )


def check_state(row: dict, column: str, where: str, errors: list[str]) -> None:
    value = (row.get(column) or "").strip()
    if value and (len(value) != 2 or not value.isalpha() or value != value.upper()):
        errors.append(f"{where}: {column} must be two uppercase letters")


def check_zip(row: dict, column: str, where: str, errors: list[str]) -> None:
    value = (row.get(column) or "").strip()
    if not value:
        return
    digits = value.replace("-", "")
    valid = digits.isdigit() and (len(value) == 5 or (len(value) == 10 and value[5] == "-"))
    if not valid:
        errors.append(f"{where}: {column} must be 12345 or 12345-6789")


def check_email_columns(path, row, kind, record_id, where, emails, errors) -> None:
    for column in EMAIL_COLUMNS[kind]:
        value = (row.get(column) or "").strip()
        if not value:
            continue
        if not valid_email(value):
            errors.append(f"{where}: {column} must contain @ and a period, with no spaces")
            continue
        key = value.casefold()
        owner = f"{path.name}:{record_id}"
        prior = emails.get(key)
        if prior is None:
            emails[key] = owner
        elif prior != owner:
            errors.append(f"{where}: {value} is already used by {prior}")


def valid_email(value: str) -> bool:
    if any(mark in value for mark in " ,<>()[]"):
        return False
    if value.count("@") != 1:
        return False
    local, domain = value.split("@")
    return bool(local and domain and "." in domain and " " not in value)


def check_donation(path, row, where, donation_ids, errors) -> None:
    values = {column: (row.get(column) or "").strip() for column in DONATION_COLUMNS}
    sponsorship = (row.get("custom donation field sponsorship") or "").strip()
    if any(values.values()):
        if sponsorship not in ("Yes", "No"):
            errors.append(f"{where}: custom donation field sponsorship must be Yes or No on a gift row")
    elif sponsorship:
        errors.append(f"{where}: custom donation field sponsorship must be blank when there is no gift")
    if not any(values.values()):
        return

    for column in ("amount", "donation_date", "payment_method", "description"):
        if not values[column]:
            errors.append(f"{where}: {column} is required on a gift row")

    amount = parse_amount(values["amount"])
    if values["amount"] and amount is None:
        errors.append(f"{where}: amount must be digits with an optional decimal point")

    gift_date = parse_date(values["donation_date"])
    if values["donation_date"] and gift_date is None:
        errors.append(f"{where}: donation_date must be YYYY-MM-DD")
    elif gift_date is not None and gift_date > date.today():
        errors.append(f"{where}: donation_date is in the future")

    method = values["payment_method"]
    if method and method not in PAYMENT_METHODS:
        errors.append(f"{where}: payment_method is not an NFG value")

    if amount is not None and amount < 0:
        errors.append(f"{where}: amount must be zero or greater")
    if amount is not None and method and amount == 0 and method != "in_kind":
        errors.append(f"{where}: amount 0 is allowed only for in_kind")

    description = values["description"]
    donation_id = donation_id_from(description)
    if description and donation_id is None:
        errors.append(f"{where}: description must start with LHOR-DON-#### | note")
    elif donation_id is not None:
        owner = where
        prior = donation_ids.get(donation_id)
        if prior is None:
            donation_ids[donation_id] = owner
        else:
            errors.append(f"{where}: {donation_id} is already used at {prior}")


def parse_amount(value: str) -> Decimal | None:
    if not value or any(mark in value for mark in "$, "):
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return None
    if not amount.is_finite():
        return None
    return amount


def parse_date(value: str) -> date | None:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None
    if parsed.strftime("%Y-%m-%d") != value:
        return None
    return parsed


def donation_id_from(description: str) -> str | None:
    marker = " | "
    if marker not in description:
        return None
    donation_id, note = description.split(marker, 1)
    if matches_id(donation_id, "LHOR-DON-####") and note.strip():
        return donation_id
    return None


def collect_unique(store, found, errors, label) -> None:
    for key, owner in found.items():
        prior = store.get(key)
        if prior is None:
            store[key] = owner
        elif prior != owner:
            errors.append(f"{label} {key} appears in both {prior} and {owner}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
