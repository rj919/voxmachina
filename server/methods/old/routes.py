__author__ = 'rcj1492'
__created__ = '2016.05'
__license__ = 'MIT'

# OLD METHODS for other projects
# @app.route('/v1/user/details')
# def user_details():
#     valid_response, code = userAuth.request.validate(request)
#     if code:
#         return jsonify(valid_response), code
#     request_dict = {'headers': {}, 'body': request.form}
#     for key, value in request.headers.items():
#         request_dict['headers'][key] = value
#     app.logger.debug('Headers: %s' % request_dict)
#     model_details = userAuth.model
#     return render_template('model.html', modelDetails=model_details), 200
#
# @app.route('/v1/tink/twilio/sms', methods=['POST'])
# def tink_twilio_sms():
#     valid_response, code = twilioSMS.validate(request)
#     if code:
#         return jsonify(valid_response), code
#     twilio_response = twiml.Response()
#     request_dict = { 'headers': {}, 'body': request.form }
#     for key, value in request.headers.items():
#         request_dict['headers'][key] = value
#     reply_dict = smsRelay.post(request_dict)
#     if not reply_dict:
#         reply_dict['message'] = 'Faerie-phone currently out of area.\nTry my faerie-mail: tink@collectiveacuity.com'
#     twilio_response.message(reply_dict['message'])
#     return str(twilio_response), 200
#
# @app.route('/v1/tink/web/im', methods=['POST'])
# def tink_web_im():
#     valid_response, code = webIM.validate(request)
#     if code:
#         return jsonify(valid_response), code
#     # method to convert request data in model into usable dictionaries
#     # method to check authenticity of requester
#     request_dict = { 'headers': {}, 'body': request.form }
#     for key, value in request.headers.items():
#         request_dict['headers'][key] = value
#     reply_dict = smsRelay.post(request_dict)
#     if not reply_dict:
#         reply_dict['message'] = 'AFK...\nTry my faerie-mail: tink@collectiveacuity.com'
#     return jsonify(reply_dict), 200
#