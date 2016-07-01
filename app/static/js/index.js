$(document).ready(function() {
    $('#main-form').submit(function(e) {
        var pref = {}
        pref.username = $('#username').val()
        pref.password = $('#password').val()
        pref.restrictions = $('#restrict').val()
        pref.favorites = $('#favorites').val()
        pref.scores = []

        $('.slider').each(function(){
            pref.scores.push($(this).attr('item') + '-' + $(this).val());
        });

        pref.scores = pref.scores.join();
        console.log(pref);
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
                    $('#favorites').val(result.favorites.join(', '))
                    $('#restrict').val(result.restrictions.join(', '))
                    $('.slider').each(function() {
                        var tokens = $(this).attr('item').split('-');
                        $(this).val(result.scores[tokens[0]][tokens[1]]);
                    })
                }
            })
        }
    })
});