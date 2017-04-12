var shouldClear = false;

document.addEventListener('DOMContentLoaded', function() {
    // Pincode verification code
    $('.check-button').on('click', function(){
        var code = $('.code').val();
        var checkBox = $('.check-box').is(':checked');

        console.log(checkBox);

        if (!(code.length != 6 || /^\d+$/.test(code))) {
            console.log('Invalid Code');
            appendToResults('Invalid Code, Try again', 'high');
            return;
        }

        if (!checkBox) {
            console.log('Needs to check Privacy Policy');
            appendToResults('Please agree to the Privacy Policy', 'medium');
            return;
        }

        var qs = getUrlVars();
        var uid = qs.uid;
        var pin = code;

        $.post(
            'http://108.14.46.160:8080/auth',
            {
                'uid': uid,
                'pin': pin
            },
            function(data, status) {
                data = JSON.parse(data);
                console.log(data, status);
                if (data.status == 'success') {
                    appendToResults('Success, you will be verified momentarily!', 'low');
                } else {
                    appendToResults('Error: ' + data.error, 'high');
                }
            }
        );
    });
});

function appendToResults(text, importance) {
    if (shouldClear) {
        $('.results').children().fadeOut('slow');
        $('.results').empty();
        shouldClear = false;
    }

    var data = '<p class="result ' + importance + '" style="width: 40px;margin-top: 30px;">' + text + '</p>';
    $(data).appendTo('.results').hide().fadeIn('slow');
    shouldClear = true;
}

function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}
