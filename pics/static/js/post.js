const fileForm = document.getElementById("fileForm");

fileForm.addEventListener("submit", function(e) {
  e.preventDefault();

  console.log("submitting");
  const fd = new FormData(fileForm);
  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/photos/", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      console.log("status: " + xhr.status + " responseText: " + xhr.responseText); // handle response.
      $("#postModal").modal("hide");

      let pageName = $('#page-name').val();

      if (pageName === 'photos') {
        $('#photo-content').prepend(xhr.responseText);
        initializeComments();
      }
    }
  };
  xhr.send(fd);
}, false);