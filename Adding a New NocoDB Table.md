Adding a New NocoDB Table
Purpose

Use this checklist whenever you add a new NocoDB table to the r4r-auction-flask-middleware project.

The most important requirement is to register the table name and its table ID environment variable in app/config.py. If this step is missed, the application will not recognize the table.
Before You Begin

Confirm the following:

    The exact name of the new NocoDB table
    Which NocoDB base contains the table
    The columns the table needs
    Which application features will read from or write to the table
    Whether the table needs custom API routes or can use the existing generic table routes

Table and column names are case-sensitive. Choose the names carefully and use the exact same spelling everywhere.
Table Setup Checklist
1. Choose the Table Name

Select the exact table name that will be used in NocoDB and in the application.

For example:

    Donator Messages

Do not use different variations in different places, such as:

    Donator Message
    donator messages
    Donator messages

The table name must remain consistent throughout the project.
2. Choose the NocoDB Base

Decide which NocoDB base will contain the table:

    Donator base
    Auction base
    Site base

This is important because the application uses different NocoDB request paths for Site base tables.

The Site base tables are identified in app/services/nocodb.py. If the new table belongs to the Site base, it must be included in that file’s Site table list.

If the table belongs to the Donator or Auction base, it should not be added to the Site table list.
3. Design the Table Columns

Create a list of all fields the table requires.

For every column, decide:

    The exact column name
    The NocoDB field type
    Whether the field is required
    Whether it needs default values
    Whether it needs selectable options
    Whether it will be used in searches or filters

Make sure the column names exactly match the names used by Python code.

For example, these are different names:

    Created At
    Created at
    created_at

A mismatch between NocoDB and the application can cause missing values, failed filters, or unsuccessful record updates.
4. Create the Table in NocoDB

Create the table in the correct NocoDB base.

You can create it:

    Manually through the NocoDB interface
    Using the project’s table setup script
    Using a one-time table creation script

The main setup script is scripts/setup_nocodb_tables.py.

If you use the setup script, add the table to the appropriate section:

    DONATOR_BASE_TABLES
    AUCTION_BASE_TABLES

Do not create the same table twice. Check NocoDB first if you are unsure whether it already exists.
5. Record the Table Schema

Keep the table definition documented in scripts/setup_nocodb_tables.py, even if you created the table manually.

This gives the project a record of:

    The table name
    The columns
    The field types
    Select options
    Default values

This is especially important if the table needs to be recreated later.
6. Find the NocoDB Table ID

The application uses the NocoDB table ID when making API requests.

Run scripts/get_table_ids.py and locate the new table in the output. Record the table ID shown next to its name.

Make sure the ID comes from the correct NocoDB base.

Do not confuse:

    The table’s display name
    The table’s internal NocoDB ID
    The base ID

The application needs the table ID.
7. Register the Table in app/config.py

Open app/config.py and find the TABLE_ID_ENV_VARS mapping.

Add an entry containing:

    The exact NocoDB table name
    The environment variable that will store its table ID

For example, a table named Donator Messages would use an environment variable such as DONATOR_MESSAGES_TABLE_ID.

This is the step that was previously missed.

Without this registration:

    The table will not be included in TABLE_IDS
    The generic table API will reject requests
    Application startup may fail if the required environment variable is missing
    Services using the table will not be able to find its ID

8. Add the Table ID to Local Environment Settings

Add the new table ID environment variable to your local environment configuration.

For example:

    .env
    Docker environment settings
    Local development secrets

Use the actual table ID obtained from NocoDB.

Do not commit secret values or private deployment credentials to the repository.
9. Add the Table ID to Production

Add the same environment variable to the production deployment environment.

For this project, that may include:

    Coolify environment variables
    Docker environment variables
    Server configuration
    Scheduled task configuration

Adding the variable locally is not enough. Production must have its own copy.

If the production variable is missing, the application may fail during startup with a missing table ID error.
10. Update README.md

Add the new table ID environment variable to the NocoDB table ID documentation in README.md.

Document:

    The environment variable name
    The corresponding NocoDB table name
    Any special base requirements

This helps prevent the variable from being forgotten during future deployments.
11. Update app/services/nocodb.py if Required

Only update app/services/nocodb.py if the new table belongs to the Site base.

Add the table to the Site base table collection so the application uses the correct NocoDB endpoint.

If the table belongs to the Donator or Auction base, no change is needed in this file.

The table name must still be registered in app/config.py regardless of which base it uses.
12. Add Application Services

Add or update the service code that will interact with the table.

Check that the service uses:

    The exact table name
    The exact column names
    The correct read and write operations
    Appropriate filtering
    Appropriate error handling

Review existing services for similar behavior before creating new patterns.

When a table is used by a scheduled task, check the scripts in app/services/ as well as the deployment’s scheduled task configuration.
13. Add API Routes if Needed

The project includes generic table routes in app/blueprints/tables.py.

These routes support:

    Listing records
    Creating records
    Getting an individual record
    Updating a record
    Deleting a record

A newly registered table can use these generic routes if that is appropriate.

Create a dedicated route or blueprint when the table requires:

    Custom validation
    Special permissions
    Business rules
    Data transformation
    A simplified response format
    Operations involving multiple tables

Remember that generic table access is controlled by the table registration in app/config.py.
14. Update Validation and Allowed Fields

If the new table accepts user-submitted data, review the validation code in app/services/validation.py.

Confirm that:

    Only permitted fields can be written
    User input is validated
    Email and URL fields use the existing validation helpers where appropriate
    Fields controlled by administrators cannot be overwritten by users
    Filter values are safely constructed

Do not assume that adding a table automatically provides sufficient input protection.
15. Update Scheduled Jobs and Integrations

Search the repository for related table names and column names.

Check:

    Scheduled services
    Email notifications
    Synchronization scripts
    Admin workflows
    Auction workflows
    Frontend-facing services
    Data migration scripts

A table can be correctly created and registered but still fail if a related service expects a different column name or table name.
16. Verify Every Column Name

Search for each important column name and compare the results with NocoDB.

Check:

    Spelling
    Capitalization
    Spaces
    Singular versus plural names
    Date and time field names
    ID field names
    Select option values

For example, Item Status and Status are separate fields. The application will not automatically treat them as equivalent.
17. Restart the Application

Restart the Flask application after changing:

    Environment variables
    Table registration
    NocoDB base configuration
    Service code

The application loads table IDs during startup. A running process will not automatically notice new environment values.

Scheduled tasks may also need to be restarted or redeployed separately.
18. Test the Table

Test the table in the following order:

    Confirm that the application starts successfully.
    Confirm that the table ID is present in the deployment environment.
    Test reading records.
    Test creating a record.
    Test retrieving an individual record.
    Test updating a record.
    Test deleting a test record if appropriate.
    Confirm the results in NocoDB.
    Test the feature that uses the table.
    Check application logs for errors.

Use a test record rather than real production data during initial testing.
19. Search for Missed References

Before considering the work complete, search the repository for:

    The exact table name
    The table ID environment variable
    Important column names
    Any old or temporary table names

Confirm that the table appears wherever it is expected, including:

    app/config.py
    scripts/setup_nocodb_tables.py
    app/services/nocodb.py, if it is a Site base table
    Service files
    Blueprint files
    Scheduled tasks
    README.md
    Deployment configuration documentation
    Tests

Final Review Checklist

Before merging or deploying, confirm:

    The table exists in the correct NocoDB base.
    The table name is written consistently everywhere.
    All required columns exist.
    Column names match the application exactly.
    The table schema is documented in the setup script.
    The table ID has been retrieved.
    The table name is registered in app/config.py.
    The table ID environment variable exists locally.
    The table ID environment variable exists in production.
    README.md documents the new environment variable.
    app/services/nocodb.py is updated if the table belongs to the Site base.
    Required services and routes have been added.
    Validation and permissions have been reviewed.
    Scheduled jobs and integrations have been checked.
    The application has been restarted.
    Read and write operations have been tested.
    Repository searches show no missing references.

Most Common Mistake

Creating the table in NocoDB is only the first step.

The most common mistake is forgetting to register the table in app/config.py.

Every new table needs a mapping between:

    The exact NocoDB table name
    The environment variable containing its table ID

If that mapping is missing, the application does not know the table exists.