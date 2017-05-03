#-*- coding:utf-8 -*-
from flask import jsonify
from flask import render_template
from flask import flash
from flask import current_app
from flask import abort

import os

def init_route(app):
    app.add_url_rule('/', 'home', home, methods=['GET'])
    app.add_url_rule('/api', 'list_routes', list_routes, methods=['GET'], defaults={'app': app})


def home():
    return render_template('home.html')
    pass


def list_routes(app):
    result = []
    for rt in app.url_map.iter_rules():
        result.append({
            'methods': list(rt.methods),
            'route': str(rt)
        })
    return jsonify({'routes': result, 'total': len(result)})




