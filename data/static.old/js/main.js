document.addEventListener('DOMContentLoaded', function() {
    // Pincode verification code
    $('#pin').pincodeInput({
        inputs: 6,
        hideDigits: false,
        keydown: function(e) {},
        complete: function(value, e, errorElement) {
            var qs = getUrlVars();
            var uid = qs.uid;
            var pin = value;

            // Send request
            $.post(
                'http://108.14.46.160:8080/auth',
                {
                    'uid': uid,
                    'pin': pin
                },
                function(data, status) {
                    data = JSON.parse(data);
                    console.log(data, status);

                    $('.done').removeClass('disabled');
                    $('.form').addClass('disabled');

                    if (data.status == 'success') {
                        alert('Verification successful!');
                    } else {
                        alert('Error: ' + data.error);
                        window.location.reload();
                    }
                }
            );
        }
    });
});

function getUrlVars() {
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}
