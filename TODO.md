# **TODO:**
## **Incomplete:**
- Error when using the search bar inside of the cart since it is still on the top of the screen (headder)

- Add manage users widget
- Allow the user to manage themselves using the top right
- Add change password ability to the top right for both users and admin users
- Utilize the change password function for first admin logon for change password in manage users & within the management user widget (management of others as an admin)
- Must have 1 persistant admin account

- Global Search bar to find functions for admin usage
- Create QR Code Discount Maker
- Create User Logs page for Admins
- Create Dashboard page with likely to be common use parts
- qr code scanning/ link to global search on main page + find the product page on admin

## **Potential:**
? Can add product to a category without ability to remove it back to unlisted even without full content on the product (as required for listing a product) ?
? Switch from globals to state management for shopping card integration if needed ?
? Make it so that on the store listing the images are the image of the product not the qr code. ?
? Product page fits 1280x720 and alright but still a little bit empty on all other screen sizes. ? 
? Could do with updating the color scheme default ?
? add max pswd length of 16 to fit password box length. (technically can be ignored but should be restricted to around 24 since it seems to be a common practice) ?
? Remove age from signup ?
? Potentially add email for signup and require unique ?
? Ask about use of CTK (custom tkinter) ?

## **Known Issues, unsure how to fix:**

TKINTER DOESNT SUPPORT % BASED PADDING AHHHHHH

Make change of listed/not listed available on main manage products screen cant be done since it would require changes since an unlisted product doesnt require all the details.

Sometimes a slight ghosting can be seen of the dropdown box when the screen has been moved since it updates in 1ms.

The manage products search bar wont unfocus if you click on the top_bar or the left_nav since they are outside of the manage products and cannot be included in the removal of focus.

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

- start_fullscreen does not seem to function as expected, starts in normal window mode, Removed for now since there could be an incompat with it and start_max_windowed. May be reimplimented later on if it makes sense

## **Done:**
- Added scrollability to the shopping cart function, may still need some more done to it, butit will be alright for now.
- Created a shopping cart function that works as required, still a few polishing touches left.
- Fixed issue where admin page was accessible after a normal user was to go to a product page. Added proper user authentification (checks to ensure a user is an admin) before the dropdown interface is shown.
- Reworked the product edit logic to avoid issues and handle all properly and robustly
- Updated the edit_products function to use the layout of the view products page shown in the store, adjusted it to make it dynamic in its updated viewing size and added a placeholder image to avoid issues with there being no image and instruct to add one.
- Fixed issues with cleanup of files not being activated when needed and activated when unneeded (added a new keep_files variable to parse that will be activated if the listing variable is the only one that changed!)
- Fixed error with redundant validation function inside save_edit_product causing errors when editing without a category
- Fixed issue with weird qr code generation complexity and size, not standardized with verion 1 and error correction.
- Adjusted the button's on both manage products and store listing.
- Allowed the qr code to also scale from minx 150px to max 300px depending on space.
- Adjusted padding inside of the manage_products screen and the store_listing to ensure a more uniform look
- Adjusted padding on the content_inner_frame across the store listing and admin dashboard.
- Added the unbinding of configure and button 1 to remaining functions that were missing them.
- Added the view product button to the product listing page.
- Create Pictures for products and a separate product page per one when clicked
- Added feature where if the category is deleted, then it will remove the products that were in it from that category and unlist them to avoid issues.
- Resolved issue where you could scroll even when the products fit in the canvas.
- Resolved issue where the border of the canvas was getting overriden when scrolling in it.
- Added the products sorting under categories in the manage producs listing, along with an unlisted category that will hold all that are not listed.
- Added the products to be sorted based on category on the store listing, by adding a category separator and only displaying products under that category under it.
- Potential random error with the dropdown to do with "winfo_rootx" Was resolved back when i fixed the error with unbinding the dropdown updates.
- Updated the manage products to also use the updated search bar.
- Updated the admin dashboard so it also uses the updated user display.
- Fixed issue with the login not resizing after having resized the prior screens. (set minsize for the login and register screens so that cannot be carried back. DONT set both min and max size to the same value since it causes errors).
- Fixed an issue with the dropdown box bindings not being lost and erroring out the console. ( need to unbind on EVERY Screen).
- Fixed issue with the search bar not losing focus after clicking out
- Adjusted the search bar to be dynamic between the two other title and user info sections.
- Added minimum sizes for the screens to avoid them being overshrank or too small when coming out of fullscreen windowed,
- Adjusted the dropdown box to robustly update its location and stay connected to the userinfo section no matter movements or fullscreening.
- Robustly fixed the window mode when moving between different pages, (now remembers which mode you were in either f11 or fullscreen max or normal), forces the login/register page to be small and centered still.
- Added a function in utils that can be used to center a window properly on the center of a screen.
- Removed the additional logout button on admin dashboard
- Update Color scheme of application (can now be done on the fly through the config.ini, could do with updating this in the default though)
- Added auto clearing and clear on button press of error messages across all of gui.py.
- Allowed the enter key to be used when focused on the change password button on the change_password screen.
- Adjusted the change_password screen to base its theme based on where it is shown from (maintains the correct light style on first setup and will be dark when used by a user inside the program other pages which are all light)
- Ensured that the first time setup works properly and the files are all being generated right
- Moved the default icons to a separate directory to ensure that they will be there and moved into a correct folder called just icons on first startup.
- Fixed some directories  for first generation
- Create a two step initialization setup to allow a user to edit the config.ini after it has been generated.
- Implemented  the ability for config.ini in the admin first setup etc.
- Implemented  the ability to adjust the colors dynamically across the entire gui though config.ini
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