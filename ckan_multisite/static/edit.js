$(function () {
    // Does a ajax request to the ckan-multisite API
    function simple_api_request(endpoint, success, failure, method, params) {
        $("html").css("cursor", "wait");
        if (success == undefined) {
            success = function (data) {
                $("#alert_field").text(data.success);
                $("#alert_field").removeClass('hidden');
                $("html").css("cursor", "auto");
            };
        }
        if (failure == undefined) {
            failure = function (data) {
                $("#alert_field").text("Error: " + data.responseJSON.error);
                $("#alert_field").removeClass('hidden');
                $("html").css("cursor", "auto");
            };
        }
        if (params == undefined) {
            params = {name: $("#site_name").val()}
        }
        if (method == undefined) {
            method = 'POST';
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
            $("body").css("cursor", "auto");
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
            simple_api_request("change_admin", undefined, undefined, undefined, {name: $("#site_name").val(), password: pw.val()});
        }
    }

    $("#reset_pw_button").click(submit_pw_form);
    $("#pw,#confirm_pw").keypress(function(event) {
        // Enter key
        if (event.which == 13) {
            submit_pw_form(event);
        }
    });

    function enable_buttons() {
        $('#status_button,#pw,#confirm_pw,#reset_pw_button,#start_button,#stop_button,#display_name').removeAttr('disabled')
    }

    function disable_buttons() {
        $('#status_button,#pw,#confirm_pw,#reset_pw_button,#start_button,#stop_button,#display_name').prop('disabled', 'true')
    }


    function poll_create_done() {
        simple_api_request("is_site_ready", function (data) {
	    if (data.ready) {
                enable_buttons();
                $("html").css("cursor", "auto");
            }
            else {
                setTimeout(poll_create_done, 3000);
            }
	});
    }

    if ($('#finished_create').val() !== "True") {
        disable_buttons();
        poll_create_done();
    }
});
