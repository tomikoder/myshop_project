$(function() {
    var your_data = JSON.parse($("#data_id").text());
    var price_one = your_data['price_one'];
    var price_two = your_data['price_two'];
    var flag_one = 0;
    var flag_two = 0;

    $("#id_delivery_method_0").prop('checked', true);
    $("#id_payment_method_0").prop('checked', true);

    $(".payment").change(function(){
        if (!flag_one) {
            $("#sum").text(price_two);
            flag_one = 1;
        } else {
            $("#sum").text(price_one);
            flag_one = 0;
        }
    });

    $(".delivery").change(function() {
        if (!flag_two) {
            $('#id_payment_method_0').parent().hide();
            flag_two = 1;
            if ($('#id_payment_method_1').prop('checked') == false) {
                $('#id_payment_method_0').prop('checked', false);
                $('#id_payment_method_1').prop('checked', true);
                flag_one = 1;
            }
        } else {
            $('#id_payment_method_0').parent().show();
            flag_two = 0;
        }
    });

});