/* LAB CONTENT EXTENSION */
/* Requires main lab.js scripts */

/* Constructors for lab dynamic page, dialog and view elements */

function protocolsDialog() {

/* a method to display lab protocols information */

// define arguments
    var request_url = '/info'
    var request_body = { 'file': 'lab-protocols.json' }

/*
// add client info to request headers
    var request_headers = {}
    if (Modernizr.ambientlight) {
        // supported
        request_headers['X-AmbientLight'] = true
    } else {
        // not-supported
        request_headers['X-AmbientLight'] = false
    }
*/

// define success function
    function _protocol_success(data) {

     // construct html content from response
        var header_title = data.details.title;
        var div_id = header_title.toLowerCase().replace(' ', '_');
        var div_title = data.details.description;
        var div_class = 'font-mini small text-left';
        var content_html = '<div id="' + div_id + '_details" class="' + div_class + '" title="' + div_title + '">';
        var lab_policies = data.details.policies;
        for (var i = 0; i < lab_policies.length; i++) {
            content_html += '<strong>' + lab_policies[i].policy_title + '</strong>';
            content_html += '<ul class="list-padding">';
            var policy_terms = lab_policies[i].policy_terms;
            for (var j = 0; j < policy_terms.length; j++) {
                content_html += '<li>' + policy_terms[j] + '</li>';
            };
            content_html += '</ul>';
        }
        content_html += '</div>';

    // inject DOM with html content
        $('#dialog_full_page_header_title').text(header_title);
        $('#dialog_full_page_content_middle').html(content_html);
        $('#dialog_middle_center_header_title').text(header_title);
        $('#dialog_middle_center_content_middle').html(content_html);
    }

// define error function
    function _protocol_error(response, exception) {
        errorMessage(response, exception);
    }

// construct request outcomes variable
    request_outcomes = {
        'success': _protocol_success,
        'error': _protocol_error
    }

// open dialog window
    var dialog_id_mobile = '#dialog_full_page'
    var dialog_id_desktop = '#dialog_middle_center'
    responsiveDialog(dialog_id_mobile, dialog_id_desktop);

// call json request method
    jsonRequest(request_url, request_body, request_outcomes);

}

function missionDialog() {

    /* a method to display lab protocols information */

// define arguments
    var request_url = '/info'
    var request_body = { 'file': 'lab-mission.json' }

// define success function
    function _mission_success(data) {

     // construct html content from response
        var header_title = data.details.title;
        var div_id = header_title.toLowerCase().replace(' ', '_');
        var div_title = data.details.description;
        var div_class = 'font-sm text-left';
        var content_html = '<div id="' + div_id + '_details" class="' + div_class + '" title="' + div_title + '">';
        var lab_mission = data.details.details;
        content_html += '<blockquote class="blockquote-reverse"><p>' + lab_mission + '</p><footer>Collective Acuity</footer></blockquote>'
        content_html += '</div>';

    // inject DOM with html content
        $('#dialog_full_page_header_title').text(header_title);
        $('#dialog_full_page_content_middle').html(content_html);
        $('#dialog_middle_center_header_title').text(header_title);
        $('#dialog_middle_center_content_middle').html(content_html);
    }

// define error function
    function _mission_error(response, exception) {
        errorMessage(response, exception);
    }

// construct request outcomes variable
    request_outcomes = {
        'success': _mission_success,
        'error': _mission_error
    }

// open dialog window
    var dialog_id_mobile = '#dialog_full_page'
    var dialog_id_desktop = '#dialog_middle_center'
    responsiveDialog(dialog_id_mobile, dialog_id_desktop);

// call json request method
    jsonRequest(request_url, request_body, request_outcomes);

}

function contentMiddle() {

/* a helper method for constructing a full page middle center display*/

// construct content html
    var middle_html = '\
        <div id="content_container" class="container content-container-fill">\
            <div id="content_row" class="row height-100">\
                <div id="content_left" class="col-lg-4 col-md-4 col-sm-3 col-xs-2"></div>\
                <div id="content_middle" class="col-lg-4 col-md-4 col-sm-6 col-xs-8 height-100">\
                    <div id="content_middle_row" class="row vertical-center-40">\
                        <div id="content_middle_column" class="col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>\
                    </div>\
                </div>\
                <div id="content_right" class="col-lg-4 col-md-4 col-sm-3 col-xs-2"></div>\
            </div>\
        </div>'

// update DOM with content html
    $('#content').html(middle_html)

}

function startPage() {

/* a method to display lab sign-in content */

// construct middle center content
    contentMiddle();
    document.title = 'Collective Acuity : Welcome to the Laboratory'

// construct start content
    content_html = '\
        <div id="welcome_icon" class="font-mega text-center padding-vertical-20">\
            <span id="chemistry_icon" class="icon-chemistry float-middle"></span>\
        </div>'

// update DOM with content html
    $('#content_middle_column').html(content_html)

}

function signinPage() {

/* a method to display lab sign-in content */

// construct middle center content
    contentMiddle();
    document.title = 'Collective Acuity : Welcome to the Laboratory'

// construct signin content
    content_html = '\
        <div id="welcome_icon" class="font-xl text-center padding-vertical-20">\
            <span id="chemistry_icon" class="icon-chemistry float-middle"></span>\
        </div>\
        <div id="signin_form" title="Sign-In" class="form-line text-center">\
            <label id="signin_label" for="signin_input" class="form-label">\
                Signin/Signup with Email:\
            </label>\
            <div class="form-control-inline">\
                <input id="signin_input" type="text" autofocus class="form-control form-control-fill">\
                <div id="signin_status" class="form-control form-control-auto">\
                    <div id="signin_status_wait" class="icon-xs" style="display: none;">\
                        <span class="icon-refresh font-success icon-xs"></span>\
                    </div>\
                    <span id="signin_status_error" class="icon-ban icon-overlay font-error" style="display: none;"></span>\
                    <a id="signin_status_success" href="javascript:void(0)" class="icon-arrow-right font-success"></a>\
                </div>\
            </div>\
            <div id="signin_lab_protocols" class="padding-vertical-0">\
                <span id="signin_lab_protocols_text" class="font-micro text-uppercase">Please review the <a id="signin_lab_protocols_text_link" href="javascript:void(0)" onclick="protocolsDialog()">Lab Protocols</a></span>\
            </div>\
        </div>'

// update DOM with content html
    $('#content_middle_column').html(content_html)

// define actions for request success
    function signinSuccess(data){

    // hide anonymous elements & show authenticated elements
        $('#footer_container').hide();
        $('#header_left_title').hide();
        $('#header_left_button').show();
        $('#header_middle_wide').show();

    // remove signin page elements
        statusSpinnerStop(status_selectors);
        $('#content_container').remove()
        console.log('Signin successful.')

    }

// define actions for request failure
    function signinError(response, exception){
        statusSpinnerStop(status_selectors);
        errorMessage(response, exception, input_selector, message_location);
        console.log('Signin failed.')
    }

// define actions for request waiting
    function signinWait(){
        var wait_message = 'Signin in progress'
        console.log(wait_message + '...')
        statusSpinnerStart(status_selectors);
        // waitMessage(input_selector, wait_message, '', message_location)
    }

// define dynamic content variables
    var input_selector = '#signin_input'
    var status_selectors = {
        status_error_id: '#signin_status_error',
        status_success_id: '#signin_status_success',
        status_wait_id: '#signin_status_wait'
    }
    var request_url = '/signin'
    var request_outcomes = {
        'success': signinSuccess,
        'error': signinError,
        'wait': signinWait,
        // 'stop': stopWait
    }
    var field_key = 'user_email'
    var field_criteria = {
        // for internationalization validation: https://github.com/bestiejs/punycode.js
        must_contain: [ '^[\\w\\-_\\.\\+]{1,24}?@[\\w\\-\\.]{1,24}?\\.[a-z]{2,10}$' ],
        must_not_contain: [ '^\\.', '\\.\\.', '\\.@', '@\\.', '[\\"\\s<>(),]' ],
        example_values: [ 'satoshi@bitcoin.org' ],
        field_title: 'Email'
    }
    var input_saved = 'satoshi@bitcoin.org'
    var message_location = 'bottom'

// add handlers for dynamic content
    injectPlaceholder(input_selector, field_criteria.example_values[0]);
    inputHandler(input_selector, request_url, request_outcomes, field_key, field_criteria, input_selector, message_location, messageMap);
    statusButtonHandler(input_selector, request_url, request_outcomes, field_key, field_criteria, status_selectors, input_selector, message_location, messageMap);

}

function signoutTrigger() {

/* a method to sign out user */

// construct method fields
    var request_url = '/signout'
    var request_body = { 'test': 'me' }

// define success function
    function signoutSuccess(data) {

    // hide anonymous elements & show authenticated elements
        $('#footer_container').show();
        $('#header_left_title').show();
        $('#header_left_button').hide();
        $('#header_middle_wide').hide();

    // restore signin page
        signinPage();

    // log confirmation
        console.log('Signout successful.')

    }

// define wait function
    function signoutWait() {
        console.log('Signout in progress...')
    }

// define request outcomes
    var request_outcomes = {
        'success': signoutSuccess,
        'wait': signoutWait
    }

// submit input through ajax request
    jsonRequest(request_url, request_body, request_outcomes)

}

function subscribePage() {

/* a method to display lab subscription signup content */

// construct middle center content
    contentMiddle();
    document.title = 'Collective Acuity : Subscribe to Newsletter'

// construct subscription content
    content_html = '\
        <div id="welcome_icon" class="font-xl text-center padding-vertical-20">\
            <span id="chemistry_icon" class="icon-chemistry float-middle"></span>\
        </div>\
        <div id="subscribe_form" title="Subscribe" class="form-line text-center">\
            <label id="subscribe_label" for="subscribe_input" class="form-label">\
                Subscribe to the newsletter:\
            </label>\
            <div class="form-control-inline">\
                <input id="subscribe_input" type="text" autofocus class="form-control form-control-fill">\
                <div id="subscribe_status" class="form-control form-control-auto">\
                    <div id="subscribe_status_wait" class="icon-xs" style="display: none;">\
                        <span class="icon-refresh font-success icon-xs"></span>\
                    </div>\
                    <span id="subscribe_status_error" class="icon-ban icon-overlay font-error" style="display: none;"></span>\
                    <a id="subscribe_status_success" href="javascript:void(0)" class="icon-arrow-right font-success"></a>\
                </div>\
            </div>\
        </div>'

// update DOM with content html
    $('#content_middle_column').html(content_html)

// define dynamic content variables
    var input_selector = '#subscribe_input'
    var status_selectors = {
        status_error_id: '#subscribe_status_error',
        status_success_id: '#subscribe_status_success',
        status_wait_id: '#subscribe_status_wait'
    }
    var request_url = '/subscribe'
    var field_key = 'user_email'
    var field_criteria = {
        // for internationalization validation: https://github.com/bestiejs/punycode.js
        must_contain: [ '^[\\w\\-_\\.\\+]{1,24}?@[\\w\\-\\.]{1,24}?\\.[a-z]{2,10}$' ],
        must_not_contain: [ '^\\.', '\\.\\.', '\\.@', '@\\.', '[\\"\\s<>(),]' ],
        example_values: [ 'satoshi@bitcoin.org' ],
        field_title: 'Email'
    }
    var input_saved = 'satoshi@bitcoin.org'

// add handlers for dynamic content
    injectPlaceholder(input_selector, input_saved);
    inputHandler(input_selector, request_url, field_key, field_criteria, input_selector, 'bottom', messageMap);
    statusButtonHandler(input_selector, request_url, field_key, field_criteria, status_selectors, input_selector, 'bottom', messageMap);

}

(function(){

    /* if (!$.trim($('#content').html()) && $('#footer_container').is(':visible')){
        signinPage();
    } */
    if (!$.trim($('#content').html())) {
        startPage();
    }

})();

