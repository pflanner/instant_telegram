const fileForm = document.getElementById("fileForm");

fileForm.addEventListener("submit", function(e) {
  e.preventDefault();

  console.log("submitting");
  const fd = new FormData(fileForm);
  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/post/", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      console.log("status: " + xhr.status + " responseText: " + xhr.responseText); // handle response.
      $("#postModal").modal("hide");
    }
  };
  xhr.send(fd);
}, false);