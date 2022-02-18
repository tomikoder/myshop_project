$(function() {
    var your_data = JSON.parse($("#data_id").text());
    var price_one = your_data['price_one'];
    var price_two = your_data['price_two'];
    var flag = 0;

    $("input[name='payment']").change(function(){
        if (!flag) {
            $("#sum").text(price_two);
            flag = 1;
        } else {
            $("#sum").text(price_one);
            flag = 0;
        }
    });
});