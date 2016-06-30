$(document).ready(function() {
    $('#main-form').submit(function(e) {
        var pref = {}
        pref.username = $('#username').val()
        pref.password = $('#password').val()
        pref.preference = $('#preference').val()

        URL = "api/preferences/"
        $.post(URL, pref, function(result) {
            if (result) {
                window.location.href = "thanks/"
            } else {

            }
        })
        return false;
    });

    $('#password').change(function() {
        var username = $('#username').val()
        var password = $('#password').val()
        if (username != "" && password != "") {
            URL = "api/preferences/"
            data = {
                username:username,
                password:password
            }
            $.get(URL, data, function(result) {
                if(result) {
                    $('#preference').val(result.preference)
                }
            })
        }
    })
});