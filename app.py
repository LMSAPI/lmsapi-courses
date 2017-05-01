from flask import Flask, request, abort
from flask_pymongo import PyMongo
from functools import wraps
from bson import json_util

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'heroku_k0kdm9jl'
app.config['MONGO_URI'] = 'mongodb://test_user:test_pass@ds157380.mlab.com:57380/heroku_k0kdm9jl'
app.secret_key = 'mysecret'

mongo = PyMongo(app)


def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and key_exists(request.args.get('key')):
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.route('/')
@require_appkey
def root():
    return 'hello there'


@app.route('/courses/<course>/student', methods=['POST', 'GET', 'PUT', 'DELETE'])
@require_appkey
def student_courses(course):
    mongo_student_courses = mongo.db.student_courses
    teacheruser = user_name(request.args.get('key'))

    # get all students in course
    if request.method == 'GET':
        courses_resp = mongo_student_courses.find({'number': course, 'teacheruser': teacheruser})
        return json_util.dumps(courses_resp)

    # insert new student into course
    if request.method == 'POST':
        existing_course = mongo_student_courses.find_one({'number': course,
                                                          'email': request.args.get('email'),
                                                          'teacheruser': teacheruser})
        if existing_course is None:
            mongo_student_courses.insert({'number': course,
                                          'email': request.args.get('email'),
                                          'enrolled': request.args.get('enrolled'),
                                          'teacheruser': teacheruser})
            return 'Added'

        return 'already exists!'

    # update a student in a course
    if request.method == 'PUT':
        existing_course = mongo_student_courses.find_one({'number': course,
                                                          'email': request.args.get('email'),
                                                          'teacheruser': teacheruser})
        if existing_course is not None:
            print(request.args)
            mongo_student_courses.update_one({'number': course,
                                              'email': request.args.get('email'),
                                              'teacheruser': teacheruser},
                                             {'$set': {'enrolled': request.args.get('enrolled')}})
            return 'Updated'

        return 'Update failed'

    # delete a student from a course
    if request.method == 'DELETE':
        existing_course = mongo_student_courses.find_one({'number': course,
                                                          'email': request.args.get('email'),
                                                          'teacheruser': teacheruser})
        if existing_course is not None:
            mongo_student_courses.delete_one({'number': course,
                                              'email': request.args.get('email'),
                                              'teacheruser': teacheruser})
            return 'Deleted'

        return 'Delete failed'


@app.route('/courses', methods=['POST', 'GET'], defaults={'course': None})
@app.route('/courses/<course>', methods=['PUT', 'DELETE'])
@require_appkey
def courses(course):
    mongo_courses = mongo.db.courses
    teacheruser = user_name(request.args.get('key'))

    # get all courses
    if request.method == 'GET':
        courses_resp = mongo_courses.find({'teacheruser': teacheruser})
        return json_util.dumps(courses_resp)

    # insert new course
    if request.method == 'POST':
        existing_course = mongo_courses.find_one({'number': request.args.get('number'), 'teacheruser': teacheruser})
        if existing_course is None:
            mongo_courses.insert({'number': request.args.get('number'),
                                  'title': request.args.get('title'),
                                  'prereq': request.args.get('prereq'),
                                  'teacheruser': teacheruser})
            return 'Added'

        return 'already exists!'

    # update a course
    if request.method == 'PUT':
        existing_course = mongo_courses.find_one({'number': course, 'teacheruser': teacheruser})
        if existing_course is not None:
            print(request.args)
            mongo_courses.update_one({'number': course, 'teacheruser': teacheruser},
                                     {'$set': {'title': request.args.get('title'),
                                               'prereq': request.args.get('prereq')}})
            return 'Updated'

        return 'Update failed'

    # delete a course
    if request.method == 'DELETE':
        existing_course = mongo_courses.find_one({'number': course, 'teacheruser': teacheruser})
        if existing_course is not None:
            mongo_courses.delete_one({'number': course, 'teacheruser': teacheruser})
            return 'Deleted'

        return 'Delete failed'


def obj_dict(obj):
    return obj.__dict__


def user_name(key):
    users = mongo.db.users
    user = users.find_one({'apikey': key})
    return user['name']


def key_exists(key):
    users = mongo.db.users
    user_key = users.find_one({'apikey':key})

    if user_key is None:
        return False

    return True


if __name__ == '__main__':
    app.run(debug=True)
