$(function() {
    var mycookie, ai, elem, elem_two, elem_three, datatosend;

    var your_data = JSON.parse($("#data_id").text());

    if ('user_id' in your_data) {
        is_login = 1;
    } else {
        is_login = 0;
    }

	$("#menu li").click(function(event) {
		event.preventDefault();
		$(this).next("ul").toggle();
	});

	var other_books = JSON.parse(your_data['other_books']);

	$('#loginform').on('submit', function(event) {
	    event.preventDefault();
	    ai = $('#loginform').serialize();
	    mycookie = Cookies.get("csrftoken");
	    $('#cover-spin').show(0)
	    $.ajax({
	        url: '/accounts/login/',
	        type: 'POST',
	        headers: {'X-CSRFToken': mycookie},
	        data: ai,
	        error:      function (xhr, ajaxOptions, thrownError) {
	                        var parseresp, x, y, text;
	                        parseresp = JSON.parse(xhr.responseText)
	                        for (x in parseresp['form']['fields']) {
	                            text = ''
	                            if (parseresp['form']['fields'][x]['errors'].length != 0) {
	                                for (y in parseresp['form']['fields'][x]['errors']) {
	                                    text += parseresp['form']['fields'][x]['errors'][y] + '<br>'
	                                }
	                                $('#loginform #err_'.concat(x)).html(text)
	                            }
	                        }
	                        text = ''
	                        if (parseresp['form']['errors'].length != 0) {
	                            for (x in parseresp['form']['errors']) {
	                                text += parseresp['form']['errors'][x] + '<br>'
	                            }
	                            $('#loginform #err_nonfield').html(text)
	                        }
	                        else {
	                            $('#loginform #err_nonfield').html(text)
	                        }
	                        $('#loginmodal').modal('hide')
	                        $('#loginmodal').modal('show')
	                        $('#cover-spin').hide()
	                    },
	        success:    function(data, textStatus, jqXHR) {
	                        var parseresp, text;
	                        parseresp = JSON.parse(jqXHR.responseText)
	                        text = parseresp['html']
                            if (text) {
                                $('#loginform #err_nonfield').html(text.concat("<br>Wysłaliśmy link aktywacyjny ponownie."))
                                $('#loginmodal').modal('hide')
                                $('#loginmodal').modal('show')
                                $('#cover-spin').hide()
                            }
                            else {
                                $('#cover-spin').hide()
                                location.reload();
                            }
	        }
	    });
	});

	$('#signupform').on('submit', function(event) {
	    event.preventDefault();
	    ai = $('#signupform').serialize();
	    mycookie = Cookies.get("csrftoken");
	    $('#cover-spin').show(0)
	    $.ajax({
	        url: '/accounts/signup/',
	        type: 'POST',
	        headers: {'X-CSRFToken': mycookie},
	        data: ai,
	        error:      function (xhr, ajaxOptions, thrownError) {
	                        var parseresp, x, y, text;
	                        parseresp = JSON.parse(xhr.responseText)
	                        for (x in parseresp['form']['fields']) {
	                            text = ''
	                            if (parseresp['form']['fields'][x]['errors'].length != 0) {
	                                for (y in parseresp['form']['fields'][x]['errors']) {
	                                    text += parseresp['form']['fields'][x]['errors'][y] + '<br>'
	                                }
	                                $('#signupform #err_'.concat(x)).html(text)
	                            }
	                            else {
	                                $('#signupform #err_'.concat(x)).html(text)
	                            }
	                        }
	                        text = ''
	                        if (parseresp['form']['errors'].length != 0) {
	                            for (x in parseresp['form']['errors']) {
	                                text += parseresp['form']['errors'][x] + '<br>'
	                            }
	                            $('#signupform #err_nonfield').html(text)
	                        }
	                        else {
	                            $('#signupform #err_nonfield').html(text)
	                        }
	                        $('#signupmodal').modal('hide')
	                        $('#signupmodal').modal('show')
	                        $('#cover-spin').hide()
	                    },
	        success:    function(data, jqXHR ) {
	                        $('#signupmodal').modal('hide')
	                        $('#successsignupmodal #yourmail').html($('#signupmodal #id_email').val())
	                        $('#successsignupmodal').modal('show')
	                        $('#cover-spin').hide()
	                    }
	    });
	});

    $(".buy").click(function(event) {
        event.preventDefault();
        elem_three = $(this);
        $("#quanity").modal("show");
        $("#ok").click(function(event){
            elem = $("#shc span");
            elem_two = $("#number");
            elem.text('(' + (Number(elem.text().slice(1, -1)) + Number(elem_two.val())) + ')');
            if (elem_three.hasClass('main')) {
                elem = JSON.parse(your_data['book'])[0];
            } else {
                index = Number(elem_three.attr('index'));
                elem = other_books[index];
            }
            elem['amount'] = Number(elem_two.val());
            elem = JSON.stringify(elem);
            datatosend = {};
            datatosend.book = elem;
            if (is_login) {
                datatosend.user_additional_data = your_data['user_additional_data'];
            }
            mycookie = Cookies.get("csrftoken");
            $.ajax({
                url: '/add/product/',
                type: 'POST',
                headers: {'X-CSRFToken': mycookie},
                data: datatosend,
                dataType: "json",
                success:    function(data, jqXHR ) {
                    if (is_login) {
                        your_data['user_additional_data'] = data['user_additional_data'];
                    }
                    },
	            error:      function (xhr, ajaxOptions, thrownError) {
	                },
	            complete:   function(jqXHR, textStatus ) {
	                $("#quanity").modal("hide");
	                elem_two.val("1");
	                $('#addtoshopingcard').modal('show');
	                }
            });
        })
    });
});



	
