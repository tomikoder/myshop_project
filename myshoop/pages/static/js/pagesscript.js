$(function() {
    var stars, sib, datatosend, number_of_votes, elem, elem_two, elem_three, elem_four, new_rate, actual_val, first_vote, index, rev_like, one_click;
    var voted = 0;
    var update_vote = 0;
    var your_data = JSON.parse($("#data_id").text());


    var button1 = 1;
    var button2 = 0;
    var button3 = 0;
    var button4 = 1;

    if ('user_id' in your_data) {
        is_login = 1;
    } else {
        is_login = 0;
    }

    var other_books = JSON.parse(your_data['other_books']);

    $('[data-toggle="tooltip"]').tooltip('hide');
    you_liked = your_data['you_liked'];

    if ('your_rate' in your_data) {
        voted = 1;
        first_vote = 0;
    } else {
        first_vote = 1;
    }

    if (!you_liked) {
        $("[data-toggle='tooltip']").tooltip('hide');
    }
    else {
        $("[data-toggle='tooltip']").tooltip();
    }

    $("#book_img").mouseover(function(){
        $(this).css('cursor', 'zoom-in');
    });

    $("#content_to_display1").click(function(event){
        event.preventDefault();
        if (button1) {
            $(this).children().attr('class', 'fas fa-chevron-up');
            button1 = 0;
        }
        else {
            $(this).children().attr('class', 'fas fa-chevron-down');
            button1 = 1;
        }
        $(this).parent().next().toggle();
    });

    $("#content_to_display2").click(function(event){
        event.preventDefault();
        if (button2) {
            $(this).children().attr('class', 'fas fa-chevron-up');
            button2 = 0;
        }
        else {
            $(this).children().attr('class', 'fas fa-chevron-down');
            button2 = 1;
        }
        $(this).parent().next().toggle();
    });

    $("#content_to_display3").click(function(event){
        event.preventDefault();
        if (button3) {
            $(this).children().attr('class', 'fas fa-chevron-up');
            button3 = 0;
        }
        else {
            $(this).children().attr('class', 'fas fa-chevron-down');
            button3 = 1;
        }
        $(this).parent().next().toggle();
    });

    $("#content_to_display4").click(function(event){
        event.preventDefault();
        if (button4) {
            $(this).children().attr('class', 'fas fa-chevron-up');
            button4 = 0;
        }
        else {
            $(this).children().attr('class', 'fas fa-chevron-down');
            button4 = 1;
        }
        $("#reviews").toggle();
    });

	$("#vote span").mouseover(function(){
	    if (!voted) {
	        $(this).css('cursor', 'pointer');
	        $(this).addClass("checked");
	        sib = $(this).prevAll();
	        sib.addClass("checked");
	    }

	    $(this).mouseout(function(){
	        if (!voted) {
                $(this).removeClass("checked");
	            $(this).prevAll().removeClass("checked");
            }
        });

        block = 0;


        $(this).on('click', function(){
            if (!block) block = 1;
            else return;
            $(this).css('cursor', 'default');
            datatosend = {};
            voted = 1;
            elem = JSON.parse(your_data['book']);
            elem = elem['id'];
            datatosend.book_pk = elem;
            stars = sib.length + 1;
	        datatosend.stars = stars;
	        datatosend.first_vote = first_vote;
            mycookie = Cookies.get("csrftoken");
            if (!first_vote) {
                datatosend.your_rate = your_data['your_rate'];
            }
            $.ajax({
                url: '/vote/book/',
                type: 'POST',
                headers: {'X-CSRFToken': mycookie},
                data: datatosend,
                dataType: "json",
                success:    function(data, jqXHR ) {
                    new_rate = data["new_rate"];
                    elem = $("#rate").children("span.fa");
                    elem.removeClass("checked");
                    for (let i = 0; i < new_rate; i++) {
                        elem[i].classList.add("checked");
                    }
                    if (first_vote) {
                        first_vote = 0;
                        your_data['your_rate'] = data['your_rate'];
                        elem = $("#number_of_votes");
                        elem.text("(" + (parseInt(elem.text().slice(1, -1)) + 1) + ")");
                    }
                },
	            error:      function (xhr, ajaxOptions, thrownError) {
	                block = 0;
	                $("#err").show();
	            },
	            complete:   function(jqXHR, textStatus ) {
	                update_vote = 0;
	                $("#change").show();
	                block = 0;
	            }
            });
	    });
	});

	$("#change").click(function(event) {
       event.preventDefault();
       $(this).hide();
       $(this).prevAll().removeClass("checked");
       voted = 0;
       update_vote = 1;
    });

    $("#curr_page").click(function(event) {
        event.preventDefault();
    });

    block_two = 0;

	$("#like_book").click(function(event) {
	    if (block_two) {
	        event.preventDefault();
            return;
	    }
	    block_two = 1;
	    event.preventDefault();
	    datatosend = {};
	    mycookie = Cookies.get("csrftoken");
	    elem = JSON.parse(your_data['book']);
        elem = elem['id'];
        datatosend.book_pk = elem;
        datatosend.user_additional_data = your_data['user_additional_data'];
        elem = $(this);
        if (you_liked) {
            $.ajax({
                url: '/unlike/book/',
                type: 'POST',
                headers: {'X-CSRFToken': mycookie},
                data: datatosend,
                dataType: "json",
                success:    function(data, jqXHR ) {
                    elem.prev().attr('class', 'far fa-heart ml-2 text-primary ml-1');
                    elem.find('strong').text('Polub');
                    elem = elem.next();
                    elem.text('  ' + (parseInt(elem.text()) - 1) + " polubiło");
                    your_data['user_additional_data'] = data['user_additional_data'];
                    you_liked = 0;
                    $("[data-toggle='tooltip']").tooltip('dispose');
                },
	            error:      function (xhr, ajaxOptions, thrownError) {
	            },
	            complete:   function(jqXHR, textStatus ) {
	                block_two = 0;
	            }
            });
        } else {
            $.ajax({
                url: '/like/book/',
                type: 'POST',
                headers: {'X-CSRFToken': mycookie},
                data: datatosend,
                dataType: "json",
                success:    function(data, jqXHR ) {
                    elem.prev().attr('class', 'fas fa-heart ml-2 text-primary ml-1');
                    elem.find('strong').text('Lubisz');
                    elem = elem.next();
                    elem.text('  ' + (parseInt(elem.text()) + 1) + " polubiło");
                    your_data['user_additional_data'] = data['user_additional_data'];
                    you_liked = 1;
                    $("[data-toggle='tooltip']").tooltip('show');
                },
	            error:      function (xhr, ajaxOptions, thrownError) {
	            },
	            complete:   function(jqXHR, textStatus ) {
	                block_two = 0;
	            },
            });
        }
	});

    $("#post").click(function(event) {
        event.preventDefault();
        if (!voted) {
            $("#error2").modal('show');
        } else {
            $("#comment_form").toggle();
	        $('#comment_form').on('submit', function(event) {
	            event.preventDefault();
	            datatosend = {};
                datatosend.subject = $("#subject").val();
                datatosend.content = $("#content").val();
                datatosend.book_pk = JSON.parse(your_data['book'])['id'];
                datatosend.your_rate = your_data['your_rate'];
                datatosend.num_of_reviews = your_data['num_of_reviews'];
                mycookie = Cookies.get("csrftoken");
                $.ajax({
                    url: '/post/book/review/',
                    type: 'POST',
                    headers: {'X-CSRFToken': mycookie},
                    data: datatosend,
                    dataType: "json",
                    success:    function(data, jqXHR) {
                    	$("#comment_form").toggle();
	                    $("#subject").val("");
	                    $("#content").val("");
	                    elem = $("#reviews");
	                    elem.children().each(function() {
	                        elem_two = $(this).find(".index");
	                        elem_two.attr("index", (Number(elem_two.attr("index")) + 1));
	                    });
                        elem.prepend(data['output']);
                        $("#post").text('Już dodałeś/aś recenzję !');
                        your_data['num_of_reviews']++;
                        $("#rev_num").text(your_data['num_of_reviews']);
                        elem = JSON.parse(your_data['book_reviews']);
                        elem.splice(0, 0, JSON.parse(data['your_review'])[0]);
                        your_data['book_reviews'] = JSON.stringify(elem);
                        your_data['is_reviewed'] = true;
                        your_data['your_rate'] = data['your_rate'];
                    },
	                error:      function (xhr, ajaxOptions, thrownError) {
	                },
	                complete:   function(jqXHR, textStatus) {
	                }
                });
            });
        }
    });

	$('#remove').on("click", function(event) {
	    event.preventDefault();
        index = Number($(this).parent().attr('index'));
        datatosend = {};
        elem = JSON.parse(your_data['book_reviews']);
        datatosend.your_review_pk = elem[index]['pk'];
        datatosend.your_rate = your_data['your_rate'];
        mycookie = Cookies.get("csrftoken");
        $.ajax({
            url: '/remove/book/review/',
            type: 'POST',
            headers: {'X-CSRFToken': mycookie},
            data: datatosend,
            dataType: "json",
            success:    function(data, jqXHR ) {
                elem.splice(index, 1);
                elem_two = $("#reviews").children();
                elem_two.eq(index).remove();
                c = 0;
                elem_two.each(function() {
                    elem_three = $(this).find(".index");
                    elem_three.attr("index", c);
                    c++;
                });
                your_data['book_reviews'] = JSON.stringify(elem);
                your_data['your_rate'] = data['your_rate'];
                your_data['num_of_reviews']--;
                elem = $("#rev_num");
                elem.text(your_data['num_of_reviews']);
                $("#post").html('<a href="">Napisz recenzję</a>');
                your_data['is_reviewed'] = false;
                your_data['your_rate'] = data['your_rate'];
            },
	        error:      function (xhr, ajaxOptions, thrownError) {
	        },
	        complete:   function(jqXHR, textStatus ) {
	        }
        });
	});

    $("#edit").on("click", function(event) {
        event.preventDefault();
        elem = $(this).parent();
        index = Number(elem.attr('index'));
	    $("#subject").val(elem.prev().prev().text());
	    $("#content").val(elem.prev().text());
        $("#comment_form").show();
        location.href = "#comment_form";
	    $('#comment_form').on('submit', function(event) {
	        event.preventDefault();
            datatosend = {};
            elem_two = JSON.parse(your_data['book_reviews']);
            datatosend.your_review = JSON.stringify([elem_two[index]]);
            datatosend.subject = $("#subject").val();
            datatosend.content = $("#content").val();
            mycookie = Cookies.get("csrftoken");
            $.ajax({
                url: '/edit/book/comment/',
                type: 'POST',
                headers: {'X-CSRFToken': mycookie},
                data: datatosend,
                dataType: "json",
                success:    function(data, jqXHR ) {
                    elem_two.splice(index, 1, JSON.parse(data['your_review'])[0]);
                    your_data['book_reviews'] = JSON.stringify(elem_two);
                    elem.prev().prev().text($("#subject").val());
                    elem.prev().text($("#content").val());
                    $("#comment_form").toggle();
                },
	            error:      function (xhr, ajaxOptions, thrownError) {
	            },
	            complete:   function(jqXHR, textStatus ) {
	            }
            });
	    });
    });

    $("#like_review").click(function(event) {
        event.preventDefault();
        datatosend = {};
        index = Number($(this).parent().attr('index'));
        rev_like = Number($(this).attr('isliked'));
        mycookie = Cookies.get("csrftoken");
        elem = JSON.parse(your_data['book_reviews'])[index];
        elem = JSON.stringify([elem]);
        datatosend.liked_review = elem;
        datatosend.user_id = your_data['user_id'];
        datatosend.rev_like = rev_like;
        elem = $(this);
        $.ajax({
            url: '/like/book/review/',
            type: 'POST',
            headers: {'X-CSRFToken': mycookie},
            data: datatosend,
            dataType: "json",
            success:    function(data, jqXHR ) {
                if (data['rev_like']) {
                    elem.text('Lubisz ');
                    elem.next().attr('class', 'fas fa-thumbs-up pt-1');
                    elem_two = elem.parent().next().find('.u');
                    elem_two.text(parseInt(elem_two.text()) + 1 + ' uznało tę recenzję za przydatną.');
                }
                else {
                    elem.text('Polub  ');
                    elem.next().attr('class', 'far fa-thumbs-up pt-1');
                    elem_two = elem.parent().next().find('.u');
                    elem_two.text(parseInt(elem_two.text()) - 1 + ' uznało tę recenzję za przydatną.');
                }
                elem.attr('isliked', String(data['rev_like']));
                elem = JSON.parse(your_data['book_reviews']);
                elem[index] = JSON.parse(data['review'])[0];
                your_data['book_reviews'] = JSON.stringify(elem);
            },
	        error:      function (xhr, ajaxOptions, thrownError) {
	        },
	        complete:   function(jqXHR, textStatus ) {
	        }
        });
    });

    $("#hide_form").on("click", function(event) {
        event.preventDefault();
        $('#comment_form').hide();
    });

    var curr_index = 0;


    //Przewijam w karuzeli kolejne ksiązki
    $("#pl").click(function(event) {
        event.preventDefault();
        if (!curr_index == 0) {
            elem = $("#other_books");
            elem.children('.other_book').css({"visibility": "hidden"});
            curr_index = curr_index - 5;
            c = 0;
            elem_two = other_books.slice(curr_index, curr_index + 5);
            elem.children('.other_book').each(function() {
                elem_three = $(this);
                if (Number(elem_two[c]['is_long_name'])) {
                    elem_three.find(".add_new_line").hide();
                } else {
                    elem_three.find(".add_new_line").show();
                }
                elem_three.find('.other_book_link').attr("href", ('/books/' + elem_two[c]['link']));
                elem_three.find('.other_book_img').attr("src", elem_two[c]['menu_img']);
                elem_three.find('.other_book_title').text(elem_two[c]['title']);
                elem_three.find('.other_book_author').text(elem_two[c]['author']);
                if (elem_two[c]['promotional_price'] != '0.00') {
                    elem_three.find('.price_one').text(elem_two[c]['price'] + " zł  ").show();
                    elem_three.find('.price_two').text(elem_two[c]['promotional_price'] + " zł");
                } else {
                    elem_three.find('.price_one').text("").hide();
                    elem_three.find('.price_two').text(elem_two[c]['price'] + " zł");
                }
                c2 = elem_two[c]['rate'];
                elem_three.find('other_book_rate').children().removeClass("checked").each(function() {
                    if (c2 != 0) {
                        $(this).addClass("checked");
                        c2--;
                    } else {
                        return false;
                    }
                });
                elem_three.find('.buy').attr('index', String(elem_two[c]['index']));
                c++;
	        });
            elem.children('.other_book').css({"visibility": "visible"});
        }
    });

    $("#pr").click(function(event) {
        event.preventDefault();
        if (curr_index != 10) {
            elem = $("#other_books");
            elem.children('.other_book').css({"visibility": "hidden"});
            curr_index = curr_index + 5;
            c = 0
            elem_two = other_books.slice(curr_index, curr_index + 5);
            elem.children('.other_book').each(function() {
                elem_three = $(this);
                if (Number(elem_two[c]['is_long_name'])) {
                    elem_three.find(".add_new_line").hide();
                } else {
                    elem_three.find(".add_new_line").show();
                }
                elem_three.find('.other_book_link').attr("href", ('/books/' + elem_two[c]['link']));
                elem_three.find('.other_book_img').attr("src", elem_two[c]['menu_img']);
                elem_three.find('.other_book_title').text(elem_two[c]['title']);
                elem_three.find('.other_book_author').text(elem_two[c]['author']);
                if (elem_two[c]['promotional_price'] != '0.00') {
                    elem_three.find('.price_one').text(elem_two[c]['price'] + "  zł  ").show();
                    elem_three.find('.price_two').text(elem_two[c]['promotional_price'] + " zł");
                } else {
                    elem_three.find('.price_one').text("").hide();
                    elem_three.find('.price_two').text(elem_two[c]['price'] + " zł");
                }
                c2 = elem_two[c]['rate'];
                elem_three.find('other_book_rate').children().removeClass("checked").each(function() {
                    if (c2 != 0) {
                        $(this).addClass("checked");
                        c--;
                    } else {
                        return false;
                    }
                });
                elem_three.find('.buy').attr('index', String(elem_two[c]['index']));
                c++;
	        });
            elem.children('.other_book').css({"visibility": "visible"});
        }
    });
});