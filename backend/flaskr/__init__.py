import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
    '''

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,PATCH,DELETE,OPTIONS"
        )
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
    '''

    @app.route("/categories", methods=["GET"])
    def get_category():

        if request.method == "GET":

            categories = Category.query.all()
            category_dic = {}

            for category in categories:
                category_dic[category.id] = category.type

            if len(categories) == 0:
                abort(404)

            return jsonify({
                'success': True,
                'categories': category_dic
            })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the
  bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
    '''

    @app.route('/questions', methods=["GET"])
    def get_questions():

        questions = Question.query.all()
        all_questions = paginate_questions(request, questions)

        categories = Category.query.all()
        current_category = Category.query.get(1).format()
        category_dic = {}
        lengh_questions = len(questions)

        for category in categories:
            category_dic[category.id] = category.type
        if lengh_questions == 0:
            abort(404)

        return jsonify(
            {
                'success': True,
                'questions': all_questions,
                'total_questions': lengh_questions,
                'categories': category_dic,
                'current_category': current_category
            }
        )

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).first()
            if question is None:
                abort(404)

            question.delete()
            questions = Question.query.all()
            all_questions = paginate_questions(request, questions)
            categories = Category.query.all()
            current_category = Category.query.get(1).format()
            category_dic = {}
            lengh_questions = len(questions)

            for category in categories:
                category_dic[category.id] = category.type

            return jsonify({
                'success': True,
                'deleted': question.id,
                'questions': all_questions,
                'total_questions': lengh_questions,
                'current_category': current_category,
                'categories': category_dic
            })

        except ValueError as e:
            print(e)
            abort(422)

    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
     '''
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
    '''

    @app.route('/questions', methods=["POST"])
    def create_question():

        data = request.get_json()

        question = data.get('question', None)
        answer = data.get('answer', None)
        difficulty = data.get('difficulty', None)
        category = data.get('category', None)
        search_questions = data.get('searchTerm', None)

        try:

            if search_questions:
                questions = Question.query.filter(
                    Question.question.ilike(f"%{search_questions}%")).all()
                paginated_questions = paginate_questions(request, questions)
                lengh_question = len(paginated_questions)

                return jsonify({
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': lengh_question
                })
            else:

                question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category)

                question.insert()

                questions = Question.query.order_by(Question.id).all()
                all_questions = paginate_questions(request, questions)

                categories = Category.query.all()
                category_dic = {}
                lengh_questions = len(questions)

                for category in categories:
                    category_dic[category.id] = category.type

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': all_questions,
                    'total_questions': lengh_questions,
                    'categories': category_dic
                })

        except BaseException:
            abort(422)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
    '''

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_category(category_id):

        try:

            category = Category.query.filter_by(id=category_id).first()
            print(category)

            if (category is None):
                abort(404)

            questions = Question.query.filter_by(category=category.id).all()
            print(questions)
            current_questions = paginate_questions(request, questions)
            lengh_questions = len(questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': lengh_questions,
                'current_category': category.type
            })

        except BaseException:
            abort(404)

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
    '''

    @app.route("/quizzes", methods=['POST'])
    def quiz_question():

        data = request.get_json()
        try:

            category = data['quiz_category']
            previous_questions = data['previous_questions']
            filter_questions = Question.id.notin_((previous_questions))
            required_category = category['id']
            selected_question = 0

            if required_category != 0:
                quiz_questions = Question.query.filter_by(
                    category=required_category).filter(filter_questions).all()

            else:
                quiz_questions = Question.query.filter(filter_questions).all()

            length_question = len(quiz_questions)

            if length_question > 0:
                selected_question = random.choice(quiz_questions).format()
                result = {
                    'success': True,
                    'question': selected_question
                }
            else:
                result = {
                    'success': True,
                    'question': None,
                    'empty': True
                }

            return jsonify(result)

        except BaseException:
            abort(400)

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
    '''

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not Found"
        }), 404

    @app.errorhandler(422)
    def unproccesable(error):

        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):

        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    return app
