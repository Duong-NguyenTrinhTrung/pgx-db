// script.js
document.addEventListener("DOMContentLoaded", function() {
  var cookieBanner = document.getElementById("cookie-consent-banner");
  var acceptButton = document.getElementById("accept-cookies");
  var declineButton = document.getElementById("decline-cookies");

  // Check if cookies have already been accepted
  if (localStorage.getItem("cookiesAccepted") === "true") {
      cookieBanner.style.display = "none";
  }

  // Accept cookies
  acceptButton.addEventListener("click", function() {
      localStorage.setItem("cookiesAccepted", "true");
      cookieBanner.style.display = "none";
  });

  // Decline cookies
  declineButton.addEventListener("click", function() {
      cookieBanner.style.display = "none";
  });
});
