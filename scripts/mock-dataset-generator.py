# Install the library via terminal first: pip install uszipcode
import random
import pandas as pd

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

from faker import Faker

# Initialize the search engine
engine = SearchEngine()

# List of US state abbreviations
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", 
          "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", 
          "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", 
          "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", 
          "WI", "WY"]

all_zipcodes = []

for state in states:
    # Query all ZIP code types within the state (setting a high return limit)
    results = engine.by_state(state, zipcode_type=None, returns=5000)
    for res in results:
        if res.zipcode and res.state:
            all_zipcodes.append((res.zipcode, res.major_city, res.state))

cols = ['external user id', 'first name', 'last name', 'email', 'address',
       'city', 'state', 'zip code', 'mobile phone', 'amount', 'donation_date',
       'payment_method', 'campaign', 'designation', 'description',
       'custom donation field sponsorship']

# Initialize the generator
fake = Faker()

payment_methods = ["ach", "cash", "check", "credit_card", "paypal", "venmo", "zelle", "other"]
campaigns = ["Annual Fund", "Year-End Appeal", "Spring Breakfast", "Household Drive"]
designations = ["General Support", "Recovery Housing", "Household Goods"]
notes = ["first gift", "renewal", "year-end gift", "spring grant"]

records = []
donation_number = 1

for i in range(1, 5001):
    first_name = fake.first_name()
    last_name = fake.last_name()
    external_user_id = "LHOR-IND-" + str(i).zfill(4)
    email_local = (first_name + "." + last_name + "." + str(i)).lower()
    email_local = email_local.replace(" ", "").replace("'", "")
    email = email_local + "@example.com"
    zip_code, city, state_abbr = random.choice(all_zipcodes)
    if city is None:
        city = ""
    address = fake.street_address().replace("\n", " ")
    mobile_phone = fake.numerify("###-555-####")

    if i % 25 == 0:
        amount = ""
        donation_date = ""
        payment_method = ""
        campaign = ""
        designation = ""
        description = ""
        sponsorship = ""
    else:
        if i % 17 == 0:
            payment_method = "in_kind"
            amount = "0.00"
        else:
            payment_method = random.choice(payment_methods)
            amount = str(random.randint(10, 500)) + "." + str(random.randint(0, 99)).zfill(2)
        donation_date = fake.date_between(start_date="-5y", end_date="today").isoformat()
        campaign = random.choice(campaigns)
        designation = random.choice(designations)
        description = "LHOR-DON-" + str(donation_number).zfill(4) + " | " + random.choice(notes)
        donation_number = donation_number + 1
        if i <= 10:
            sponsorship = "Yes"
        else:
            sponsorship = "No"

    records.append([
        external_user_id, first_name, last_name, email, address,
        city, state_abbr, str(zip_code).zfill(5), mobile_phone, amount,
        donation_date, payment_method, campaign, designation, description,
        sponsorship,
    ])

mock_df = pd.DataFrame(records, columns=cols)
mock_df.to_csv("mock-import-dataset.csv", index=False)

