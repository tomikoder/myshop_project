$(function() {
    var datatosend, elem, c, elemTwo;
    var your_data = JSON.parse($("#data_id").text());

    if ('user_id' in your_data) {
        is_login = 1;
    } else {
        is_login = 0;
    }

    $("#clearshc").click(function(event) {
        event.preventDefault();
        datatosend = {};
        if (is_login) {
            datatosend.user_additional_data = your_data['user_additional_data'];
        }
        mycookie = Cookies.get("csrftoken");
        $.ajax({
            url: '/clear/shc/',
            type: 'POST',
            headers: {'X-CSRFToken': mycookie},
            data: datatosend,
            dataType: "json",
            success:    function(data, jqXHR ) {
                $("#shc span").text("(0)");
                $("#products").empty();
                if ('user_additional_data' in data) {
                    your_data['user_additional_data'] = data['user_additional_data'];
                }
                $("#clearshc").hide();
                $("#placeorder").hide();
                $("#sum").hide();
                $("#greeting_text").text('Twój koszyk jest pusty');
                $("#finalize").hide();
                },
	        error:      function (xhr, ajaxOptions, thrownError) {
	            },
	        complete:   function(jqXHR, textStatus ) {
	            }
         });
    });

    //Zmienia ilość produktu w koszyku
    $('.number').change(function(){
        elem = $(this);
        setTimeout(function(){
            if (elem.val()) {
                $('#cover-spin').show();
                datatosend = {};
                elemTwo = elem.parent().parent().parent();
                if (is_login) {
                    datatosend.user_additional_data = your_data['user_additional_data'];
                }
                datatosend.index = Number(elemTwo.attr('id')[5]);
                datatosend.new_amount = elem.val();
                mycookie = Cookies.get("csrftoken");
                $.ajax({
                    url: '/change/items/shc/',
                    type: 'POST',
                    headers: {'X-CSRFToken': mycookie},
                    data: datatosend,
                    dataType: "json",
                    success:    function(data, jqXHR ) {
                        elem.next().text(data['new_total']);
                        $('#sum span').text(data['new_sum']);
                        $('#shc span').text('(' + elem.val() + ')');
                        if ('user_additional_data' in data) {
                            your_data['user_additional_data'] = data['user_additional_data'];
                        }
                    },
	                error:      function (xhr, ajaxOptions, thrownError) {
	                },
	                complete:   function(jqXHR, textStatus ) {
	                    $('#cover-spin').hide();
	                }
                });
            } else {
            }
        }, 2000);
    });

    //Usuwa produkt z koszyka
    $(".product div a").click(function(event) {
        event.preventDefault();
        elem = $(this).parent().parent();
        mycookie = Cookies.get("csrftoken");
        datatosend = {};
        datatosend.index = Number(elem.attr('id')[5]);
        if (is_login) {
            datatosend.user_additional_data = your_data['user_additional_data'];
        }
        $.ajax({
            url: '/remove/items/shc/',
            type: 'POST',
            headers: {'X-CSRFToken': mycookie},
            data: datatosend,
            dataType: "json",
            success:    function(data, jqXHR ) {
                elem.remove();
                if ('user_additional_data' in data) {
                    your_data['user_additional_data'] = data['user_additional_data'];
                }
                c = 0;
                $("#products").children().each(function(){
                    $(this).attr("id", ("index" + c));
                    c++;
                });
                if (data['sum'] == '0.00') {
                    $("#greeting_text").text("Twój koszyk jest pusty");
                    $("#sum").hide();
                    $("#clearshc").hide();
                    $("#placeorder").hide();
                    $("#finalize").hide();
                }
                else {
                    $("#sum").text("W sumie: " + data['sum']);
                }
                elem = Number($("#shc span").text().slice(1, -1));
                elem = elem - data['substract'];
                $("#shc span").text("(" + elem + ")");
                $("#products").append('<p>' + data['message'] + "</p>")
                },
	        error:      function (xhr, ajaxOptions, thrownError) {
	            },
	        complete:   function(jqXHR, textStatus ) {
	            }
         });
    });
});