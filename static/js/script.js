window.onload = function(){
    $('.ui.dropdown').dropdown();
    // var ratio = window.outerWidth / window.innerWidth;
    
    // $('html').css({
    //     'width':(ratio) * ($(window).width()),
    //     'height':(ratio) * ($(window).height())
    // });
};

(function($){
    $.fn.extend({     
        'getFormData': function() {
            var data = $(this).serializeArray();
            return toObject(data);
        },        
    }); 
})(jQuery);

function toObject(data){
    var json = {};
    $.each(data, function() {
        if (this.name in json){
            json[this.name] = [json[this.name]]
            json[this.name].push(this.value)
        }
        else{
            json[this.name] = this.value;
        }
    });
    return json;
};

function setUrlParameter(key, value){
    var url_string = window.location.href;
    var url = new URL(url_string);
    url.searchParams.set(key, value);
    window.location.href = url.href;
};

function pagenate(page){
    setUrlParameter('page', page);
}

function deleteUrlParameter(key){
    var url_string = window.location.href;
    var url = new URL(url_string);
    url.searchParams.delete(key);
    window.location.href = url.href;
};

$('.nav-link').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
    window.scrollTo(0, 0);
});

$('.modal').on('hidden.bs.modal', function () {
    $(this).find("input,textarea,select").val('').end();
});

$('#search-filter').on('keyup', function(e){
    var search_text = $(this).val() || null;
    $("[name=item]").show();
    $("[name=item]").not("[search-key*="+search_text+"]").hide();

    if(search_text == null){
        $("[name=item]").show();        
    }
});

$('button[id^="custom-file-button-"]').click(function(){
    var target_handler_id = '#' + $(this).attr('id').replace('custom-file-button', 'custom-file-handler');        
    $(target_handler_id).click();
});

$('input[id^="custom-file-handler-"]').change(function(){
    var target_button_id = '#' + $(this).attr('id').replace('custom-file-handler', 'custom-file-button');
    var filename = this.value.replace(/^.*[\\\/]/, '');
    if(filename.length > 0){
        $(target_button_id).text(filename);
    }
});


function showModal(modalId){
	$(modalId).modal({
		duration:100,
		transition:'fade'
	}).modal('show');
}

$(document).ready(function(){

	$('.menu .item').tab();
    $('.ui .dropdown').dropdown();

    $('#menu').click(function(){
        $('.ui.sidebar').sidebar('toggle');
    });

    $(".close.icon").click(function(){
        $(this).parent().hide();
    });


	$("#create-testsuite-button").click(function(){
		showModal('#create-testsuite-modal');
    });

    $("#create-group-button").click(function(){
		showModal('#create-group-modal');
    });

    $("#create-assignment-button").click(function(){
		showModal('#create-assignment-modal');
    });

    $("#edit-assignment-button").click(function(){
		showModal('#edit-assignment-modal');
    });
    
    $("#create-announcement-button").click(function(){
		showModal('#create-announcement-modal');
    });

    $("#add-members-button").click(function(){
		showModal('#add-members-modal');
    });

    $("#submit-code-button").click(function(){
		showModal('#submit-code-modal');
    });

    $("#delete-group-button").click(function(){
		showModal('#delete-group-modal');
    });

    $("#delete-assignment-button").click(function(){
		showModal('#delete-assignment-modal');
    });

    $("#delete-testsuite-button").click(function(){
		showModal('#delete-testsuite-modal');
    });

    $("#add-testcase-button").click(function(){
		showModal('#add-testcase-modal');
    });

});