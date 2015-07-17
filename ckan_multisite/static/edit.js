$(function () {
    // Does a ajax request to the ckan-multisite API
    function simple_api_request(endpoint, success, failure, params) {
        if (success == undefined) {
            success = function (data) {
                $("#alert_field").text(data.success);
                $("#alert_field").removeClass('hidden');
            };
        }
        if (failure == undefined) {
            failure = function (data) {
                $("#alert_field").text("Error: " + data.responseJSON.error);
                $("#alert_field").removeClass('hidden');
            };
        }
        if (params == undefined) {
            params = {name: $("#site_name").val()}
        }

        $.ajax({
            type: "POST",
            url: "/api/v1/" + endpoint,
            data: params,
            success: success,
            error: failure
        });
    }
    
    $("#start_button").click(function () {
        simple_api_request("start");
    });

    $("#stop_button").click(function () {
        simple_api_request("stop");
    });

    $("#status_button").click(function () {
        simple_api_request("status", function (data) {
            $("#alert_field").text("Default port: " + data.default_port + " Containers Running: " + data.containers_running);
            $("#alert_field").removeClass('hidden');
        })
    });

    function submit_pw_form(event) {
        // Stop form submission via HTTP
        event.preventDefault();
        // First we validate the form
        group = $("#pw_control_group");
        pw = $("#pw");
        confirm_pw = $("#confirm_pw");
        error_label = $("#pw_error_label");

        if (pw.val() != confirm_pw.val()) {
            group.addClass("error");
            error_label.text("Password and confirm must match.");
        }
        else if (pw.val() == "" || confirm_pw.val() == "") {
            group.addClass("error");
            error_label.text("Passwords cannot be blank.");
        }
        else if (pw.val().length < 4) {
            group.addClass("error");
            error_label.text("Passwords must be more than 4 characters");
        }
        else {
            // Remove error class and error if no error
            group.removeClass("error");
            error_label.text("");
            simple_api_request("change_admin", undefined, undefined, {name: $("#site_name").val(), password: pw.val()});
        }
    }

    $("#reset_pw_button").click(submit_pw_form);
    $("#pw,#pw_confirm").keypress(function(event) {
        // Enter key
        if (event.which == 13) {
            submit_pw_form(event);
        }
    });
});
