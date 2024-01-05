run the Following command to install the packages required to run the project

   `pip install -r requirements. txt`


run the following command to run tests of the Project

  `python manage.py test`

POST /api/auth/signup: create a new user account.
  Sample request: url: http://127.0.0.1:8000/api/auth/signup
  
                  body: 
                  {
                            "email": "muralipollam@gmail.com",
                            "password": "1234@Murali"
                        }
POST /api/auth/login: log in to an existing user account and receive an access token.

  Sample request: url: http://127.0.0.1:8000/api/auth/login
  
                  body: {
                            "email": "muralipollam@gmail.com",
                            "password": "1234@Murali"
                        }

GET /api/notes: get a list of all notes for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes,
 
                  headers={'token': Constants.token}
                  
GET /api/notes/ get a note by ID for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes/?id=1
 
                  headers={'token': Constants.token}
                  
POST /api/notes: create a new note for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes
 
                  headers={'token': Constants.token}
                  
                  body: {
                            "Heading": "NoteHeading",
                            "Content": "NoteContent"
                        }
PUT /api/notes/ update an existing note by ID for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes/
 
                  headers={'token': Constants.token}
                  
                  body: {
                            "NoteId": 1,
                            "Heading": "NoteHeading",
                            "Content": "NoteContent"
                        }
       
DELETE /api/notes/ delete a note by ID for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes/
 
                  headers={'token': Constants.token}
                  
                  body: {
                            "Heading": "NoteHeading",
                            "Content": "NoteContent"
                        }

POST /api/notes/:id/share: share a note with another user for the authenticated user.
 Sample request:  url: http://127.0.0.1:8000/api/notes/1/share
 
                  headers={'token': Constants.token}
                  
                  body: {
                            "NoteId": 1
                        }
GET /api/search?q=:query: search for notes based on keywords for the authenticated user.

 Sample request:  url: http://127.0.0.1:8000/api/search?q=sometimes+humour
 
                  headers={'token': Constants.token}
