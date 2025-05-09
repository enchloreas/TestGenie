# This script is used to test the import of the User model from the app.models module.
from app.models_ import TestCase

print("User model imported successfully.")
print("Table name:", TestCase.__tablename__)
