import psycopg2
import pandas as pd
from sqlalchemy import create_engine

conn = psycopg2.connect("host=localhost dbname =dreamhomesnyc user=postgres password=123")

engine = create_engine("postgresql://postgres:123@localhost/dreamhomesnyc")

# Open a cursor to perform database operations
cur = conn.cursor()

# Create schema
schema = """
CREATE TABLE offices (
  OfficeID int,
  Office_Name varchar(50),
  Street_Address varchar(20),
  City varchar(20),
  State char(2),
  Zip_Code char(5),
  Phone_Number char(10),
  PRIMARY KEY (OfficeID)
);

CREATE TABLE employees (
  EmplID int,
  OfficeID int NOT NULL,
  FirstName varchar(20),
  LastName varchar(20),
  JobTitle varchar(50) NOT NULL,
  Employment_Type char(2) NOT NULL,
  Hire_Date date NOT NULL,
  Email varchar(50),
  Phone_Number char(20),
  PRIMARY KEY (EmplID),
  FOREIGN KEY (OfficeID)
      REFERENCES offices(OfficeID),
	CHECK (Employment_Type IN ('FT', 'PT'))
);

CREATE TABLE agent_licenses (
  LicenseID int,
  EmplID int NOT NULL,
  EffDate Date NOT NULL,
  ExpDate Date NOT NULL,
  State char(2),
  PRIMARY KEY (LicenseID),
  FOREIGN KEY (EmplID)
      REFERENCES employees(EmplID)
);

CREATE TABLE property_type (
  PropertyTypeID int,
  Name varchar(20),
  PRIMARY KEY (PropertyTypeID)
);

CREATE TABLE properties (
  UnitID serial,
  Zip_Code char(5) NOT NULL,
  Unit_Number varchar(10), 
  Building_Number varchar(10) NOT NULL,
  Street varchar(20) NOT NULL,
  City varchar(20) NOT NULL,
  State char(2) NOT NULL,
  County varchar(20) NOT NULL,
  PropertyTypeID int NOT NULL,
  PRIMARY KEY (UnitID),
  FOREIGN KEY (PropertyTypeID) 
  	REFERENCES property_type(PropertyTypeID)
);


CREATE TABLE listings (
  ListingID int,
  EmplID int NOT NULL,
  UnitID int NOT NULL,
  Price numeric(12,2) NOT NULL,
  PRIMARY KEY (ListingID),
  FOREIGN KEY (UnitID)
      REFERENCES properties(UnitID),
	FOREIGN KEY (EmplID)
      REFERENCES employees( EmplID)
);

CREATE TABLE expense_categories (
  ExpCategoryID int,
  Expense_Category varchar(20),
  PRIMARY KEY (ExpCategoryID)
);

CREATE TABLE office_expenses (
  Invoice_Number int,
  Approver int,
  OfficeID int NOT NULL,
  Expense_Date date,
  ExpCategoryID int,
  Amount numeric(12,2) NOT NULL,
  Notes varchar(200),
  PRIMARY KEY (Invoice_Number),
  FOREIGN KEY (OfficeID)
      REFERENCES offices(OfficeID),
  FOREIGN KEY (ExpCategoryID)
      REFERENCES expense_categories(ExpCategoryID),
  FOREIGN KEY (Approver)
      REFERENCES employees(EmplID)
);

CREATE TABLE clients (
  ClientID serial,
  FirstName varchar(20),
  LastName varchar(20),
  CorpName varchar(50),
  TaxID varchar(12),
  Phone_Number varchar(13),
  Email varchar(50) NOT NULL,
  Client_Type varchar(20) NOT NULL,
  PRIMARY KEY (ClientID),
  CHECK (Client_Type IN ('Individual', 'Corporation'))
);

CREATE TABLE appointments (
  AppointmentID serial,
  EmplID int NOT NULL,
  ClientID int NOT NULL,
  ListingID int,
  Date date NOT NULL,
  Time time NOT NULL,
  Notes varchar(200),
  status varchar(20),
  PRIMARY KEY (AppointmentID),
  FOREIGN KEY (ClientID)
      REFERENCES clients(ClientID),
  FOREIGN KEY (EmplID)
      REFERENCES employees(EmplID),
  FOREIGN KEY (ListingID)
      REFERENCES listings(ListingID), 
CHECK (status IN ('Scheduled', 'Completed', 'Canceled'))
);


CREATE TABLE neighborhood (
  Zip_Code char(5),
  Neighborhood varchar(20),
  PRIMARY KEY (Zip_Code)
);

CREATE TABLE client_requirements (
	ClientReqID	int,
  ClientID int NOT NULL,
  State char(2),
  City varchar(20),
  Zip_Code char(5),
  PropertyTypeID int,
  Bedrooms int,
  Bathrooms int,
  PRIMARY KEY (ClientReqID),
  FOREIGN KEY (ClientID)
      REFERENCES clients(ClientID),
  FOREIGN KEY (PropertyTypeID)
      REFERENCES property_type(PropertyTypeID),
  FOREIGN KEY (Zip_Code)
      REFERENCES neighborhood(Zip_Code)
);


CREATE TABLE transactions (
  TransactionID serial,
  ListingID int,
  ClientID int,
  EmplID int,
  Amount numeric(12,2) NOT NULL,
  Commission numeric(12,2),
  Transaction_Date date,
  Transaction_Type varchar(10) NOT NULL,
  client_role varchar(15),
  PRIMARY KEY (TransactionID),
  FOREIGN KEY (ListingID)
      REFERENCES listings(ListingID),
  FOREIGN KEY (ClientID)
      REFERENCES clients(ClientID),
  FOREIGN KEY (EmplID)
      REFERENCES employees(EmplID),
CHECK (Transaction_Type IN ('sale', 'rental')),
CHECK (client_role IN ('buyer', 'seller', 'owner', 'renter'))
);

CREATE TABLE schools (
  SchoolID int,
  Name varchar(30),
  Street varchar(20),
  City varchar(20),
  State char(2),
  County varchar(20),
  Zip_Code char(5),
  PRIMARY KEY (SchoolID),
  FOREIGN KEY (Zip_Code)
      REFERENCES neighborhood(Zip_Code)
);

CREATE TABLE open_houses (
  OpenHouseID serial,
  EmplID int NOT NULL,
  ListingID int NOT NULL,
  Date date,
  Time time,
  UnitID int NOT NULL,
  PRIMARY KEY (OpenHouseID),
  FOREIGN KEY (ListingID)
      REFERENCES listings(ListingID),
  FOREIGN KEY (EmplID)
      REFERENCES employees(EmplID),
  FOREIGN KEY (UnitID)
      REFERENCES properties(UnitID)
);

CREATE TABLE amenities (
  AmenityID int,
  AmenityName varchar(20),
  PRIMARY KEY (AmenityID)
);

CREATE TABLE public_transit (
  StationID int,
  Zip_Code char(5),
  Transit_Type varchar(10),
  PRIMARY KEY (StationID),
  FOREIGN KEY (Zip_Code)
      REFERENCES neighborhood(Zip_Code),
	CHECK (Transit_Type IN ('train', 'subway', 'bus', 'ferry'))
);

CREATE TABLE client_amenities (
  ClientID int NOT NULL,
  AmenityID int NOT NULL,
  PRIMARY KEY (ClientID, AmenityID),
  FOREIGN KEY (AmenityID)
      REFERENCES amenities(AmenityID),
  FOREIGN KEY (ClientID)
      REFERENCES clients(ClientID)
);

"""
try:
    cur.execute(schema)
    conn.commit()
    print("Schema created successfully.")
except Exception as e:
    conn.rollback()
    print(f"Tables already created.")
finally:
    cur.close()
    conn.close()

# Load data files
expense_feed = pd.read_csv('raw_office_expense_feed.csv')
re_feed = pd.read_csv('raw_real_estate_feed.csv')

# neighborhood
neighborhood_df = re_feed[['neighborhood_zip_code', 'neighborhood_name']].rename(columns={'neighborhood_zip_code': 'zip_code', 'neighborhood_name': 'neighborhood'}).drop_duplicates().dropna(subset=['zip_code'])
neighborhood_df['zip_code'] = neighborhood_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
neighborhood_df.to_sql(name='neighborhood', con=engine, if_exists='append', index=False)

# property_type
property_type_df = re_feed[['property_type_id', 'property_type_name']].rename(columns={'property_type_id': 'propertytypeid','property_type_name': 'name'}).drop_duplicates().dropna(subset=['propertytypeid'])
property_type_df.to_sql(name='property_type', con=engine, if_exists='append', index=False)

# amenities
amenities_df = re_feed[['amenity_id', 'amenity_name']].rename(columns={'amenity_id': 'amenityid', 'amenity_name': 'amenityname'}).drop_duplicates().dropna(subset=['amenityid'])
amenities_df.to_sql(name='amenities', con=engine, if_exists='append', index=False)

# expense_categories
expense_categories_df = expense_feed[['exp_category_id', 'expense_category']].rename(columns={'exp_category_id': 'expcategoryid'}).drop_duplicates().dropna(subset=['expcategoryid'])
expense_categories_df.to_sql(name='expense_categories', con=engine, if_exists='append', index=False)

# offices
offices_df = re_feed[['office_id', 'office_name', 'office_street_address', 'office_city', 'office_state', 'office_zip_code', 'office_phone_number']].rename(columns={'office_id': 'officeid','office_street_address': 'street_address', 'office_city': 'city', 'office_state': 'state', 'office_zip_code': 'zip_code', 'office_phone_number': 'phone_number'}).drop_duplicates(subset=['officeid']).dropna(subset=['officeid'])
offices_df['zip_code'] = offices_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
offices_df.to_sql(name='offices', con=engine, if_exists='append', index=False)

# employees
employees_df = re_feed[['empl_id', 'office_id', 'employee_first_name', 'employee_last_name', 'employee_job_title', 'employment_type', 'hire_date', 'employee_email', 'employee_phone_number']].rename(columns={'empl_id': 'emplid', 'office_id': 'officeid', 'employee_first_name': 'firstname', 'employee_last_name': 'lastname', 'employee_job_title': 'jobtitle', 'employment_type': 'employment_type', 'employee_email': 'email', 'employee_phone_number': 'phone_number'}).drop_duplicates(subset=['emplid']).dropna(subset=['emplid'])
employees_df.to_sql(name='employees', con=engine, if_exists='append', index=False)

# properties
properties_df = re_feed[['unit_id', 'property_zip_code', 'unit_number', 'building_number', 'property_street', 'property_city', 'property_state', 'property_county', 'property_type_id']].rename(columns={'unit_id': 'unitid', 'property_zip_code': 'zip_code', 'property_street': 'street', 'property_city': 'city', 'property_state': 'state', 'property_county': 'county', 'property_type_id': 'propertytypeid'}).drop_duplicates(subset=['unitid']).dropna(subset=['unitid'])
properties_df['zip_code'] = properties_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
properties_df.to_sql(name='properties', con=engine, if_exists='append', index=False)

# listings
listings_df = re_feed[['listing_id', 'empl_id', 'unit_id', 'listing_price']].rename(columns={'listing_id': 'listingid', 'empl_id': 'emplid', 'unit_id': 'unitid', 'listing_price': 'price'}).drop_duplicates(subset=['listingid']).dropna(subset=['listingid'])
listings_df.to_sql(name='listings', con=engine, if_exists='append', index=False)

# agent_licenses
agent_licenses_df = re_feed[['license_id', 'empl_id', 'license_eff_date', 'license_exp_date', 'license_state']].rename(columns={'license_id': 'licenseid', 'empl_id': 'emplid', 'license_eff_date': 'effdate', 'license_exp_date': 'expdate', 'license_state': 'state'}).drop_duplicates().dropna(subset=['licenseid'])
agent_licenses_df.to_sql(name='agent_licenses', con=engine, if_exists='append', index=False)

# office_expenses
office_expenses_df = expense_feed[['invoice_number', 'approver_empl_id', 'office_id', 'expense_date', 'exp_category_id', 'amount', 'notes']].rename(columns={'exp_category_id': 'expcategoryid', 'office_id': 'officeid', 'approver_empl_id': 'approver'}).drop_duplicates().dropna(subset=['invoice_number'])
office_expenses_df.to_sql(name='office_expenses', con=engine, if_exists='append', index=False)

# clients
clients_df = re_feed[['client_id', 'client_first_name', 'client_last_name', 'client_corp_name', 'client_tax_id', 'client_phone_number', 'client_email', 'client_type']].rename(columns={'client_id': 'clientid', 'client_first_name': 'firstname', 'client_last_name': 'lastname', 'client_corp_name': 'corpname', 'client_tax_id': 'taxid', 'client_phone_number': 'phone_number', 'client_email': 'email'}).drop_duplicates(subset=['clientid']).dropna(subset=['clientid'])
clients_df.to_sql(name='clients', con=engine, if_exists='append', index=False)

# appointments
appointments_df = re_feed[['appointment_id', 'empl_id', 'client_id', 'listing_id', 'appointment_date', 'appointment_time', 'appointment_notes', 'appointment_status']].rename(columns={'appointment_id': 'appointmentid', 'empl_id': 'emplid', 'client_id': 'clientid', 'listing_id': 'listingid', 'appointment_date': 'date', 'appointment_time': 'time', 'appointment_notes': 'notes', 'appointment_status': 'status'}).drop_duplicates().dropna(subset=['appointmentid'])
appointments_df['status'] = appointments_df['status'].str.strip().str.lower().str.capitalize()
appointments_df.to_sql(name='appointments', con=engine, if_exists='append', index=False)

# client_requirements
client_requirements_df = re_feed[['client_req_id', 'client_id', 'req_state', 'req_city', 'req_zip_code', 'req_property_type_id', 'req_bedrooms', 'req_bathrooms']].rename(columns={'client_req_id': 'clientreqid', 'client_id': 'clientid', 'req_state': 'state', 'req_city': 'city', 'req_zip_code': 'zip_code', 'req_property_type_id': 'propertytypeid', 'req_bedrooms': 'bedrooms', 'req_bathrooms': 'bathrooms'}).drop_duplicates().dropna(subset=['clientreqid'])
client_requirements_df['zip_code'] = client_requirements_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
client_requirements_df.to_sql(name='client_requirements', con=engine, if_exists='append', index=False)

# transactions
transactions_df = re_feed[['transaction_id', 'listing_id', 'client_id', 'empl_id', 'transaction_amount', 'transaction_commission', 'transaction_date', 'transaction_type', 'client_role']].rename(columns={'transaction_id': 'transactionid', 'listing_id': 'listingid', 'client_id': 'clientid', 'empl_id': 'emplid', 'transaction_amount': 'amount', 'transaction_commission': 'commission'}).drop_duplicates().dropna(subset=['transactionid'])
transactions_df.to_sql(name='transactions', con=engine, if_exists='append', index=False)

# schools
schools_df = re_feed[['school_id', 'school_name', 'school_street', 'school_city', 'school_state', 'school_county', 'school_zip_code']].rename(columns={'school_id': 'schoolid', 'school_name': 'name', 'school_street': 'street', 'school_city': 'city', 'school_state': 'state', 'school_county': 'county', 'school_zip_code': 'zip_code'}).drop_duplicates().dropna(subset=['schoolid'])
schools_df['zip_code'] = schools_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
schools_df.to_sql(name='schools', con=engine, if_exists='append', index=False)

# open_houses
open_houses_df = re_feed[['open_house_id', 'empl_id', 'listing_id', 'open_house_date', 'open_house_time', 'unit_id']].rename(columns={'open_house_id': 'openhouseid', 'empl_id': 'emplid', 'listing_id': 'listingid', 'open_house_date': 'date', 'open_house_time': 'time', 'unit_id': 'unitid'}).drop_duplicates().dropna(subset=['openhouseid'])
open_houses_df.to_sql(name='open_houses', con=engine, if_exists='append', index=False)

# public_transit
public_transit_df = re_feed[['station_id', 'neighborhood_zip_code', 'transit_type']].rename(columns={'station_id': 'stationid', 'neighborhood_zip_code': 'zip_code'}).drop_duplicates().dropna(subset=['stationid'])
public_transit_df['zip_code'] = public_transit_df['zip_code'].astype(str).str.replace('\.0$', '', regex=True).str.zfill(5)
public_transit_df.to_sql(name='public_transit', con=engine, if_exists='append', index=False)

# client_amenities
client_amenities_df = re_feed[['client_id', 'amenity_id']].rename(columns={'client_id': 'clientid', 'amenity_id': 'amenityid'}).drop_duplicates().dropna()
client_amenities_df.to_sql(name='client_amenities', con=engine, if_exists='append', index=False)

print("Data successfully loaded.")