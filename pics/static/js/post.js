const fileSelect = document.getElementById("fileSelect");
const fileElem = document.getElementById("fileElem");
const fileSubmit = document.getElementById("fileSubmit");
const fileForm = document.getElementById("fileForm");

fileSelect.addEventListener("click", function (e) {
  if (fileElem) {
    fileElem.click();
  }
}, false);

fileElem.addEventListener("change", function(e) {
  console.log("clicking fileSubmit");
  fileSubmit.click();
});

fileForm.addEventListener("submit", function(e) {
  e.preventDefault();

  console.log("submitting");
  const fd = new FormData(fileForm);
  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/post/", true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      alert("status: " + xhr.status + " responseText: " + xhr.responseText); // handle response.
    }
  };
  xhr.send(fd);
}, false);