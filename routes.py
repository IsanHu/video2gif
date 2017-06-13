#-*- coding:utf-8 -*-
from flask import jsonify
from flask import render_template
from flask import flash
from flask import current_app
from flask import abort


def list_routes(app):
    result = []
    for rt in app.url_map.iter_rules():
        result.append({
            'methods': list(rt.methods),
            'route': str(rt)
        })
    return jsonify({'routes': result, 'total': len(result)})




