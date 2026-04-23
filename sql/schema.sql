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


