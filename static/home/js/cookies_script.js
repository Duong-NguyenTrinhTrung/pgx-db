
document.addEventListener('DOMContentLoaded', function() {
    const banner = document.getElementById('cookie-consent-banner');
    const acceptBtn = document.getElementById('accept-cookies');
    const declineBtn = document.getElementById('decline-cookies');
    // const learnMoreLink = document.getElementById('learn-more-link');

    // Show banner if consent is not given
    if (!localStorage.getItem('cookiesAccepted')) {
        banner.style.display = 'block';
    }

    // Handle accept button click
    acceptBtn.addEventListener('click', function() {
        localStorage.setItem('cookiesAccepted', 'true');
        banner.style.display = 'none';
        enableCookies();
    });

    // Handle decline button click
    declineBtn.addEventListener('click', function() {
        localStorage.setItem('cookiesAccepted', 'false');
        banner.style.display = 'none';
        disableCookies();
    });

    // Learn more link (could open a modal or redirect to a policy page)
    // learnMoreLink.addEventListener('click', function(event) {
    //     event.preventDefault();
    //     // Display your "Learn More" information here
    //     alert('Learn more about our cookie policy...');
    // });

    // Enable cookies (analytics or other non-essential cookies)
    function enableCookies() {
        // Initialize analytics or other non-essential cookies
        // Example: Google Analytics initialization
        // (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        // (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        // m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        // })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
        // ga('create', 'YOUR_TRACKING_ID', 'auto');
        // ga('send', 'pageview');
    }

    // Disable cookies (remove or prevent non-essential cookies)
    function disableCookies() {
        // Disable analytics or other non-essential cookies
        // Example: Google Analytics opt-out
        // window['ga-disable-YOUR_TRACKING_ID'] = true;
    }
});