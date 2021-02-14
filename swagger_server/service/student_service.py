import json
import logging
import os
import tempfile

from pymongo import MongoClient
import bson
from bson.objectid import ObjectId
from swagger_server.models import Student

client = MongoClient('mongodb://mongodb:27017/')
#mongodb://127.0.0.1:27017/mongo_db_name
#client = MongoClient('mongodb', 27017)
db = client.swagger_db
student_db = db.students


def add_student(student):
    if (student.first_name is None) | (student.last_name is None):
        return 'provide all information', 405

    query = {
        'first_name': student.first_name,
        'last_name': student.last_name,
        'grades': student.grades
            }

    res = student_db.find_one(query)
    if res:
        return 'already exists', 409
    
    # mongodb specific, integer id had to be changed to string
    doc_id = student_db.insert_one(query).inserted_id
    student.student_id = str(doc_id)
    return student.student_id


def get_student_by_id(student_id, subject):
    try:
        student_id = ObjectId(student_id)
    except bson.errors.InvalidId:
        student_id = ObjectId()

    student = student_db.find_one({'_id': student_id})
    if not student:
        return student
    student = Student.from_dict(student)
    if not subject:
        return student
    if subject in student.grades.keys():
        return student
    else:
        return 'subject not in grades', 404
    return student


def get_student_by_last_name(last_name):
    student = student_db.find_one({'last_name': last_name})
    if not student:
        return student
    student = Student.from_dict(student)
    return student


def delete_student(student_id):
    try:
        student_id = ObjectId(student_id)
    except bson.errors.InvalidId:
        student_id = ObjectId()

    query = {'_id': student_id}
    student = student_db.find_one(query)
    if not student:
        return student
    student_db.delete_one(query)
    return str(student_id)
