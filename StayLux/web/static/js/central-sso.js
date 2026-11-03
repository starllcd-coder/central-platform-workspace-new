(function () {
  var params = new URLSearchParams(window.location.hash.slice(1));
  var ticket = params.get("central_sso");
  if (!ticket) return;
  history.replaceState(null, "", window.location.pathname + window.location.search);
  fetch("/api/central/sso/", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({token:ticket})})
    .then(function(response){ return response.json().then(function(body){if(!response.ok)throw new Error(body.error);return body;}); })
    .then(function(){window.location.replace("/");})
    .catch(function(){var message=document.createElement("p");message.setAttribute("role","alert");message.textContent="Central sign-in could not be completed. Your normal app login remains available.";var form=document.querySelector("form");if(form)form.prepend(message);});
})();
