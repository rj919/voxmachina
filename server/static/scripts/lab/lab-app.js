/* LAB CONTENT EXTENSION */
/* Requires main lab.js scripts */

/* Constructors for lab dynamic page, dialog and view elements */

function toggleVerified() {

/* a method to toggle the view between id_verified states */

// declare input schema
    input_schema = {
        'schema': {
            'test': ''
        }
    }

// toggle hidden/visible elements
    var visible_ids = $('.id-verified-visible')
    var style_property = 'display: none;'
    visible_ids.each(function(){
        toggleStyle($(this), style_property);
    });

// toggle dashboard header border
    var border_ids = $('.id-verified-border')
    border_ids.each(function(){
        $(this).toggleClass('navbar-border');
    });

}

function itemizedDialog(itemized_kwargs) {

/* a method to display lab protocols information */

// declare input schema
    input_schema = {
        'schema': {
            'title': 'Lab Protocols',
            'description': 'How flask bot uses data.',
            'effective_date': '2016.05.30.13.45.55',
            'sections': [ {
                'section_title': 'Zero Tracking',
                'section_description': '',
                'section_items': [ 'We do not place any weird cookies, use any trackers or allow third parties services to collect data about you from us.' ]
            } ]
        },
        'metadata': {
            'example_statements': [ 'display lab protocols information' ]
        }
    }

// unpack kwargs input
    itemized_dict = input_schema.schema
    unpackKwargs(itemized_kwargs, itemized_dict, 'itemizedDialog')

 // construct html content from response
    var title_text = itemized_dict.title
    var div_id = title_text.toLowerCase().replace(' ', '_');
    var div_title = itemized_dict.description;
    var div_class = 'font-mini small text-left';
    var content_html = '<div id="' + div_id + '_details" class="' + div_class + '" title="' + div_title + '">';
    var sections_list = itemized_dict.sections;
    for (var i = 0; i < sections_list.length; i++) {
        content_html += '<strong>' + sections_list[i].section_title + '</strong>';
        content_html += '<ul class="list-padding">';
        var section_items = sections_list[i].section_items;
        for (var j = 0; j < section_items.length; j++) {
            content_html += '<li>' + section_items[j] + '</li>';
        };
        content_html += '</ul>';
    }
    content_html += '</div>';

// open dialog window
    var dialog_kwargs = {
        'dialog_title': title_text,
        'dialog_content': content_html
    }
    responsiveDialog(dialog_kwargs);
}

function blockquoteDialog(blockquote_kwargs) {

/* a method to display lab mission information */

// declare input schema
    input_schema = {
        'schema': {
            'title': 'Mission',
            'description': 'Statement of purpose for the laboratory.',
            'effective_date': '2016.05.31.13.45.55',
            'details': 'To make accessible to each individual the resources of the world.',
            'author': 'Collective Acuity'
        },
        'metadata': {
            'example_statements': [ 'display a blockquote in the responsive dialog' ]
        }
    }

// unpack kwargs input
    blockquote_dict = input_schema.schema
    unpackKwargs(blockquote_kwargs, blockquote_dict, 'blockquoteDialog')

// construct html content from response
    var title_text = blockquote_dict.title;
    var div_id = title_text.toLowerCase().replace(' ', '_');
    var div_title = blockquote_dict.description;
    var div_class = 'font-sm text-left';
    var content_html = '<div id="' + div_id + '_details" class="' + div_class + '" title="' + div_title + '">';
    var content_text = blockquote_dict.details;
    var author_text = blockquote_dict.author;
    content_html += '<blockquote class="blockquote-reverse"><p>' + content_text + '</p><footer>' + author_text + '</footer></blockquote>'
    content_html += '</div>';

// open dialog window
    var dialog_kwargs = {
        'dialog_title': title_text,
        'dialog_content': content_html
    }
    responsiveDialog(dialog_kwargs);
}

function contentMiddle() {

/* a helper method for constructing a full page middle center display*/

// construct content html
    var middle_html = '\
        <div id="content_container" class="container content-container-fill">\
            <div id="content_row" class="row height-100">\
                <div id="content_left" class="col-lg-4 col-md-4 col-sm-3 hidden-xs"></div>\
                <div id="content_middle" class="col-lg-4 col-md-4 col-sm-6 col-xs-12 height-100">\
                    <div id="content_middle_row" class="row vertical-center-40">\
                        <div id="content_middle_column" class="col-lg-12 col-md-12 col-sm-12 col-xs-12"></div>\
                    </div>\
                </div>\
                <div id="content_right" class="col-lg-4 col-md-4 col-sm-3 hidden-xs"></div>\
            </div>\
        </div>'

// update DOM with content html
    $('#content').html(middle_html)

}

function landingView() {

/* a method to display the lab startup content */

// TODO: add recaptcha into beaker click
// https://github.com/lepture/flask-wtf/tree/master/flask_wtf/recaptcha

// construct middle center content
    contentMiddle();
    document.title = 'Collective Acuity : Welcome to the Laboratory'

// construct start content
    content_html = '\
        <div id="start_box" class="font-mega text-center line-height-1 padding-vertical-20">\
            <a href="javascript:void(0)" id="chemistry_icon" class="icon-chemistry icon-glow" onclick="testMethod()" title="Click to Get Started"></a>\
        </div>'

// update DOM with content html
    $('#content_middle_column').html(content_html)

// update DOM with context details
    context_kwargs = {
        'element_selector': 'meta[name=lab-context]',
        'context_map': { 'current_view': 'landing' },
        'map_upsert': false
    }
    updateContext(context_kwargs)

}

function entryView() {

/* a method to display lab sign-in content */

// construct middle center content
    document.title = 'Collective Acuity : Sign-In to the Laboratory'

// construct signin content
    content_html = '\
        <div id="message_exchange" title="Sign-In" class="form-line text-left">\
            <label id="input_prompt" for="input_field" class="form-text"></label>\
            <input id="input_field" type="text" autofocus class="form-text form-control">\
        </div>'

// update DOM with content html
    var exchange_id = $('#content_middle_column')
    setTimeout(function(){
        exchange_id.html(content_html);
        $('#input_prompt').text('What is your Email?')
        exchange_id.fadeIn();
    }, 600);
    exchange_id.fadeOut(600);



}

function testMethod() {

    stringRequest('run toggleVerified');

}

(function(){

    if (!$.trim($('#content').html())) {
        landingView();
    }

})();
