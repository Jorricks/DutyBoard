# Database migrations using Alembic
This folders contain all the required code to enable database migrations.

## Applying all the migrations
To apply the migrations, it should be as simple as:
1. Open a new terminal session and go into the `duty_board` folder with `cd duty_board`.
2. Add your DB link with `export SQL_ALCHEMY_CONNECTION="postgresql://postgres:mysecretpassword@database_container:5432/postgres"`
3. Run `alembic upgrade head`

## Reverting a migration
To revert to the previous version, you need to:
1. Open a new terminal session and go into the `duty_board` folder with `cd duty_board`.
2. Add your DB link with `export SQL_ALCHEMY_CONNECTION="postgresql://postgres:mysecretpassword@database_container:5432/postgres"`
3. Run `alembic downgrade -1`, or replace -1 with the number of migrations you want to downgrade.

## Creating a new migration
To create a new migration:
1. Open a new terminal session and go into the `duty_board` folder with `cd duty_board`.
2. (Optional) If you have a new model, add the new models metadata class to the top inside `target_metadata`.
3. Add your DB link with `export SQL_ALCHEMY_CONNECTION="postgresql://postgres:mysecretpassword@127.0.0.1:5432/postgres"`
4. Create the new revision with `alembic revision --autogenerate -m "<Your message here>"`


