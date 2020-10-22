$(document).ready(function(){
    // initialize like counts
    $('.like-wrapper').each(function(){
        console.log('initializing like buttons');

        let likeWrapper = $(this);
        let likeButton = likeWrapper.children('.like-button');
        let likeCountElement = likeWrapper.children('.like-count');
        let photoId = likeButton.attr('name');

        getLikeCount(photoId, (likeCount) => {
            if (likeCount > 0) {
                likeCountElement.text(likeCount);
            } else {
                likeCountElement.text('');
            }
        });
    });

    // attach a function to toggle like state to all like buttons
    $('.like-wrapper').click(function(){
        let likeWrapper = $(this);
        let likeButton = likeWrapper.children('.like-button');
        let likeCountElement = likeWrapper.children('.like-count');
        let photoId = likeButton.attr('name');
        let csrfToken = $('input[name="csrfmiddlewaretoken"]')[0].value;
        let f = like;
        let url = '/photos/' + photoId + '/like/';
        let xhr = new XMLHttpRequest();

        if (likeButton.hasClass('is-active')) {
            url = '/photos/' + photoId + '/unlike/';
            f = unlike;
        }

        xhr.open('POST', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);

                if (xhr.status === 200) {
                    f(likeButton);
                    getLikeCount(photoId, (likeCount) => {
                       if (likeCount > 0) {
                            likeCountElement.text(likeCount);
                        } else {
                            likeCountElement.text('');
                        }
                    });
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

function getLikeCount(photoId, callback) {
    let csrfToken = $('input[name="csrfmiddlewaretoken"]')[0].value;
    let xhr = new XMLHttpRequest();
    let url = '/photos/' + photoId + '/likecount/';

    xhr.open('GET', url, true);
    xhr.setRequestHeader('X-CSRFToken', csrfToken);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);
            let responseObject = JSON.parse(xhr.responseText);

            if (xhr.status === 200) {
                callback(responseObject.like_count);
            }
        }
    };
    xhr.send();
}