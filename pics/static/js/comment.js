$(document).ready(function(){
    // initialize comment forms
    $('.comment-form').each(function(){
        setCommentFormState($(this));
    });
});


$('.comment-text').on('change keyup paste', function() {
    console.log('comment-text changing');
    let form = $(this).parent();

    setCommentFormState(form);
});

$('.comment-form').submit(function(e) {
    e.preventDefault();

    let form = $(this);
    let formText = form.children('.comment-text');
    let photoId = form.attr('name');

    if (formText[0].value.length === 0) {
        console.log('comment text empty; not submitting');
        return;
    }

    console.log('submitting comment');
    console.log(form);
    const fd = new FormData(form[0]);
    const xhr = new XMLHttpRequest();

    xhr.open('POST', '/photos/' + photoId + '/comments/', true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            console.log("status: " + xhr.status + " responseText: " + xhr.responseText); // handle response.
            formText.val('');
        }
    };
    xhr.send(fd);
});

function setCommentFormState(form) {
    let commentText = form.children('.comment-text');
    let submitButton = form.children('.comment-submit');

    if (commentText[0].value.length === 0) {
        submitButton.attr('disabled', true);
    } else {
        submitButton.attr('disabled', false);
    }
}