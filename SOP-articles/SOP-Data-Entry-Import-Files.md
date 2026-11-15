# Preparing files for import into Network for Good

**Who:** Engagement and Impact Coordinator

**When:** Before a bulk import of organizations, people, or gifts into Network for Good (NFG).

**Background**

NFG supplies detailed instructions for data import, including template documents with additional explanation. However, several features of their instructions leave ambiguity in how a user creates the spreadsheets prior to importing. Further, certain caveats, such as NFG only reads one file at a time, and only the first sheet of an excel workbook, as well as redundant columns, lead to technical errors. 

**Overview**

This protocol is intended to de-mystify the process for uploading bulk donation entries into NFG. To circumvent issues with formatting and other technical pitfalls, two "optimized" template spreadsheets were generated using the NFG-provided template and streamlining some of the more ambiguos details. 

The "optimized" spreadsheets include one for organization-related entries (`LHoR_organizations_YYYY-MM-DD.csv`) and another for donor-related entries (`LHoR_individuals_YYYY-MM-DD.csv`). These files are in "Comma Separated Values" format to ensure that they are easily transferable between spreadsheet managment softwares (e.g. excel spreadsheets, Google Sheets), as well as directly import-able to NFG. Organizations go in one file. People and their donations go in a second file. Each gift sits on the same row as its donor, with the donor's id repeated. That is how NFG attaches the gift to the right record.

For self-import, use the two files in this SOP. The donation columns are the donation table. They travel with the contact so the gift stays attached to the right id.

Practice files, filled with fictional people, are in `examples/nfg-import/`. Replace those rows before a live import. Use campaign and designation names that already exist in LHoR's NFG. A name NFG does not recognize is created as a new campaign or designation.

## The two upload files

Upload in this order, one file at a time:

1. `LHoR_organizations_YYYY-MM-DD.csv`
2. `LHoR_individuals_YYYY-MM-DD.csv`

Row 1 in both template files is the column header. For convenience, the headers are provided as  a comma separated list in each template's respective description below. For new data import sheets: copy the header names exactly. Individual columns use spaces (`first name`). Organization columns use underscores (`organization_name`). Both spellings come from NFG's field dictionary. Do not add any title rows, notes, and color keys, as NFG would read those rows as records. 

On the import screen, map each column to the NFG field of the same name. Open Imports from the Contacts page, the Giving page, or Settings.

## Identifiers

"Identifiers" here are just a unique alphanumeric key that NFG uses to help distinguish between donations. This can often be useful if two people have the same name or address and is also commonly used in database management to ensure data-cleanliness. 

The table below describes the different types of identifiers that each of the template files use to better ensure data imported to NFG is consistent and easily readable. 


| Record       | Column                     | Pattern         | Example         |
| ------------ | -------------------------- | --------------- | --------------- |
| Individual   | `external user id`         | `LHOR-IND-0001` | `LHOR-IND-0001` |
| Organization | `organization_external_id` | `LHOR-ORG-0001` | `LHOR-ORG-0001` |
| Donation     | start of `description`     | `LHOR-DON-0001  | note`           |


- The same id always means the same person or organization. A new person gets the next unused number. 
- On each gift row, repeat the contact columns unchanged. NFG keeps the contact details from the first row of that id.
- An email belongs to one id only. Two people may share a street address. A shared address is a normal household, and each person keeps their own id.
- Unique identifiers make it very easy to perform statistical analysis on big datasets, however, NFG does not enforce donation identifiers for entry. Put `LHOR-DON-####` at the start of `description`.
- The only custom column in these files is `custom donation field sponsorship`. Create that field in Network for Good before import, or the gift rows fail. Leave every other custom field and group column out.

## Individual file

One row per gift. A person with no gift still gets one row, and the donation columns stay empty.

**Header list** (copy or insert in this order):

`external user id`, `first name`, `last name`, `email`, `address`, `city`, `state`, `zip code`, `mobile phone`, `amount`, `donation_date`, `payment_method`, `campaign`, `designation`, `description`, `custom donation field sponsorship`


| Column                                                          | Record   | Required                                                                  |
| --------------------------------------------------------------- | -------- | ------------------------------------------------------------------------- |
| `external user id`, `first name`, `last name`                   | Contact  | Every row                                                                 |
| `email`, `address`, `city`, `state`, `zip code`, `mobile phone` | Contact  | When you have them                                                        |
| `amount`, `donation_date`, `payment_method`                     | Donation | Every gift. Leave all three blank when there is no gift                   |
| `campaign`, `designation`                                       | Donation | When the gift belongs to one. A blank campaign is stored as uncategorized |
| `description`                                                   | Donation | Every gift, starting with the donation id                                 |
| `custom donation field sponsorship`                             | Donation | `Yes` or `No` on every gift. Blank when there is no gift                  |


## Organization file

One row per gift. Keep the contact-person columns in the header. Leave them blank when the organization has no contact person. If you fill any contact-person column, fill `contact_first_name` too.

**Header list** (copy or insert in this order):

`organization_external_id`, `organization_name`, `organization_email`, `organization_phone`, `organization_address`, `organization_city`, `organization_state`, `organization_zip_code`, `contact_first_name`, `contact_last_name`, `contact_work_email`, `amount`, `donation_date`, `payment_method`, `campaign`, `designation`, `description`, `custom donation field sponsorship`


| Column                                                                                                                                 | Record                      | Required                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- | -------------------------------------------------------- |
| `organization_external_id`, `organization_name`                                                                                        | Organization                | Every row                                                |
| `organization_email`, `organization_phone`, `organization_address`, `organization_city`, `organization_state`, `organization_zip_code` | Organization                | When you have them                                       |
| `contact_first_name`                                                                                                                   | Contact at the organization | When any contact-person column is filled                 |
| `contact_last_name`, `contact_work_email`                                                                                              | Contact at the organization | When you have them                                       |
| `amount`, `donation_date`, `payment_method`, `description`                                                                             | Donation                    | Every gift                                               |
| `campaign`, `designation`                                                                                                              | Donation                    | When the gift belongs to one                             |
| `custom donation field sponsorship`                                                                                                    | Donation                    | `Yes` or `No` on every gift. Blank when there is no gift |


## How to enter each value

- **Names.** Put the given name in `first name` and the family name in `last name`. Both are required on every individual row.
- **Dates.** Type `YYYY-MM-DD`, such as `2025-06-20`. That is the form in NFG's field dictionary. Type it as text. One NFG help article shows `MM/DD/YYYY` and suggests saving as Excel so a cell format is kept. A CSV does not keep that cell format, so the dictionary form is the one these files use.
- **Missing dates.** Use a real date on or before today. If the date is unknown, hold the gift out of the file until it is known. Filling in January 1 would change later appeal estimates.
- **Amount.** `125.00`, digits and one decimal point. `0.00` is allowed only when `payment_method` is `in_kind`.
- **Payment method.** One of `ach`, `cash`, `check`, `credit_card`, `in_kind`, `paypal`, `venmo`, `zelle`, `other`. NFG also accepts `cash_app`, `direct`, `gift_card`, `givecard`, `invoice`, `match`, `payroll`, and `square`. Any other word is stored as `other`.
- **State.** Two letters, such as `SC`. For a US address, leave country out of the file.
- **Email.** Must contain `@` and a period, with no spaces. One address per id. `contact_work_email` follows the same rule and stays different from `organization_email`.
- **Sponsorship.** Before the first import, create a Donation custom field named `sponsorship`. In Network for Good open Settings, then Custom Fields, then the Donation tab. Set the type to radio buttons and the choices to `Yes` and `No`. A column in the spreadsheet does not create this field. On each gift, type `Yes` when that gift is an event sponsorship and `No` when it is an ordinary gift. Leave the cell blank when the row has no gift. Use those two words only. On the import screen, map `custom donation field sponsorship` to the field named `sponsorship`. The same column is used on the organization file and the individual file.

## Before you upload

1. Organizations and individuals are in two separate CSV files.
2. Row 1 is the header, spelled as in this SOP.
3. Every person has a first name, a last name, and an `LHOR-IND-####` id.
4. Every organization has a name and an `LHOR-ORG-####` id.
5. Each gift is its own row and repeats that donor's id.
6. Each gift has amount, date, and payment method, and `description` starts with a new `LHOR-DON-####`.
7. Dates are `YYYY-MM-DD` and fall on or before today.
8. Amounts contain digits and a decimal point only. Zero is used only for `in_kind`.
9. Each email is used on only one id.
10. The file has no full-name column. The only custom column is `custom donation field sponsorship`, and every gift is `Yes` or `No`.

From this project folder, you can check a file before upload:

`python scripts/validate_nfg_import.py`

## If NFG returns errors

1. Go to Settings, then Imports.
2. Open **Error File** for that import. It contains the rows that failed.
3. Read the last column, **Errors**, and correct the cells it names.
4. Delete the Errors column, save the CSV, and import that corrected file.

Rows that succeeded are already in NFG. Import the corrected error file only.