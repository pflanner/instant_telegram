$(document).ready(function(){
    // initialize like buttons
    $('.like-button').each(function(){
        console.log('initializing like buttons');

        let jqueryElement = $(this);
        let photoId = jqueryElement.attr('name');
        let csrfToken = $('input[name="csrfmiddlewaretoken"]')[0].value;
        let xhr = new XMLHttpRequest();
        let url = '/likecount/' + photoId + '/';

        xhr.open('GET', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);
                let responseObject = JSON.parse(xhr.responseText);

                if (xhr.status === 200) {
                    if (responseObject.like_count > 0) {
                        like(jqueryElement);
                    }
                }
            }
        };
        xhr.send();
    });

    // attach a function to toggle like state to all like buttons
    $('.like-button').click(function(){
        let jqueryElement = $(this);
        let photoId = jqueryElement.attr('name');
        let csrfToken = $('input[name="csrfmiddlewaretoken"]')[0].value;
        let f = like;
        let url = '/like/' + photoId + '/'
        let xhr = new XMLHttpRequest();

        if ($(this).hasClass('is-active')) {
            url = '/unlike/' + photoId + '/';
            f = unlike;
        }

        xhr.open('POST', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);

                if (xhr.status === 200) {
                    f(jqueryElement);
                }
            }
        };
        xhr.send();
    });
});

function like(jqueryElement) {
    console.log('liked')
    jqueryElement.addClass('is-active');
}

function unlike(jqueryElement) {
    console.log('unliked')
    jqueryElement.removeClass('is-active');
}