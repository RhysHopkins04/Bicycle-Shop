# Bicycle Shop Scenario 
This bricks-and-mortar family-run business is slowly transitioning from face-to-face, paper and pen methods to digital commerce. The first stage is to digitalise their inventory and processes. The interactive software you will develop will allow them to display bicycle related products, sell products and manage orders and produce outputs. This will allow them to learn what digitalisation can offer them. 

**Therefore, your task is to develop a (1) secure (2) interactive software application. It needs to have a (3) GUI and (4) database connection (5) with outputs.**

The <ins>requirements</ins> and **how marks are allocated for the software**, are listed below: 

1. **SQL Injection Prevention:** The system should be protected against SQL injection attacks. You must ensure that all user inputs are sanitized and validated before being passed to the database. For instance, user’s age under 18 is considered as an attack and details should be rejected and not saved in the database. (3 marks)  

2. **User Authentication:** The system should have a secure user authentication process, requiring users to provide their login credentials to access their personal information and view history. Passwords must be hashed and stored securely in the database. (5 marks)  

3. **Graphical User Interface:** You will need to develop a GUI for the marketing application using Python programming language. The GUI should be user-friendly and visually appealing, with at least the following features to include search bar, product categories, and a QR code scanner. (12 marks) 

4. **SQLite Database:** You will need to create a SQLite database to store product and user information. The database should have at least three tables: one for products, one for user registration, and another for storing user interactions with products. The database should be linked with developed GUI. (12 marks) 

5. **QR Code output and scanner:** The system should be able to output and scan QR codes and retrieve additional information such as product details or discounts. You will need to implement a QR code generator and scanner in the application. QR codes generated should be saved in the local directory of your developed software (application). (8 marks) 

The above requirements can be considered the deliverables for component 2 (above). There is scope to interpret and extend the requirements using more elegant or robust methods and techniques.  

**You can use one of the following Python GUI libraries: PyQt5, Python Tkinter,  PySide2, Kivy**

 It is very important to focus on the consistency of your application. Your application can contain one or more windows linked together.  **Comments in your code** will allow markers to understand that you understand your code and they can see your decision making.*

Your report should have the following sections as a minimum: 

- Introduction (aim, objectives, key features, limits)
- System Design (flow diagrams, comments, psuedo code, snippets etc)
- Testing (test plan, scope, some testing results)
- Conclusion (aim and objectives)
- References (Harvard style)
- Appendices
    - User manual
    - Source code including detailed comments
    - Test data 