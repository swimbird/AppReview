#!/usr/bin/python
# -*- encoding:utf8 -*-
import os
from werkzeug import url_decode
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort, g, jsonify
import json
from pprint import pprint

__base = os.path.dirname(os.path.abspath(__file__))
__database = os.path.normpath(os.path.join(__base, '../scripts/db/app.db'))
__table = 'reviews'


app = Flask(__name__)

class MethodRewriteMiddleware(object):
    """Middleware for HTTP method rewriting.

    Snippet: http://flask.pocoo.org/snippets/38/
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('__METHOD_OVERRIDE__')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/crossdomain.xml')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'crossdomain.xml', mimetype='text/xml')

def connect_db():
    return sqlite3.connect(__database)

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'status':'error'}), 400

def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func

@app.route('/review/<id>')
@app.route('/review/<id>?limit=<limit>&offset=<offset>&star=<star>')
def show_review(id):
    limit  = request.args.get('limit') if request.args.get('limit') else 10
    offset = request.args.get('offset') if request.args.get('offset') else 0
    star = request.args.get('star')
    app.logger.debug('id=%s\nlimit=%s\noffset=%s\nstar=%s', id, limit, offset, star)

    if id:
        if is_id(id):
            reviews = select_review(id, limit, offset, star)
        else:
            abort(400)
    else:
        abort(400)

    @after_this_request
    def add_json_header(response):
        print response
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    return json.dumps(reviews, ensure_ascii=False)
    #return jsonify(reviews)

def is_id(id):
    app_id = query_db('select * from reviews where app_id=?',
                    [id], one=True)
    if app_id is None:
        app.logger.debug('No such app_id')
        return False
    else:
        return True

def select_review(id, limit, offset, star):
    reviews = {}
    reviews["appid"]  = id
    reviews["limit"]  = limit
    reviews["offset"] = offset
    reviews["status"] = 'ok'
    reviews["review"] = []

    if star:
        sql =  'select * from reviews where app_id=? and star=? order by date desc limit ?, ?'
        bind = ["com.rovio.angrybirds", star, offset, limit]
    else:
        sql = 'select * from reviews where app_id=? order by date desc limit ?, ?'
        bind = ["com.rovio.angrybirds", offset, limit]

    for review in query_db(sql, bind):
        #print review
        item = {
            'id'   : review['id'],
            'hash' : review['hash'],
            'user' : review['user'],
            'date' : review['date'],
            'title': review['title'],
            'body' : review['body'],
            'version' : review['version'],
            'device' : review['device'],
            'app_id' : review['app_id'],
            'nodes' : review['nodes'],
            'star' : review['star'],
            'created_at' : review['created_at']
        }
        reviews["review"].append(item)

    #app.logger.debug(json.dumps(reviews))

    return reviews

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'secret'
    app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
    app.run()
