from rest_framework import status
from . import Constants
from django.test import TestCase
from rest_framework.test import APITestCase
from .models import UserDetails, Notes


class SignUpTests(APITestCase):
    fixtures = ['notes/test.json']

    def test_signUp_success(self):
        testData = {
            "email": Constants.testEmail,
            "password": Constants.testPassword
        }
        response = self.client.post('/api/auth/signup', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = UserDetails.objects.filter(email=Constants.testEmail).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.password, Constants.testPassword)

    def test_signUp_failureWeakPassword(self):
        testData = {
            "email": Constants.testEmail,
            "password": Constants.testWeakPassword
        }
        response = self.client.post('/api/auth/signup', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[Constants.errorMessage], Constants.passwordErrorMessage)

    def test_signUp_failureWrongEmailPattern(self):
        testData = {
            "email": Constants.testWrongEmail,
            "password": Constants.testPassword
        }
        response = self.client.post('/api/auth/signup', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data[Constants.errorMessage], Constants.emailErrorMessage)

    def test_signUp_failureNoPassword(self):
        testData = {
            "email": Constants.testWrongEmail
        }
        response = self.client.post('/api/auth/signup', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignInTests(APITestCase):
    fixtures = ['notes/test.json']

    def test_signIn_success(self):
        testData = {
            "email": Constants.emailInDB,
            "password": Constants.passwordInDB
        }
        response = self.client.post('/api/auth/login', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['token'])

    def test_signIn_failureWrongEmail(self):
        testData = {
            "email": Constants.testEmail,
            "password": Constants.passwordInDB
        }
        response = self.client.post('/api/auth/login', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data[Constants.errorMessage], Constants.notRegisteredMessage)

    def test_signIn_failureWrongPassword(self):
        testData = {
            "email": Constants.emailInDB,
            "password": Constants.testPassword
        }
        response = self.client.post('/api/auth/login', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data[Constants.errorMessage], Constants.incorrectPasswordMessage)

    def test_signIn_failureNoEmail(self):
        testData = {
            "password": Constants.passwordInDB
        }
        response = self.client.post('/api/auth/signup', data=testData, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotesListTests(APITestCase):
    fixtures = ['notes/test.json']

    # Tests for NotesList GET API.
    def test_NotesListGET_success(self):
        response = self.client.get('/api/notes', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = response.data['Notes']
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0][Constants.noteId], 1)

    def test_NotesListGET_failureInvalidToken(self):
        response = self.client.get('/api/notes', headers={'token': Constants.one})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data[Constants.errorMessage], repr(Exception(Constants.incorrectTokenMessage)))

    # Tests for NotesList POST API.
    def test_NotesListPOST_success(self):
        testData = {
            Constants.heading: Constants.heading,
            Constants.content: Constants.content
        }
        response = self.client.post('/api/notes', headers={'token': Constants.token}, data=testData)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = Notes.objects.all()
        self.assertEqual(len(notes), 4)


class NoteByIdTests(APITestCase):
    fixtures = ['notes/test.json']

    # Tests for NoteById GET API.
    def test_NoteByIdGET_success(self):
        response = self.client.get('/api/notes/?id=1', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        noteHeading = response.data[Constants.heading]
        noteContent = response.data[Constants.content]
        self.assertEqual(noteHeading, Constants.noteHeading)
        self.assertEqual(noteContent, Constants.noteContent)

    def test_NoteByIdGET_failureNoteNotFound(self):
        response = self.client.get('/api/notes/?id=5', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data[Constants.errorMessage], Constants.noteNotFoundMessage)

    def test_NoteByIdGET_failureNotUsersNote(self):
        response = self.client.get('/api/notes/?id=4', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data[Constants.errorMessage], Constants.noteNotAuthoredByUserMessage)

    # Tests for NoteById DELETE API.
    def test_NotesByIdDELETE_success(self):
        testData = {
            Constants.heading: Constants.heading,
            Constants.content: Constants.content
        }
        response = self.client.delete('/api/notes/?id=2', headers={'token': Constants.token}, data=testData)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = Notes.objects.all()
        self.assertEqual(len(notes), 2)

    # Tests for NotesList PUT API.
    def test_NoteByIdPUT_success(self):
        testData = {
            Constants.noteId: Constants.one,
            Constants.heading: Constants.heading,
            Constants.content: Constants.content
        }
        response = self.client.put('/api/notes/', headers={'token': Constants.token}, data=testData)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note = Notes.objects.filter(noteId=Constants.one).first()
        self.assertEqual(note.heading, Constants.heading)
        self.assertEqual(note.content, Constants.content)


class ShareNoteTest(APITestCase):
    fixtures = ['notes/test.json']

    def test_ShareNote_success(self):
        testData = {
            Constants.noteId: Constants.one
        }
        response = self.client.post('/api/notes/2/share', headers={'token': Constants.token}, data=testData)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = Notes.objects.all()
        self.assertEqual(len(notes), 4)


class SearchUsingKeyWordsTest(APITestCase):
    fixtures = ['notes/test.json']

    def test_SearchUsingKeyWords_success(self):
        response = self.client.get('/api/search?q=sometimes+humour', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        noteIds = response.data['NoteIds']
        self.assertEqual(len(noteIds), 2)

    def test_SearchUsingKeyWords_successWithRandomWords(self):
        response = self.client.get('/api/search?q=abccd+xtyzz', headers={'token': Constants.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        noteIds = response.data['NoteIds']
        self.assertEqual(len(noteIds), 0)
# Create your tests here.
