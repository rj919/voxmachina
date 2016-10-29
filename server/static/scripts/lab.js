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

function toggleStyle(jquery_element, style_property) {

/* a helper method for changing a specific style in a DOM element */

// construct style regex pattern from style property
    var _style_regex = new RegExp(style_property, 'i')

// style already exists, add the style
    if (typeof(jquery_element.attr("style")) === "undefined") {
        jquery_element.attr("style", style_property)
    } else if (!_style_regex.test(jquery_element.attr("style"))) {
        var _new_style = jquery_element.attr("style") + " " + style_property
        jquery_element.attr("style", _new_style);
// otherwise, remove the style
    } else {
        var _new_style = jquery_element.attr("style").replace(style_property, "")
        if (_new_style) {
            jquery_element.attr("style", _new_style)
        } else {
            jquery_element.removeAttr("style")
        };
    };

}

function unpackKwargs(kwargs_input, kwargs_model, method_name) {

/* a helper method for unpacking and validating keyword arguments */

    for (var key in kwargs_model) {
        var console_message = 'error unpacking ' + method_name + ': '
        try {
            if (key in kwargs_input) {
                if (typeof(kwargs_input[key]) === typeof(kwargs_model[key])) {
                    if (kwargs_model[key] && !kwargs_input[key]) {
                        if (typeof(kwargs_input[key]) != 'boolean') {
                            console_message += key + ' cannot be empty.'
                            console.log(console_message)
                        }
                    } else {
                        kwargs_model[key] = kwargs_input[key]
                    };
                } else {
                    console_message += key + ' must be a ' + typeof(kwargs_model[key]) + '.'
                    console.log(console_message)
                };
            };
        } catch(e) {
            console_message += key + ' failed to unpack.'
            console.log(console_message);
        };

    };

}

function logConsole(console_kwargs) {

// declare input schema
    input_schema = {
        'schema': {
            'message': "I am a lollipop."
        },
        'metadata': {
            'example_statements': [ 'display the response message in the console' ]
        }
    }

// unpack kwargs input
    console_dict = input_schema.schema
    unpackKwargs(console_kwargs, console_dict, 'logConsole')

// log message
    console.log(console_dict.message)

}

function responsiveDialog(dialog_kwargs) {

// unpack kwargs input
    dialog_dict = {
        'dialog_title': 'Mission',
        'dialog_content': '<blockquote class="blockquote-reverse"><p>To make accessible to each individual the resources of the world</p><footer>Collective Acuity</footer></blockquote>'
    }
    unpackKwargs(dialog_kwargs, dialog_dict, 'responsiveDialog')

// construct method variables
    var backdrop_dialog_id = '#dialog_backdrop'
    var desktop_dialog_id = '#dialog_middle_center'
    var desktop_dialog_title_id = '#dialog_middle_center_header_title'
    var desktop_dialog_content_id = '#dialog_middle_center_content_container'
    var desktop_dialog_links = '#dialog_middle_center [href="javascript:void(0)"]'
    var mobile_dialog_id = '#dialog_full_page'
    var mobile_dialog_title_id = '#dialog_full_page_header_title'
    var mobile_dialog_content_id = '#dialog_full_page_content_container'
    var mobile_dialog_links = '#dialog_full_page [href="javascript:void(0)"]'

// construct desktop dialog html content
    var desktop_dialog_html = '\
        <div id="dialog_middle_center" class="dialog-box page-middle-center hidden-xs">\
            <div id="dialog_middle_center_header_container" class="container-fluid">\
                <div id="dialog_middle_center_header_row" class="row navbar">\
                    <div id="dialog_middle_center_header_left" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">\
                    </div>\
                    <div id="dialog_middle_center_header_middle" class="col-lg-8 col-md-8 col-sm-8 col-xs-8">\
                        <div id="dialog_middle_center_header_title" class="navbar-title-24 navbar-center"></div>\
                    </div>\
                    <div id="dialog_middle_center_header_right" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">\
                        <div id="dialog_middle_center_header_close" class="navbar-title-24 navbar-end">\
                            <a href="javascript:void(0)" id="dialog_middle_center_header_close_button" title="Close Button" class="icon-close font-sm float-middle"></a>\
                        </div>\
                    </div>\
                </div>\
            </div>\
            <div id="dialog_middle_center_content_container" class="container-fluid">\
            </div>\
        </div>'

// construct mobile dialog html content
    var mobile_dialog_html = '\
        <div id="dialog_full_page" class="dialog-box page-overlay-100 dialog-full-page hidden-lg hidden-md hidden-sm">\
            <div id="dialog_full_page_header_container" class="container-fluid">\
                <div id="dialog_full_page_header_row" class="row navbar">\
                    <div id="dialog_full_page_header_left" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">\
                    </div>\
                    <div id="dialog_full_page_header_middle" class="col-lg-8 col-md-8 col-sm-8 col-xs-8">\
                        <div id="dialog_full_page_header_title" class="navbar-title-24 navbar-center"></div>\
                    </div>\
                    <div id="dialog_full_page_header_right" class="col-lg-2 col-md-2 col-sm-2 col-xs-2">\
                        <div id="dialog_full_page_header_close" class="navbar-title-24 navbar-end">\
                            <a href="javascript:void(0)" id="dialog_full_page_header_close_button" title="Close Button" class="icon-close font-sm float-middle"></a>\
                        </div>\
                    </div>\
                </div>\
            </div>\
            <div id="dialog_full_page_content_container" class="container-fluid">\
            </div>\
        </div>'

// remove any previous dialogs with same name
    if ($(desktop_dialog_id).length){
        $(desktop_dialog_id).remove();
    };
    if ($(mobile_dialog_id).length){
        $(mobile_dialog_id).remove();
    };

// inject DOM with html content
    $(backdrop_dialog_id).show();
    $('body').append(desktop_dialog_html);
    $('body').append(mobile_dialog_html);
    $(desktop_dialog_title_id).text(dialog_dict['dialog_title']);
    $(mobile_dialog_title_id).text(dialog_dict['dialog_title']);
    $(desktop_dialog_content_id).html(dialog_dict['dialog_content']);
    $(mobile_dialog_content_id).html(dialog_dict['dialog_content']);

//// construct method variables
//    var dialog_id_mobile = dialog_dict['dialog_id_mobile']
//    var dialog_id_desktop = dialog_dict['dialog_id_desktop']
//
//// construct selector for dialog javascript link children
//    var dialog_id_backdrop = '#dialog_backdrop';
//    var dialog_links_mobile = dialog_id_mobile + ' [href="javascript:void(0)"]';
//    var dialog_links_desktop = dialog_id_desktop + ' [href="javascript:void(0)"]';
//
//// open up dialog and dialog backdrop
//    $(dialog_id_mobile).show();
//    $(dialog_id_mobile).addClass("hidden-lg hidden-md hidden-sm");
//    $(dialog_id_desktop).show();
//    $(dialog_id_desktop).addClass("hidden-xs");
//    $(dialog_id_backdrop).show();

// bind event handlers to close dialogs
    $(mobile_dialog_links).click(function(){
        $(backdrop_dialog_id).hide();
        $(mobile_dialog_id).remove();
        $(desktop_dialog_id).remove();
    });
    $(desktop_dialog_links).click(function(){
        $(backdrop_dialog_id).hide();
        $(mobile_dialog_id).remove();
        $(desktop_dialog_id).remove();
    });
    $(backdrop_dialog_id).click(function(){
        $(backdrop_dialog_id).hide();
        $(mobile_dialog_id).remove();
        $(desktop_dialog_id).remove();
    });
}

function successConstructor(response) {

/* a method for handling a successful ajax response */

    methodConstructor(response);

}

function errorConstructor(response, exception) {

/* a method for handling an error in an ajax response */

// retrieve variables from response
    var response_code = response.status
    try {
        var response_body = JSON.parse(response.responseText)
    } catch(e) {
        var response_body = {}
    }

// construct message from error codes
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

// report error to console log
    console.log(message_content);

}

function methodConstructor(response_kwargs) {

/* a method for parsing function calls from a response body */

// unpack variables in response
    var response_dict = {
        'dt': 0,
        'id': '',
        'code': 0,
        'methods': []
    }
    unpackKwargs(response_kwargs, response_dict, 'methodConstructor')

// call each method inside details
    if (response_dict['methods']) {
        var console_message = 'error constructing method '
        for (var i = 0; i < response_dict['methods'].length; i++) {
            try {
                var _func_name = response_dict['methods'][i]['function']
                var _global_func = window[_func_name]
                if ('kwargs' in response_dict['methods'][i]) {
                    var _func_args = response_dict['methods'][i]['kwargs'];
                    if (typeof(_func_args) === 'object') {
                        _global_func(_func_args);
                    } else {
                        _global_func();
                    };
                } else {
                    _global_func();
                };
            } catch(e) {
                console_message += response_dict['methods'][i]
                console.log(console_message);
            };
        }
    }

}

function stringRequest(request_string) {

/* a method to request information from server */

// add request string to context history
    context_kwargs = {
        'element_selector': 'meta[name=lab-context]',
        'context_array': [ request_string ],
        'array_upsert': true
    }
    updateContext(context_kwargs);

// construct request_kwargs
    context_data = $('meta[name=lab-context]').data()
    request_dict = {
        'request_url': '/web',
        'request_body': {
            'details': { 'string': request_string },
            'context': {
                'context_properties': context_data.context_map,
                'context_history': context_data.context_array
            }
        }
    }

// define outcome functions
    request_dict['request_success'] = successConstructor
    request_dict['request_error'] = errorConstructor

// call json request method
    jsonRequest(request_dict);

}

function jsonRequest(request_kwargs) {

/* a method to send an ajax request with json structured data by POST method */

// define catchall request outcome functions
    function _success_function(response) {
        console.log('Request Successful.')
    };
    function _error_function(response, exception) {
        console.log('Request Failed.')
    };
    function _wait_function(){
        console.log('Waiting...')
    };

// unpack request keywords
    request_dict = {
        'request_url': '/web',
        'request_body': { 'file': 'lab-mission.json' },
        'request_success': _success_function,
        'request_error': _error_function,
        'request_wait': _wait_function,
        'request_headers': {}
    }
    unpackKwargs(request_kwargs, request_dict, 'jsonRequest');

// construct method variables
    var request_data = JSON.stringify(request_dict['request_body'])

// add time to headers
    request_dict['request_headers']['X-Timestamp'] = ($.now() / 1000)

// add csrf token to headers
    try {
        var csrf_token = $('meta[name=csrf-token]').attr('content')
    } catch(e) {
        var csrf_token = null
    };
    if (csrf_token){
        request_dict['request_headers']["X-CSRFToken"] = csrf_token
    };

// construct ajax request map
    var ajax_map = {
        method: 'POST',
        timeout: 12000,
        headers: {},
        url: request_dict['request_url'],
        data: request_data,
        contentType: 'application/json',
        success: request_dict['request_success'],
        error: request_dict['request_error']
    }

// add headers to map
    for (var key in request_dict['request_headers']){
        ajax_map['headers'][key] = request_dict['request_headers'][key]
    };

// send ajax request
    $.ajax(ajax_map);

// initialize wait function
    request_dict['request_wait']();

}

function updateContext(context_kwargs) {

/* a method to inject array data into a DOM element */

// declare input schema
    input_schema = {
        'schema': {
            'element_selector': 'meta[name=lab-context]',
            'context_array': [ 'strings' ],
            'context_map': {},
            'array_upsert': true,
            'map_upsert': true
        },
        'components': {
            '.context_map': {
                'extra_fields': true
            }
        },
        'metadata': {
            'example_statements': [ 'inject array data into a DOM element' ]
        }
    }

// unpack context keywords
    context_dict = input_schema.schema
    unpackKwargs(context_kwargs, context_dict, 'updateContext')

// retrieve context data from jquery selector
    element_selector = $(context_dict.element_selector)
    context_data = element_selector.data()
    if (!Object.keys(context_data).length){
        context_data = {
            'context_array': [],
            'context_map': {}
        }
    }

// update context array data
    if (context_dict.context_array.length) {
        if (context_dict.array_upsert) {
            for (var i = 0; i < context_dict.context_array.length; i++) {
                if (context_data.context_array.length > 48) {
                    context_data.context_array.splice(0,1)
                }
                context_data.context_array.push(context_dict.context_array[i])
            }
        } else {
            context_data.context_array = context_dict.context_array
        }
    }

// update context map data
    if (Object.keys(context_dict.context_map).length) {
        if (context_dict.map_upsert) {
            for (var key in context_dict.context_map) {
                context_data.context_map[key] = context_dict.context_map[key]
            }
        } else {
            context_data.context_map = context_dict.context_map
        }
    }

// inject new data into DOM
    element_selector.data(context_data)

}

function dummy() {}