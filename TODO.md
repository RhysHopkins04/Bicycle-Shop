# **TODO:**
## **Incomplete:**


- Additional logout button on admin dashboard

- Add change password ability to the top right for both users and admin users
- Add the products to be sorted based on category
- Create Pictures for products and a separate product page per one when clicked

- Make change of listed/not listed available on main manage products screen
- Adjust button locations/buttons on manage products

- Global Search bar to find functions
- qr code scanning/ link to global search on main page + find the product page on admin
- Switch from globals to state management for shopping card integration.
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
- Refactor the code locations for a few functions/modules
- Resolve all issues with Contradictions in my code locations
- All current fixable DRY Violations have been resolved at this point.
- Migrated the majority of the display_products functions to utils.py to clean up the display products functions repeatability without losing ties to the other parts of the screen.
- Fixed small issue with message label creation being in the wrong place in register
- Migrated the password entry box setup to utils.py to be called to create the password entry's for all usage with the visibility button.
- Appears that the password visibility appears in the tab list or adds another tab and should be excluded from this, Excluded the password box from focus with "takefocus=False".
- Manage categories add new category does not automatically refresh the categories page, adjusted order of the display_categorys function to be first.
- Fixed error where when being saved even without image edit would try and replace the image with the same iamge and give a samefile error.
- Fixed error where you could set a product to listed without a description
- Fixed issue where the old qr code was deleted without regeneration when the edit product was saved even without edits to the name/price values.
- Updated when the scroll wheel binding should be active and dropped to avoid the error "invalid command name" when the canvas is improperly closed.
- Fixed issue which would cause error when viewing the combo box on edit products if the box was empty.
- Relocated some of the functions regarding scrollbox's and product layouts into utils.py
- Removed the old add logout button function from gui.py due to being out of use
- Relocated the promote and demote admin functions to the auth.py for centralising user management.
- Removed unused imports across all files.
- Updated the icons to use the file location paths from file_manager instead of defining each time.
- Moved the category editing and deletion into the database for database access consistency.
- Reworked the Product add and edit validationss and centralized them in validation.py
- Moved the password change operation into auth for consistency
- Moved all directory and file management operations to file_manager.py
- Organized constants by moving PRODUCTS_DIR and ICONS_DIR to file_manager.py
- Created new module file_manager.py to centralize file operations
- Removed QR code generation from gui.py and centralized in database.py/file_manager.py
- Rearanged functions in all helper files for readability.
- Moved the styled button creation for the admin dashboard left_nav to utils.py to increase readabiltiy and reduce repetition
- Moved the Dropdown functions to the utils.py and updated their bindings to match since used twice in both main store page and the admin dashboard.
- Moved Password Visiblity function to the utils file, the setting the images has to remain inside of the start_app() function loop post window creation otherwise it errors out.
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
