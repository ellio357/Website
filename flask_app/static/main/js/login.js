let count = 0;

$(document).ready(function () {
    console.log("Document ready");

    $('#loginForm').on('submit', function (event) {
        event.preventDefault();
        console.log("Form submitted");

        const isNewUser = $('#newUser').is(':checked');
        const data_d = {
            email: $('#email').val(),
            password: $('#password').val(),
            new_user: isNewUser
        };

        console.log("Data to send:", data_d);

        $.ajax({
            url: "/processlogin",
            data: data_d,
            type: "POST",
            success: function (returned_data) {
                console.log("Returned from server:", returned_data);
                const parsed = JSON.parse(returned_data);

                if (parsed.success) {
                    console.log("Login success, redirecting to /home");
                    window.location.href = "/home";
                } else {
                    count++;
                    $('#error-message').text('Authentication Failure: ' + count);
                    console.log("Login failed, count:", count);
                }
            },
            error: function (xhr, status, error) {
                console.error("AJAX error:", status, error);
            }
        });
    });
});
