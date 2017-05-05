/* LAB LANDING EXTENSION MIT License 2017 rcj1492 */
/* Functions for Landing */
/* Requires jquery */

function missionDialog() {

/* a method to display the lab mission in a dialog panel */

// construct input schema
    var dialog_dict = {
        'dialog_title': 'Mission',
        'dialog_content': '<blockquote class="blockquote-reverse"><p>To make accessible to each individual the resources of the world</p><footer>Collective Acuity</footer></blockquote>'
    }

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
        <div id="dialog_middle_center" class="page-middle-center dialog-box hidden-xs">\
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
        <div id="dialog_full_page" class="page-container-100 dialog-page hidden-lg hidden-md hidden-sm">\
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

$(function(){
    if (($('#oauth2_confirmation_close').length )) {
        var count = 8
        var close_timer = window.setInterval(function() {
            if (count > 0) {
                var closing_text = 'Closing in ' + count + '...'
                $('#oauth2_confirmation_close').text(closing_text)
                count -= 1
            } else {
                window.clearInterval(close_timer)
                window.close()
            }
        }, 1000)
    }
});
