# -*- coding: utf-8 -*-

from flask import Flask
from flask import request, jsonify, render_template, session, g
from apiflask import app, db
from apiflask.models import Student

from library import *

app.secret_key = 'zhufree'


@app.route('/')
def index():
    if 'stuid' in session:
        cur_stu = Student.query.filter(Student.stuid==session['stuid']).first()
        return render_template('index.html', stu=cur_stu)
    else:
        return render_template('index.html')


@app.route('/login/', methods=['POST'])
def loginLibrary():
    session.permanent = True
    stuid = request.form.get('sid')
    cur_stu = Student.query.filter(Student.stuid==stuid).first()
    if cur_stu:
        login_result = getcookie(cur_stu.stuid, cur_stu.stupwd)
        if login_result['status']:
            session['stuid'] = cur_stu.stuid
            session['_cookie'] = login_result['info']
            result = {
                    'status': True,
                    'info': cur_stu.stuid
            }
            return jsonify(result)
        else:
            error = {
                'status': False,
                'info': 'Invalid username/password'
            }
            return jsonify(error)
    else:
        login_result = getcookie(request.form.get('sid'), request.form.get('pwd'))
        if login_result['status']:
            new_stu = Student(stuid=request.form.get('sid'), stupwd=request.form.get('pwd'))
            db.session.add(new_stu)
            db.session.commit()
            session['stuid'] = new_stu.stuid
            session['_cookie'] = login_result['info']
            result = {
                'status': True,
                'info': new_stu.stuid
            }
            return jsonify(result)
        else:
            error = {
                'status': False,
                'info': 'Invalid username/password'
            }
            return jsonify(error)


@app.route('/whubook/')
def bookIndex():
    return render_template('whubook.html')


@app.route('/whubook/history/', methods=['POST'])
def historyBook():
    query_result = queryhistory(session['_cookie'])
    if query_result['status']:
        result = {"status": True, "info": query_result['info']}
    else:
        result = {"status": False, "info": query_result['reason']}
    return jsonify(result)


@app.route('/whubook/current/', methods=['POST'])
def currentBook():
    query_result = queryloan(session['_cookie'])
    if query_result['status']:
        result = {"status": True, "info": query_result['info']}
    else:
        result = {"status": False, "info": query_result['reason']}
    return jsonify(result)


@app.route('/whubook/renewall/', methods=['POST'])
def renewall_():
    renew_result = renewall(session['_cookie'])
    if renew_result['status']:
        result = {"status": True, "info": renew_result['info']}
    else:
        result = {"status": False, "info": renew_result['reason']}
    return jsonify(result)


@app.route('/whubook/renew/', methods=['POST'])
def renew_():
    number = int(request.form.get('number'))
    renew_result = renew(session['_cookie'], number)
    if renew_result['status']:
        result = {"status": True, "info": renew_result['info']}
    else:
        result = {"status": False, "info": renew_result['reason']}
    return jsonify(result)


@app.route('/whubook/search/', methods=['POST'])
def search():
    keyword = request.form.get('keyword', '')
    search_result = searchbook(session['_cookie'], keyword)
    # print search_result
    if search_result['status']:
        if isinstance(search_result['info'], dict):
            session['books_info'] = search_result['info']['books_info']
            result = {
                "status": True, 
                "info": search_result['info']['books_info'], 
                "next_page_link": search_result['info']['next_page_link']
                }
            # print result
        else:
            session['books_info'] = search_result['info']
            result = {
                "status": True, 
                "info": search_result['info']
                }
            # print result
    else:
        result = {"status": False, "info": search_result['reason']}
    return jsonify(result)


@app.route('/whubook/nextpage/', methods=['POST'])
def next_page():
    next_page_link = request.form.get('next_page_link', '')
    search_result = catch_book_info(next_page_link)
    # print search_result
    session['books_info'] += search_result[0]
    result = {
        "status": True, 
        "info": search_result[0], 
        "next_page_link": search_result[1]
        }
    return jsonify(result)


@app.route('/whubook/order/', methods=['POST'])
def order():
    num = request.form.get('num', '')
    books_info = session['books_info']
    book_to_order = None
    for book in books_info:
        if book['BookNum'] == num:
            book_to_order = book
    if book_to_order:
        order_result = orderbook(session['_cookie'], book_to_order)
        if order_result['status']:
            result = {"status": True, "info": order_result['info']}
        else:
            result = {"status": False, "info": order_result['reason']}
    else:
        result = {"status": False, "info": 'no such book'}
    return jsonify(result)#


@app.route('/whubook/queryorder/', methods=['POST'])
def queryorder_():
    query_result = queryorder(session['_cookie'])
    if query_result['status']:
        session['orders'] = query_result['info']
        result = {"status": True, "info": query_result['info']}
    else:
        result = {"status": False, "info": query_result['reason']}
    return jsonify(result)


@app.route('/whubook/deleteorder/', methods=['POST'])
def deleteorder_():
    num = request.form.get('num', '')
    orders = session['orders']
    order_to_delete = None
    for order in orders:
        if order['BookNum'] == num:
            order_to_delete = order
    if order_to_delete:
        delete_reault = deleteorder(session['_cookie'], order_to_delete)
        if delete_reault['status']:
            result = {"status": True, "info": delete_reault['info']}
        else:
            result = {"status": False, "info": delete_reault['result']}
    else:
        result = {"status": False, "info": 'no such order'}
    return jsonify(result)