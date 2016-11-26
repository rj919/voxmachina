/* LAB JAVASCRIPT EXTENSION */
/* MIT License 2016 rcj1492 */
/* Requires jQuery >= 2.2.3 */
/* Requires modernizr-custom */

/* JQUERY DOCUMENTATION */
/* https://api.jquery.com/ */

/* ANGULARJS DOCUMENTATION */
/* https://angularjs.org/ */

/* BOOTSTRAP DOCUMENTATION */
/* https://getbootstrap.com/javascript/ */

var messageMap = {
    '^\\.': 'cannot start with "."',
    '\\.\\.': 'cannot contain ".."',
    '\\.@': 'username cannot end with "."',
    '@\\.': 'domain name cannot start with "."',
    '\\.$': 'domain name cannot end with "."',
    '[\\"\\s<>(),]': 'cannot contain "<>(), characters or spaces.',
    '^[\\w\\-_\\.\\+]{1,24}?@[\\w\\-\\.]{1,24}?\\.[a-z]{2,10}$': 'is not a valid email address.'
};

function openDialog(dialog_id) {

/* a method to open (and close) a dialog div */

// validate input
    var id_pattern = /^#/;
    if (!id_pattern.test(dialog_id)){
        var dialog_id = '#' + dialog_id;
    };

// construct selector for javascript link children
    var dialog_links = dialog_id + ' [href="javascript:void(0)"]';
    var dialog_close = dialog_links + ':first';

// open up dialog and dialog backdrop;
    $(dialog_id).show();
    $('#dialog_backdrop').show();
    $(dialog_close).focus();

// bind event handlers to close dialogs
    $(dialog_links).click(function(){
        $(dialog_id).hide();
        $('#dialog_backdrop').hide();
    });
    $('#dialog_backdrop').click(function(){
        $(dialog_id).hide();
        $('#dialog_backdrop').hide();
    });

}

function nativeDialog(dialogID, closeID) {

    /*
    method to open dialog with native css3
    NOTE:   to prevent auto selection on open use:
            <input autofocus class="hide">
    */

   	var dialog = document.getElementById(dialogID);
   	var dialogBackdrop = document.getElementById('dialog_backdrop');
	dialog.show();
    dialogBackdrop.show();
	document.getElementById(closeID).onclick = function() {
		dialog.close();
		dialogBackdrop.close();
	};
	dialogBackdrop.addEventListener('click', function() {
	    dialog.close();
		dialogBackdrop.close();
	});
}

function responsiveDialog(dialog_id_mobile, dialog_id_desktop) {

// construct selector for dialog javascript link children
    var dialog_id_backdrop = '#dialog_backdrop';
    var dialog_links_mobile = dialog_id_mobile + ' [href="javascript:void(0)"]';
    var dialog_links_desktop = dialog_id_desktop + ' [href="javascript:void(0)"]';

// open up dialog and dialog backdrop;
    $(dialog_id_mobile).show();
    $(dialog_id_mobile).addClass("hidden-lg hidden-md hidden-sm")
    $(dialog_id_desktop).show();
    $(dialog_id_desktop).addClass("hidden-xs")
    $(dialog_id_backdrop).show();

// bind event handlers to close dialogs
    $(dialog_links_mobile).click(function(){
        $(dialog_id_mobile).hide();
        $(dialog_id_mobile).removeClass("hidden-lg hidden-md hidden-sm")
        $(dialog_id_desktop).hide();
        $(dialog_id_desktop).removeClass("hidden-xs")
        $(dialog_id_backdrop).hide();
    });
    $(dialog_links_desktop).click(function(){
        $(dialog_id_mobile).hide();
        $(dialog_id_mobile).removeClass("hidden-lg hidden-md hidden-sm")
        $(dialog_id_desktop).hide();
        $(dialog_id_desktop).removeClass("hidden-xs")
        $(dialog_id_backdrop).hide();
    });
    $(dialog_id_backdrop).click(function(){
        $(dialog_id_mobile).hide();
        $(dialog_id_mobile).removeClass("hidden-lg hidden-md hidden-sm")
        $(dialog_id_desktop).hide();
        $(dialog_id_desktop).removeClass("hidden-xs")
        $(dialog_id_backdrop).hide();
    });

}

function removeText(jquery_selector) {

// a helper class for removing text in the DOM

    $(jquery_selector).contents().filter(function() {
        return this.nodeType == 3; // node type for text
    }).remove();

}

function injectPlaceholder(input_selector, placeholder_value) {

/* a helper method for injecting data into an input placeholder */

    $(input_selector).attr('placeholder', placeholder_value);

}

function convertElement(element_selector, new_tag) {

// construct method variables
    var old_tag = $(element_selector)[0].tagName.toLowerCase()
    var new_element_tag = '<' + new_tag + '></' + new_tag + '>'

// construct a new element
    var new_element = $(new_element_tag)

// add each attribute to new element
    $(element_selector).each(function() {
        $.each(this.attributes, function() {
            if(this.specified) {
                new_element.attr(this.name, this.value)
            };
        });
    });

// add inner html contents to new element
    new_element.html($(element_selector)[0].innerHTML)

// add/remove href attributes to/from new element
    if (new_tag == 'a'){
        new_element.attr('href', 'javascript:void(0)')
    } else if (old_tag == 'a'){
        new_element.removeAttr('href')
    };

// update DOM with replaced element
    $(element_selector).replaceWith(new_element)

}

function showMessage(anchor_selector, message_text, message_status, message_location, timeout) {

/* a method to display a message below an input field */

// retrieve page variables
    if (typeof(message_status) === 'undefined'){ var message_status = '' }
    if (typeof(message_location) === 'undefined'){ var message_location = 'overlay' }
    if (typeof(timout) === 'undefined'){ var timeout = null }
    var anchor_position = $(anchor_selector).offset()
    var anchor_width = $(anchor_selector).width()
    var anchor_height = $(anchor_selector).height()
    var message_dialog_name = 'dialog_status_message_' + anchor_selector.replace('#','').toLowerCase()
    var message_dialog_id = '#' + message_dialog_name;

// remove any previous dialogs with same name
    if ($(message_dialog_id).length){
        $(message_dialog_id).remove();
    };

// construct HTML content
    var message_dialog_html = '<div id="' + message_dialog_name + '" style="display: none;"></div>'
    var message_class_list = [ 'dialog-box', 'dialog-tooltip', 'page-status-message', 'padding-vertical-5', 'padding-horizontal-5', 'font-mini' ];
    if (message_status == 'success') {
        message_class_list.push('font-success');
    } else if (message_status == 'error') {
        message_class_list.push('font-error');
    };
    var message_class_string = ''
    for (var i = 0; i < message_class_list.length; i++){
        message_class_string += message_class_list[i] + ' '
    }

// inject dialog into DOM
    $('body').append(message_dialog_html);
    var message_dialog = $(message_dialog_id);
    message_dialog.addClass(message_class_string);
    message_dialog.html(message_text);

// calculate position for message
    if (message_location == 'bottom'){
        var message_width = message_dialog.width();
        var message_padding_top = message_dialog.css('padding-top')
        var message_padding_top = parseFloat(message_padding_top.replace(/[^-\d\.]/g, ''))
        var message_top = anchor_position.top + anchor_height + message_padding_top
        var message_left = anchor_position.left + (anchor_width / 2) - (message_width / 2)
    } else if (message_location == 'top'){
        var message_width = message_dialog.width();
        var message_height = message_dialog.height();
        var message_padding_bottom = message_dialog.css('padding-bottom')
        var message_padding_bottom = parseFloat(message_padding_bottom.replace(/[^-\d\.]/g, ''))
        var message_top = anchor_position.top - message_height - (message_padding_bottom * 3)
        var message_left = anchor_position.left + (anchor_width / 2) - (message_width / 2)
    } else if (message_location == 'right'){
        var message_padding_top = message_dialog.css('padding-top')
        var message_padding_top = parseFloat(message_padding_top.replace(/[^-\d\.]/g, ''))
        var message_padding_right = message_dialog.css('padding-right')
        var message_padding_right = parseFloat(message_padding_right.replace(/[^-\d\.]/g, ''))
        var message_top = anchor_position.top - message_padding_top
        var message_left = anchor_position.left + anchor_width + message_padding_right
    } else if (message_location == 'left'){
        var message_width = message_dialog.width();
        var message_padding_top = message_dialog.css('padding-top')
        var message_padding_top = parseFloat(message_padding_top.replace(/[^-\d\.]/g, ''))
        var message_padding_right = message_dialog.css('padding-right')
        var message_padding_right = parseFloat(message_padding_right.replace(/[^-\d\.]/g, ''))
        var message_top = anchor_position.top - message_padding_top
        var message_left = anchor_position.left - message_width - (message_padding_right * 2.5)
    } else {
        var message_width = message_dialog.width();
        var message_padding_top = message_dialog.css('padding-top')
        var message_padding_top = parseFloat(message_padding_top.replace(/[^-\d\.]/g, ''))
        var message_top = anchor_position.top - message_padding_top
        var message_left = anchor_position.left + (anchor_width / 2) - (message_width / 2)
    }

// inject position values into DOM
    message_dialog.css({top: message_top, left: message_left});
    if (timeout){
        setTimeout(function(){ message_dialog.fadeOut() }, timeout);
    };
    message_dialog.fadeIn();

}

function hideMessage(anchor_selector) {

// retrieve div variable
    var message_dialog_id = '#dialog_status_message_' + anchor_selector.replace('#','').toLowerCase()

// update the DOM
    $(message_dialog_id).hide()

}

function statusSpinnerStart(status_selectors) {

/* a method to initiate a spinner over the status icon */

// construct method variables
    var status_error_id = status_selectors.status_error_id
    var status_success_id = status_selectors.status_success_id
    var status_wait_id = status_selectors.status_wait_id

// define sub-method for rotating wait symbol
    function rotateIcon(icon_id){
        var el = $(icon_id);
        function rotate(degree) {

        // update DOM with new rotation
            deg = degree * 10
            el.css({ WebkitTransform: 'rotate(' + deg + 'deg)'}); /* Webkit */
            el.css({ '-moz-transform': 'rotate(' + deg + 'deg)'}); /* Mozilla */

        // recursive call creates animation
            setTimeout(function() {
                if (el.is(':visible')){ rotate(--degree); };
            }, 20);

        }
        rotate(0);
    }

// update DOM with method variables
    $(status_error_id).hide();
    $(status_success_id).hide();
    $(status_wait_id).show();
    rotateIcon(status_wait_id);

}

function statusSpinnerStop(status_selectors) {

/* a method to stop the spinner over a status icon */

// construct method variables
    var status_success_id = status_selectors.status_success_id
    var status_wait_id = status_selectors.status_wait_id

// update DOM with method variables
    $(status_success_id).show();
    $(status_wait_id).hide();

}

function inputValidator(input_value, field_criteria) {

/* a method to test string input for valid criteria */

// construct method variables
    var must_contain = field_criteria.must_contain;
    var must_not_contain = field_criteria.must_not_contain;

// construct empty values
    var required_error = '';
    var prohibited_error = '';

// test input for required regex
    for (var i = 0; i < must_contain.length; i++){
        var test_pattern = new RegExp(must_contain[i],'i');
        if (!test_pattern.test(input_value)){
            required_error = must_contain[i];
        };
    };

// test input for prohibited regex
    for (var i = 0; i < must_not_contain.length; i++){
        var test_pattern = new RegExp(must_not_contain[i],'i');
        if (test_pattern.test(input_value)){
            prohibited_error = must_not_contain[i];
        };
    };

// return errors found as map
    return {
        required: required_error,
        prohibited: prohibited_error
    };

}

function submitValidator(input_selector, input_value, field_criteria, message_selector, message_location, message_map){

/* a method to validate an input value prior to submission */

// construct variables
    var input_title = field_criteria.field_title

// retrieve error report from error finder method
    var error_report = inputValidator(input_value, field_criteria);

// update DOM to reflect report
    if (error_report.prohibited){
        var error_message = 'Oops! '
        if (!input_title){
            error_message += 'Input '
        } else {
            error_message += input_title + ' '
        };
        error_message += message_map[error_report.prohibited]
        showMessage(message_selector, error_message, 'error', message_location);
        return null;
    }
    else if (error_report.required){
        var error_message = 'Errr! '
        if (!input_value){
            error_message += input_title + ' cannot be empty.'
        } else {
            if (!input_title){
                error_message += 'Input '
            } else {
                error_message += '"' + input_value + '" '
            };
            error_message += message_map[error_report.required]
        };
        showMessage(message_selector, error_message, 'error', message_location);
        return null;
    }
    else {
        return input_value;
    };

}

function formValidator(form_selectors, input_selectors, input_values, model_criteria) {}

function successMessage(response, anchor_selector, message_location) {

/* a method to inject a tooltip message into the DOM from a successful ajax request */

// retrieve variables from response
    try {
        var response_body = JSON.parse(response)
    } catch(e) {
        var response_body = {}
    }

// construct message variables from response body
    var message_status = response_body.status
    var message_content = response_body.message
    var dialog_title = response_body.status
    var dialog_message = '<p>' + response_body.message + '</p>'

// update DOM
    if (typeof(anchor_selector) === 'string'){
        if (typeof(message_location) != 'string') {
            var message_location = ''
        }
        showMessage(anchor_selector, message_content, message_status, message_location, 2000)
    } else {
        $('#dialog_middle_center_header_title').text(dialog_title);
        $('#dialog_middle_center_content_middle').html(dialog_message);
        openDialog('#dialog_middle_center');
    }

}

function errorMessage(response, exception, anchor_selector, message_location) {

/* a method to inject a tooltip message into the DOM from a failed ajax request */

// retrieve variables from response
    var response_code = response.status
    try {
        var response_body = JSON.parse(response.responseText)
    } catch(e) {
        var response_body = {}
    }

// construct html variables from error codes
    var message_content = 'Errr! '
    if (response_code === 0) {
        message_content += 'No connection. Check network settings.'
    } else if (response_code == 404) {
        message_content += 'Page not found. [404]'
    } else if (response_code == 500) {
        message_content += 'Internal Server Error [500].'
    } else if (exception === 'timeout') {
        message_content += 'Request timeout.'
    } else if (exception === 'abort') {
        message_content += 'Request aborted.'
    }

// modify message depending upon response text
    if (typeof(response_body.status) === 'string') {
        var message_status = response_body.status
        var dialog_title = response_body.status
    } else {
        var message_status = 'error'
        var dialog_title = response_code
    }
    if (typeof(response_body.message) === 'string' ){
        var message_content = response_body.message
        var dialog_message = '<p>' + response_body.message + '</p>'
    } else {
        var dialog_message = '<p>' + message_content + '</p>'
    }

// update DOM
    if (typeof(anchor_selector) === 'string'){
        if (typeof(message_location) != 'string') {
            var message_location = ''
        }
        showMessage(anchor_selector, message_content, message_status, message_location)
    } else {
        $('#dialog_middle_center_header_title').text(dialog_title);
        $('#dialog_middle_center_content_middle').html(dialog_message);
        openDialog('#dialog_middle_center');
    }

}

function waitMessage(anchor_selector, base_message, message_status, message_location) {

/* a method to inject a tooltip message into the DOM while waiting for a callback */

// validate optional inputs
    if (typeof(message_status) === 'undefined'){ var message_status = '' }
    if (typeof(message_location) === 'undefined'){ var message_location = 'overlay' }

// retrieve page variables
    var message_dialog_name = 'dialog_status_message_' + anchor_selector.replace('#','').toLowerCase()
    var message_dialog_id = '#' + message_dialog_name;

// update DOM with progress message
    var start_message = new String(base_message)
    var base_length = base_message.length
    for (var i = 0; (i + base_length) < (base_length * 2); i++){
        start_message += '&nbsp;'
    };
    showMessage(anchor_selector, start_message, message_status, message_location)

// recursive progress message until wait completes
    function _update_message(base_message) {

        var base_length = base_message.length
        var updated_message = new String(base_message);
        var message_box = $(message_dialog_id);

        function _increment(count){

            if (!(count % base_length)){
                updated_message = new String(base_message)
            } else {
                updated_message += '.'
            }
            var total_message = new String(updated_message)
            var message_length = updated_message.length
            for (var i = 0; (i + message_length) < (base_length * 2); i++){
                total_message += '&nbsp;'
            };
            message_box.html(total_message)
            setTimeout(function() {
                if (message_box.is(':visible')){ _increment(++count); }
            }, 125);
        }

        _increment(0);

    }

    _update_message(base_message);

}

function jsonRequest(request_url, request_body, request_outcomes, request_headers) {

/* a method to send an ajax request with json structured data by POST method */

// define request data
    if (typeof(request_body) === 'undefined'){
        request_body = { 'test': 'me' }
    };
    var request_data = JSON.stringify(request_body)

// define catchall request headers
    if (typeof(request_headers) != 'object'){
        var request_headers = {}
    };

// add time to headers
    request_headers['X-Timestamp'] = ($.now() / 1000)

// add csrf token to headers
    try {
        var csrf_token = csrfToken // $('meta[name=csrf-token]').attr('content')
    } catch(e) {
        var csrf_token = null
    };
    if (csrf_token){
        request_headers["X-CSRFToken"] = csrf_token
    };

// define catchall request outcome functions
    function _success_function(data) {
        console.log('Request Successful.')
    };
    function _error_function(response) {
        console.log('Request Failed.')
    };
    function _wait_function(){
        console.log('Waiting...')
    };

// define catchall request_outcomes
    if (typeof(request_outcomes) === 'undefined') {
        var request_outcomes = {
            'success': _success_function,
            'error': _error_function,
            'wait': _wait_function
        }
    };
    var _outcome_functions = [ 'success', 'error', 'wait' ]
    for (var i = 0; i < _outcome_functions.length; i++){
        if (!(_outcome_functions[i] in request_outcomes)){
            if (_outcome_functions[i] === 'success'){
                request_outcomes['success'] = _success_function
            } else if (_outcome_functions[i] === 'error'){
                request_outcomes['error'] = _error_function
            } else if (_outcome_functions[i] === 'wait'){
                request_outcomes['wait'] = _wait_function
            };
        };
    };

// construct headers for request

    if (request_headers){
        function header_function(request){
            for (var key in request_headers){
                request.setRequestHeader(key, request_headers[key])
            };
        }
    } else {
        function header_function(request){}
    };

// initialize wait function
    request_outcomes.wait();

// send ajax request
    $.ajax({
        method: 'POST',
        timeout: 12000,
        beforeSend: header_function,
        url: request_url,
        data: request_data,
        contentType: 'application/json',
        success: request_outcomes.success,
        error: request_outcomes.error
    });

}

function inputHandler(input_selector, request_url, request_outcomes, field_key, field_criteria, message_selector, message_location, message_map, saved_value, enter_submit, auto_save) {

/* a method to bind a validation & request handler to an input field */

// construct method variables
    if (typeof(saved_value) === 'undefined'){ var saved_value = '' };
    if (typeof(enter_submit) === 'undefined'){ var enter_submit = true };
    if (typeof(auto_save) === 'undefined'){ var auto_save = false };
    var input_title = field_criteria.field_title

// add typing event handler
    $(input_selector).keyup(function( event ){

    // block normal enter behavior
        var key_code = event.keyCode;
        if (key_code == 13){
            event.preventDefault();
        }

    // retrieve input value
        var input_value = $(this).val();
        if (!input_value && saved_value){
            input_value = saved_value
        }

    // retrieve error report from error finder method
        var error_report = inputValidator(input_value, field_criteria);

    // update DOM to reflect report
        if (error_report.prohibited){
            var error_message = 'Oops! '
            if (!input_title){
                error_message += 'Input '
            } else {
                error_message += input_title + ' '
            };
            error_message += message_map[error_report.prohibited]
            showMessage(message_selector, error_message, 'error', message_location);
        }
        else if (key_code == 13 && enter_submit){

            if (error_report.required){

                var error_message = 'Errr! '
                if (!input_value){
                    error_message += input_title + ' cannot be empty.'
                } else {
                    if (!input_title){
                        error_message += 'Input '
                    } else {
                        error_message += '"' + input_value + '" '
                    };
                    error_message += message_map[error_report.required]
                };
                showMessage(message_selector, error_message, 'error', message_location);

            } else {

                var request_body = {}
                request_body[field_key] = input_value
                jsonRequest(request_url, request_body, request_outcomes);

            }

        }
        else {
            hideMessage(input_selector);
        };

    });

// add focusout event handler
    if (auto_save){

        $(input_selector).focusout(function( event ){

        // retrieve input value
            var input_value = $(this).val();
            if (!input_value && saved_value){
                input_value = saved_value
            }

        // validate input value
            var valid_input = submitValidator(input_selector, input_value, field_criteria, message_selector, message_location, message_map);

        // submit input to endpoint
            if (valid_input === null){} else {

                var request_body = {}
                request_body[field_key] = input_value
                jsonRequest(request_url, request_body, request_outcomes);

            };

        });

    };

}

function statusIconHandler(input_selector, field_criteria, status_selectors) {

/* a method to bind a validation handler to a status icon linked to an input field */

// construct method variables
    var status_error_id = status_selectors.status_error_id
    var status_success_id = status_selectors.status_success_id

// add typing event trigger
    $(input_selector).keyup(function(){

    // retrieve input value and success element tag name
        var input_value = $(this).val();
        var status_success_tag = $(status_success_id)[0].tagName.toLowerCase()

    // retrieve error report from error finder method
        var error_report = inputValidator(input_value, field_criteria);

    // update DOM according to error report
        if (input_value == ''){
            $(status_error_id).hide();
        }
        else if (error_report.required || error_report.prohibited){
            $(status_error_id).show();
        }
        else {
            $(status_error_id).hide();
        };

    });

}

function statusButtonHandler(input_selector, request_url, request_outcomes, field_key, field_criteria, status_selectors, message_selector, message_location, message_map, saved_value) {

/* a method to bind a validation & request handler to a button linked to an input field */

// construct method variables
    if (typeof(saved_value) === 'undefined'){ var saved_value = '' };
    var input_title = field_criteria.field_title
    var status_error_id = status_selectors.status_error_id
    var status_success_id = status_selectors.status_success_id

// construct submit handling sub-method
    function submitHandling(input_selector, status_success_id, field_key, field_criteria, message_selector, message_location, message_map, saved_value){

        $(status_success_id).click(function(){

        // retrieve input value
            var input_value = $(input_selector).val();
            if (!input_value) {
                input_value = saved_value;
            };

        // validate input value
            var valid_input = submitValidator(input_selector, input_value, field_criteria, message_selector, message_location, message_map);

        // submit input to endpoint
            if (valid_input === null){} else {

                var request_body = {}
                request_body[field_key] = input_value
                jsonRequest(request_url, request_body, request_outcomes);

            };

        });

    }

// add typing event trigger
    $(input_selector).keyup(function(){

    // retrieve input value and success element tag name
        var input_value = $(this).val();
        var status_success_tag = $(status_success_id)[0].tagName.toLowerCase()

    // retrieve error report from error finder method
        var error_report = inputValidator(input_value, field_criteria);

    // update DOM according to error report
        if (input_value == ''){

        // remove blocking icon
            $(status_error_id).hide();

        // convert span into button
            if (status_success_tag == 'span') {

                convertElement(status_success_id, 'a')

            // add back submit handling
                submitHandling(input_selector, status_success_id, field_key, field_criteria, message_selector, message_location, message_map, saved_value);

            };

        }
        else if (error_report.required || error_report.prohibited){

        // add blocking icon
            $(status_error_id).show();

        // convert button into span
            if (status_success_tag == 'a') {
                convertElement(status_success_id, 'span')
            };
        }
        else {

        // remove blocking icon
            $(status_error_id).hide();

        // convert span into button
            if (status_success_tag == 'span') {

                convertElement(status_success_id, 'a')

            // add back submit handling
                submitHandling(input_selector, status_success_id, field_key, field_criteria, message_selector, message_location, message_map, saved_value);

            };

        };

    });

// add submit handling for starting value
    submitHandling(input_selector, status_success_id, field_key, field_criteria, message_selector, message_location, message_map, saved_value);

}

function formHandler(form_selectors, input_selectors, input_values, model_keys, model_criteria, status_selectors, message_selectors, message_locations, message_map, saved_values) {

/* a method to bind a validation & request handler to set of inputs in a form field */

}








