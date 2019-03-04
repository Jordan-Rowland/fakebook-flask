@main.app_errorhandler(404)
def page_not_foun(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response


@main.app_errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
