window.onload = function () {
    $('#upload_photo_display').css({ "height": 180, "width": 180 });
};

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            console.log(e.target.result)
            let $image = $('#upload_photo_display')
            let width = $image.width();
            let height = $image.height();
            $image.attr('src', e.target.result);
            $image.css({ "height": height, "width": width });
            console.log($image.src)
        };

        reader.readAsDataURL(input.files[0]);
    }
}

$('#upload_photo').click(function () {
    $('#id_photo').click();
});