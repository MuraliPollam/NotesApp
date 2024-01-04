import json
import jwt
import datetime
import re
from . import Constants
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import UserDetails, Notes, WordSet


def checkEmailPattern(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))


def checkPasswordRequirements(password):
    min_length = 6
    has_uppercase = re.search(r'[A-Z]', password)
    has_lowercase = re.search(r'[a-z]', password)
    has_digit = re.search(r'\d', password)
    has_special_char = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

    return (
            len(password) >= min_length and
            has_uppercase and
            has_lowercase and
            has_digit and
            has_special_char
    )


def checkIfAuthenticatedAndReturnUserId(token):
    try:
        secretKey = "Speer"
        payload = jwt.decode(token, secretKey, algorithms=['HS256'])
        userId = payload['UserId']
        return userId
    except Exception:
        raise Exception("The given token is not Correct")


def createWordSet(paragraph):
    words = paragraph.split()
    words = [word.lower() for word in words]
    excludedWords = {'the', 'a', 'an', 'and'}
    filteredWords = [word for word in words if word not in excludedWords]
    filteredWords = [''.join(char for char in word if char.isalnum()) for word in filteredWords]
    return set(filteredWords)


def updateWordSet(content, userId, note):
    uniqueWords = createWordSet(content)
    wordsSet = WordSet.objects.filter(user_id=userId).first()
    temp = wordsSet.wordSet
    if temp == "":
        hashTable = {}
    else:
        hashTable = json.loads(temp)
    for i in uniqueWords:
        try:
            hashTable[i].append(note.noteId)
        except:
            hashTable[i] = [note.noteId]
    wordsSet.wordSet = json.dumps(hashTable)
    wordsSet.save()


class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        jsonData = request.data
        email = jsonData['email'].lower()
        password = jsonData['password']
        if not checkEmailPattern(email):
            return Response({Constants.errorMessage: "Email is format is incorrect."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not checkPasswordRequirements(password):
            return Response({Constants.errorMessage: "Password is not strong enough."},
                            status=status.HTTP_400_BAD_REQUEST)
        user = UserDetails.objects.create(
            password=password,
            email=email
        )
        WordSet.objects.create(
            user_id=user.userId,
            wordSet=""
        )
        return Response({Constants.message: Constants.successMessage})


class SignIn(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        jsonData = request.data
        email = jsonData['email'].lower()
        password = jsonData['password']
        user = UserDetails.objects.filter(email=email).first()
        if user is None:
            return Response({Constants.errorMessage: "User Not Registered"}, status=status.HTTP_404_NOT_FOUND)
        else:
            if user.password != password:
                return Response({Constants.errorMessage: "Password is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                payload = {
                    Constants.userId: user.userId,
                    Constants.creationTime: str(datetime.datetime.utcnow())
                }
                secretKey = "Speer"
                token = jwt.encode(payload, secretKey, algorithm='HS256')
                return Response({"token": token}, status=status.HTTP_200_OK)


class NotesList(APIView):

    def get(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        notesByUser = Notes.objects.filter(user_id=userId)
        notes = []
        for note in notesByUser:
            notes.append({
                Constants.noteId: note.noteId,
                Constants.heading: note.heading,
                Constants.content: note.content
            })
        return Response({"Notes": notes}, status=status.HTTP_200_OK)

    def post(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        jsonData = request.data
        heading = jsonData[Constants.heading]
        content = jsonData[Constants.content]
        note = Notes.objects.create(
            heading=heading,
            content=content,
            user_id=userId
        )
        updateWordSet(content, userId, note)
        return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)


class NoteById(APIView):
    def get(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        requestedNoteId = request.GET['id']
        note = Notes.objects.filter(noteId=requestedNoteId).first()
        if note is None:
            return Response({Constants.errorMessage: "The requested note is not found"},
                            status=status.HTTP_404_NOT_FOUND)
        if userId != note.user_id:
            return Response({Constants.errorMessage: "The requested note is written by the user"},
                            status=status.HTTP_403_FORBIDDEN)

        return Response({
            Constants.heading: note.heading,
            Constants.content: note.content
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        jsonData = request.data
        noteId = jsonData[Constants.noteId]
        note = Notes.objects.filter(noteId=noteId).first()
        if note is None:
            return Response({Constants.errorMessage: "The requested note is not found"},
                            status=status.HTTP_404_NOT_FOUND)
        if userId != note.user_id:
            return Response({Constants.errorMessage: "The requested note is written by the user"},
                            status=status.HTTP_403_FORBIDDEN)
        note.delete()

        return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)

    def put(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        jsonData = request.data
        noteId = jsonData[Constants.noteId]
        content = jsonData[Constants.content]
        heading = jsonData[Constants.heading]
        note = Notes.objects.filter(noteId=noteId).first()
        if note is None:
            return Response({Constants.errorMessage: "The requested note is not found"},
                            status=status.HTTP_404_NOT_FOUND)
        if userId != note.user_id:
            return Response({Constants.errorMessage: "The requested note is written by the user"},
                            status=status.HTTP_403_FORBIDDEN)
        note.heading = heading
        note.content = content
        note.save()

        return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)


# class AddNote(APIView):
#     def post(self, request):
#         token = request.headers['token']
#         try:
#             userId = checkIfAuthenticatedAndReturnUserId(token)
#         except Exception as e:
#             return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
#         jsonData = request.data
#         heading = jsonData[Constants.heading]
#         content = jsonData[Constants.content]
#         note = Notes.objects.create(
#             heading=heading,
#             content=content,
#             user_id=userId
#         )
#         updateWordSet(content, userId, note)
#         return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)


# class DeleteNote(APIView):
# def delete(self, request):
#     token = request.headers['token']
#     try:
#         userId = checkIfAuthenticatedAndReturnUserId(token)
#     except Exception as e:
#         return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
#     jsonData = request.data
#     noteId = jsonData[Constants.noteId]
#     note = Notes.objects.filter(noteId=noteId).first()
#     if note is None:
#         return Response({Constants.errorMessage: "The requested note is not found"},
#                         status=status.HTTP_404_NOT_FOUND)
#     if userId != note.user_id:
#         return Response({Constants.errorMessage: "The requested note is written by the user"},
#                         status=status.HTTP_403_FORBIDDEN)
#     note.delete()
#
#     return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)


class ShareNote(APIView):
    def post(self, request, id):
        token = request.headers['token']
        jsonData = request.data
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)
        sharedUser = UserDetails.objects.filter(userId=id).first()
        if sharedUser is None:
            return Response({Constants.errorMessage: "User Not Registered"}, status=status.HTTP_404_NOT_FOUND)
        noteId = jsonData[Constants.noteId]
        note = Notes.objects.filter(noteId=noteId).first()
        if note is None:
            return Response({Constants.errorMessage: "The requested note is not found"},
                            status=status.HTTP_404_NOT_FOUND)
        if userId != note.user_id:
            return Response({Constants.errorMessage: "The requested note is written by the user"},
                            status=status.HTTP_403_FORBIDDEN)
        newNote = Notes.objects.create(
            heading=note.heading,
            content=note.content,
            user_id=id
        )
        updateWordSet(note.content, id, newNote)

        return Response({Constants.message: Constants.successMessage}, status=status.HTTP_200_OK)


class SearchUsingKeyWords(APIView):
    def get(self, request):
        token = request.headers['token']
        try:
            userId = checkIfAuthenticatedAndReturnUserId(token)
        except Exception as e:
            return Response({Constants.errorMessage: repr(e)}, status=status.HTTP_403_FORBIDDEN)

        wordsSet = WordSet.objects.filter(user_id=userId).first()
        keywords = request.GET['q']
        keywords = keywords.split(" ")
        noteIds = []
        hashTable = json.loads(wordsSet.wordSet)
        for i in keywords:
            noteIds.extend(hashTable.get(i, []))
        noteIds = set(noteIds)
        return Response({"NoteIds": noteIds}, status=status.HTTP_200_OK)
