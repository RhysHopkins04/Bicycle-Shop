# **TODO:**
## **Incomplete:**
- Resolve all repeated code use
- Resolve all issues with Contradictions in my code locations
    - Move the qr code generation into the database.py for when they are being added to match update_product
- Refactor the code locations for a few functions/modules

- Add change password ability to the top right for both users and admin users
- Add the products to be sorted based on category 
- Create Pictures for products and a separate product page per one when clicked

- Make change of listed/not listed available on main manage products screen
- Adjust button locations/buttons on manage products

- Global Search bar to find functions
- qr code scanning/ link to global search on main page + find the product page on admin
- Create a Shopping Cart Function

- Add manage users widget
- Allow the user to manage themselves using the top right
- Utilize the change password function for first admin logon for change password in manage users
- Must have 1 persistant admin account.

- Create QR Code Discount Maker
- Create User Logs page for Admins
- Create Dashboard page with likely to be common use parts.

- Update Color scheme of application: 

- Potential random error with the dropdown to do with "winfo_rootx"

## **Potential:**
? Remove age from signup ?
? Potentially add email for signup and require unique ?
? Ask about use of CTK (custom tkinter) ?

# **Completion:**
## **Partial:**
- Redesign the normal user interface
    - Somewhat, but not final
- Ensure that I do not have any reduntant functions
    - Changed all field validation for registration and password change is done through validation.py
- Go through my code and ensure that functions from gui.py are split into their correct files
    - Removed the Validation from gui.py to validation.py, Still more to be checked (Recursive on feature creation)
- Document all of Code
    - gui.py up to date as of 27/11/24
    - docstrings throughout should be up to date always across all files

## **Done:**
- Allow unhide password temp button for logon, register and change password. (Test Change Password when implemented since might be broken, cant test till implemented)
- Redid the error+Success messages inside utils.py to adhere better to DRY Proceedure, switched all uses of succes/error messages inside of gui.py to use these functions.
- Moved the qr code generation into the database file for update_product instead of gui
- Creates/Updates/Removes the old file tree and images/qr_codes correctly on product_edit
- Organise the file tree's for products and icons.
- Make it so change password has same validation as when registering
- make it so both paswds have to match to create/change, enter password 2x for creation, or both
- Adjust the admin dashboard to somewhat relate to the user page 
- Add more information to be on product creation + edit = Description, Category, Image, stock
- Add Search bar for main store page to find listed products
- Update Products on normal user listing to use horizontal (same as manage products)
- Make it so that when the row length becomes too tall for the viewing window it will allow scrolling
- Make Product listings (length of products on one row) dynamic
- Make it so main store and admin viewing match/ make admin be able to see main + back button
- Make old QR code be deleted on product edits
