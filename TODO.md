# **TODO:**
## **Incomplete:**
- Ensure that I do not have any reduntant functions.
- Ensure that all functions are in the correct files, possibly separate into more modules due to size of project

- Improve my documentation as a whole, comments and docustrings.
    - gui.py up to date as of 27/11/24.
    - docstrings throughout should be up to date always across all files.

- Complete all tests and log in excel document for the assignment writeup. (also learn about proper automated pipeline testing CI/CD ETC)
    - Test all logging both user and admin(success and failure), to ensure there are no broken parts.
    - Potentially an issue with the old qr codes for products not being removed againn...
    - Able to keep product listed even after removing content from it, doesnt go back to being unlisted automatically if info is removed (bug but maybe a feature? depends who sees it)


## **Potential:**
### **Features Additions:**
- ? Switch to using loging instead of show_login_screen for all functions. ?
- ? add max password length of 16 to fit password box length. (technically can be ignored but should be restricted to around 24 since it seems to be a common practice) ?
- ? Reduce password requirements for a standard users password, keep complexity requirements for accounts with admin access, on account update to admin have them meet the requirements if password does not already ?

- ? Global Search bar to find functions for admin usage. ?
- ? qr code scanning/ link to global search on main page + find the product page on admin. ?

- ? Allow discounts to be specific to just certain items or certain basket sizes (spend more than etc, or only % off this product) ?

### **Changes:**
- ? Issue with stock not being checked to ensure it is an integer when editing a product ?
- ? Can add product to a category without ability to remove it without changing it to a new category (cannot go back to unlisted category)
- ? Swap age from signup for email and require unique ?

- ? **!MAJOR CHANGE!** Update the adding of categories and management of categories screen since it is primitive and not user friendly for first time useage. ?
- ? **!MAJOR CHANGE!** Swap all scrollable frames over to scrollable grid and update the product boxes to match (much neater code, however means changing over entire screens to use a different geometry method)

- ? Could do with updating the color scheme default ?
- ? Make it so that on the store listing the images are the image of the product not the qr code. ?
- ? Product page fits 1280x720 and alright but still a little bit empty on all other screen sizes. ? 

- ? **!MAJOR CHANGE!** Impliment state management for transfers bvetween screens of the gui since it is more elegant and robust and avoids passing the parameters every transfer. ?


## **Known Issues, unsure how to fix:**
- ! Issues with refreshing the header section with username and first & last names after changing in manage user (self change), can be done with refresh users but will only work on the dashboard/ listing page since that is where it is setup and hence needs to be refreshed there on that page. Unimplimented and cleared for now till could be possibly fixed with rewrite of codebase !
- ! Issues with checkboxes and radioboxes, Ask about use of CTK (custom tkinter) might fix it !
- ! Have had issues trying to use grid layounds inside of a packed scrollable doesnt work obviously, used long workarounds until grid version was created and works, switch to it... !
- ! start_fullscreen does not function as expected, starts in normal window mode, Removed for now since there could be an incompat with it and start_max_windowed. May be reimplimented later on if it makes sense. !
- ! Sometimes a slight ghosting can be seen of the dropdown box when the screen has been moved since it updates in 1ms, it also stays up if the mouse is moved off the entire window (not really an issue but noted) !


# **Completion:**
## **Done:**
- Create Dashboard page 3 sections, admin logs readout, Statistics of the application/Store and alerts for certain issues. Can be adjusted later if required to contain more specific information.
- Logging files are located in the /temp/ folder in the application directory and get cleaned up automatically to avoid dataleaks (somewhat unnsessary but good practice encase adjusments are made which reveal sensitive data).
- Created logging for attempted logins to admin accounts that fail to allow admins to stop these before progressing to an attack.
- Created admin logging for success and failure operations to stop malicious use and ensure that tracking for training recaps can be done.
- Created user logging for all processes succesful and navigation to monitor interraction.
- Implimented the qr code scanning or uploading (camera or file) to the cart for the user.
- Created discount qr code maker and management screen for admins. Qr codes can be added, edited, deactivated./activated and they have their usages tracked.
- System works to stop an admin from demoting themselves or deleting themselves ensuring there is always a persistent admin account.
- Adjusted the change passsowrd function to work for all password changes, including first login, self change and admin changes.
- Added ability for users to manage themselves from the dropdown, including change passwords from inside of that.
- Added Manage Users Widget, ensures admin cannot delete themselves, or take away admin status from themselves. Confirmations before deletion takes place on other users.
- Fixed error when the to go back to the admin dashboard after visiting the cart and going back to the store page.
- Fixed error when trying to go back to store page from cart, when cart is empty and store page is empty.
- Added the search bar: "enable"/"disable" function to allow for it to only be usable under pages where it is allowed (this should completely stop the ability for an error to occur where the search bar cant filter the page).
- Added scrollability to the shopping cart function, may still need some more done to it, butit will be alright for now.
- Created a shopping cart function that works as required, still a few polishing touches left.
- Fixed issue where admin page was accessible after a normal user was to go to a product page. Added proper user authentification (checks to ensure a user is an admin) before the dropdown interface is shown.
- Reworked the product edit logic to avoid issues and handle all properly and robustly.
- Updated the edit_products function to use the layout of the view products page shown in the store, adjusted it to make it dynamic in its updated viewing size and added a placeholder image to avoid issues with there being no image and instruct to add one.
- Fixed issues with cleanup of files not being activated when needed and activated when unneeded (added a new keep_files variable to parse that will be activated if the listing variable is the only one that changed!).
- Fixed error with redundant validation function inside save_edit_product causing errors when editing without a category.
- Fixed issue with weird qr code generation complexity and size, not standardized with verion 1 and error correction.
- Adjusted the button's on both manage products and store listing.
- Allowed the qr code to also scale from minx 150px to max 300px depending on space.
- Adjusted padding inside of the manage_products screen and the store_listing to ensure a more uniform look.
- Adjusted padding on the content_inner_frame across the store listing and admin dashboard.
- Added the unbinding of configure and button 1 to remaining functions that were missing them.
- Added the view product button to the product listing page.
- Create Pictures for products and a separate product page per one when clicked.
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
- Fixed issue with the search bar not losing focus after clicking out.
- Adjusted the search bar to be dynamic between the two other title and user info sections.
- Added minimum sizes for the screens to avoid them being overshrank or too small when coming out of fullscreen windowed.
- Adjusted the dropdown box to robustly update its location and stay connected to the userinfo section no matter movements or fullscreening.
- Robustly fixed the window mode when moving between different pages, (now remembers which mode you were in either f11 or fullscreen max or normal), forces the login/register page to be small and centered still.
- Added a function in utils that can be used to center a window properly on the center of a screen.
- Removed the additional logout button on admin dashboard.
- Update Color scheme of application (can now be done on the fly through the config.ini, could do with updating this in the default though).
- Added auto clearing and clear on button press of error messages across all of gui.py.
- Allowed the enter key to be used when focused on the change password button on the change_password screen.
- Adjusted the change_password screen to base its theme based on where it is shown from (maintains the correct light style on first setup and will be dark when used by a user inside the program other pages which are all light).
- Ensured that the first time setup works properly and the files are all being generated right.
- Moved the default icons to a separate directory to ensure that they will be there and moved into a correct folder called just icons on first startup.
- Fixed some directories  for first generation.
- Create a two step initialization setup to allow a user to edit the config.ini after it has been generated.
- Implemented  the ability for config.ini in the admin first setup etc.
- Implemented  the ability to adjust the colors dynamically across the entire gui though config.ini.
- Refactor the code locations for a few functions/modules.
- Resolve all issues with Contradictions in my code locations.
- All current fixable DRY Violations have been resolved at this point.
- Migrated the majority of the display_products functions to utils.py to clean up the display products functions repeatability without losing ties to the other parts of the screen.
- Fixed small issue with message label creation being in the wrong place in register.
- Migrated the password entry box setup to utils.py to be called to create the password entry's for all usage with the visibility button.
- Appears that the password visibility appears in the tab list or adds another tab and should be excluded from this, Excluded the password box from focus with "takefocus=False".
- Manage categories add new category does not automatically refresh the categories page, adjusted order of the display_categorys function to be first.
- Fixed error where when being saved even without image edit would try and replace the image with the same iamge and give a samefile error.
- Fixed error where you could set a product to listed without a description.
- Fixed issue where the old qr code was deleted without regeneration when the edit product was saved even without edits to the name/price values.
- Updated when the scroll wheel binding should be active and dropped to avoid the error "invalid command name" when the canvas is improperly closed.
- Fixed issue which would cause error when viewing the combo box on edit products if the box was empty.
- Relocated some of the functions regarding scrollbox's and product layouts into utils.py.
- Removed the old add logout button function from gui.py due to being out of use.
- Relocated the promote and demote admin functions to the auth.py for centralising user management.
- Removed unused imports across all files.
- Updated the icons to use the file location paths from file_manager instead of defining each time.
- Moved the category editing and deletion into the database for database access consistency.
- Reworked the Product add and edit validationss and centralized them in validation.py.
- Moved the password change operation into auth for consistency.
- Moved all directory and file management operations to file_manager.py.
- Organized constants by moving PRODUCTS_DIR and ICONS_DIR to file_manager.py.
- Created new module file_manager.py to centralize file operations.
- Removed QR code generation from gui.py and centralized in database.py/file_manager.py.
- Rearanged functions in all helper files for readability.
- Moved the styled button creation for the admin dashboard left_nav to utils.py to increase readabiltiy and reduce repetition.
- Moved the Dropdown functions to the utils.py and updated their bindings to match since used twice in both main store page and the admin dashboard.
- Moved Password Visiblity function to the utils file, the setting the images has to remain inside of the start_app() function loop post window creation otherwise it errors out.
- Allow unhide password temp button for logon, register and change password. (Test Change Password when implemented since might be broken, cant test till implemented).
- Redid the error+Success messages inside utils.py to adhere better to DRY Proceedure, switched all uses of succes/error messages inside of gui.py to use these functions.
- Moved the qr code generation into the database file for update_product instead of gui.
- Creates/Updates/Removes the old file tree and images/qr_codes correctly on product_edit.
- Organise the file tree's for products and icons.
- Make it so change password has same validation as when registering.
- make it so both paswds have to match to create/change, enter password 2x for creation, or both.
- Adjust the admin dashboard to somewhat relate to the user page .
- Add more information to be on product creation + edit = Description, Category, Image, stock.
- Add Search bar for main store page to find listed products.
- Update Products on normal user listing to use horizontal (same as manage products).
- Make it so that when the row length becomes too tall for the viewing window it will allow scrolling.
- Make Product listings (length of products on one row) dynamic.
- Make it so main store and admin viewing match/ make admin be able to see main + back button.
- Make old QR code be deleted on product edits.