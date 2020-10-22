function toggleFollow(element) {
    let userIdElement = document.getElementById('user_id');
    let userId = userIdElement.value;
    let csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    if (element.name === 'following') {
        let xhr = new XMLHttpRequest();
        let url = '/users/' + userId + '/unfollow/';

        xhr.open('POST', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);

                if (xhr.status === 200) {
                    element.name = 'not_following';
                    element.textContent = 'Follow';
                    element.className = 'btn btn-outline-primary';
                }
            }
        };
        xhr.send();
    } else {
        let xhr = new XMLHttpRequest();
        let url = '/users/' + userId + '/follow/';

        xhr.open('POST', url, true);
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                console.log('response from ' + url + ' – status: ' + xhr.status + ' responseText: ' + xhr.responseText);

                if (xhr.status === 200) {
                    element.name = 'following';
                    element.textContent = 'Following';
                    element.className = 'btn btn-primary';
                }
            }
        };
        xhr.send();
    }
}