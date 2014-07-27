#clash-workspace

  Django workspace for clash

###Testing the app:

  * Create files in the root directory of the app:
      - file/
      - app/static/files/
    
  * Create the database using command:
      - python manage.py syncdb
    
  * Create database fields from the /admin url. This app assumes that there are three Team entries named
    - round1
    - round2
    - swifttyper

  * After creation of users, run the scripts from root directory of the app :
    ```
    python manage.py shell
    from app.script import user_folders()
    user_folders()
    ```

###Resetting the app
  - rm db.sqlite3
  - python manage.py shell
  - from app.script import clean_up()
  - clean_up()
  
  
  
