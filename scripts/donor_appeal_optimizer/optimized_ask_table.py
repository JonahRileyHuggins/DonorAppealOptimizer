# Build a suggested-ask table from an individual Network for Good export.
# Organizations are not read. Sponsorship gifts are not counted.

import csv
from datetime import date, datetime, timedelta
from pathlib import Path

import sqlalchemy_mate
import sqlalchemy_mate.types as sqlalchemy_mate_types
from sqlalchemy_mate.orm.api import ExtendedBase
from sqlalchemy_mate.engine_creator import EngineCreator
from sqlalchemy_mate.types.compressed_json import CompressedJSONType

# uszipcode 1.0.1 still looks for these names on sqlalchemy_mate itself.
sqlalchemy_mate.ExtendedBase = ExtendedBase
sqlalchemy_mate.EngineCreator = EngineCreator
sqlalchemy_mate_types.CompressedJSONType = CompressedJSONType

from uszipcode import SearchEngine

from choose_file import choose_file

project_root = Path(__file__).resolve().parents[1]
start_folder = project_root / "examples" / "nfg-import"
chosen = choose_file(str(start_folder))
if chosen == "":
    raise SystemExit("No file was selected.")

input_path = Path(chosen)
output_path = input_path.parent / "LHoR_optimized_asks.csv"

# The past year is the 365 days ending today.
as_of = date.today()
past_year_start = as_of - timedelta(days=365)

# ZIP median household income is compared with this dollar figure.
reference_income = 75000

engine = SearchEngine()

# One entry per donor. Gifts for the same id are added together.
donor_ids = []
donors = {}

with input_path.open(newline="", encoding="utf-8-sig") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        # A sponsorship gift is left out of the ask.
        if (row.get("custom donation field sponsorship") or "").strip() == "Yes":
            continue

        amount_text = (row.get("amount") or "").strip()
        date_text = (row.get("donation_date") or "").strip()
        if amount_text == "" or date_text == "":
            continue

        gift_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        if gift_date < past_year_start or gift_date > as_of:
            continue

        donor_id = (row.get("external user id") or "").strip()
        amount = float(amount_text)

        if donor_id not in donors:
            donor_ids.append(donor_id)
            first_name = (row.get("first name") or "").strip()
            last_name = (row.get("last name") or "").strip()
            donors[donor_id] = {
                "donor name": (first_name + " " + last_name).strip(),
                "zip code": (row.get("zip code") or "").strip(),
                "past_year_total": 0.0,
            }

        donors[donor_id]["past_year_total"] = donors[donor_id]["past_year_total"] + amount

# Look up each ZIP once. A missing income uses a factor of 1.
income_by_zip = {}

output_rows = []
for donor_id in donor_ids:
    donor = donors[donor_id]
    zip_code = donor["zip code"].split("-")[0].zfill(5)

    if zip_code not in income_by_zip:
        zip_record = engine.by_zipcode(zip_code)
        if zip_record is None or zip_record.median_household_income is None:
            income_by_zip[zip_code] = None
        else:
            income_by_zip[zip_code] = zip_record.median_household_income

    zip_income = income_by_zip[zip_code]
    if zip_income is None:
        income_factor = 1
    else:
        income_factor = zip_income / reference_income

    # Keep one ZIP from multiplying the gift history by more than this range.
    if income_factor < 0.5:
        income_factor = 0.5
    if income_factor > 2:
        income_factor = 2

    # Middle ask, then half of that ask, then 1.5 times that ask.
    # Each step rounds to the nearest $25. A result under $25 is written as 25.
    middle_unrounded = donor["past_year_total"] * income_factor
    middle_ask = int(middle_unrounded / 25 + 0.5) * 25
    first_ask = int((middle_ask * 0.5) / 25 + 0.5) * 25
    third_ask = int((middle_ask * 1.5) / 25 + 0.5) * 25

    if first_ask < 25:
        first_ask = 25
    if middle_ask < 25:
        middle_ask = 25
    if third_ask < 25:
        third_ask = 25

    output_rows.append({
        "donor-id": donor_id,
        "donor name": donor["donor name"],
        "optimized first tier request": first_ask,
        "optimized second tier request": middle_ask,
        "optimized third tier request": third_ask,
    })

with output_path.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "donor-id",
            "donor name",
            "optimized first tier request",
            "optimized second tier request",
            "optimized third tier request",
        ],
    )
    writer.writeheader()
    writer.writerows(output_rows)

print("Wrote " + str(len(output_rows)) + " donors to " + str(output_path))
