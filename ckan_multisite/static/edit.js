$(function () {
    // Does a ajax request to the ckan-multisite API
    function do_api_request(endpoint, success, failure) {
        if (success == undefined) {
            success = function (data) {
                obj = JSON.parse(data);
                $("#alert_field").text(obj.success);
                $("#alert_field").removeClass('hidden');
            };
        }
        if (failure == undefined) {
            failure = function (data) {
                obj = JSON.parse(data);
                $("#alert_field").text("Error: " + obj.error);
                $("#alert_field").removeClass('hidden');
            };
        }

        $.ajax({
            type: "POST",
            url: "/api/v1/" + endpoint,
            data: {name: $("#site_name").val()},
            success: success,
            error: failure
        });
    }
    
    $("#start_button").click(function () {
        do_api_request("start")
    });

    $("#stop_button").click(function () {
        do_api_request("stop")
    });

    $("#status_button").click(function () {
        do_api_request("status", function (data) {
            obj = JSON.parse(data);
            $("#alert_field").text("Default port: " + obj.default_port + " Containers Running: " + obj.containers_running);
            $("#alert_field").removeClass('hidden');
        })
    })
});
