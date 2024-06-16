const dashContainer = document.getElementById('sequence_viewer');
// const dashAppUrl = '/gene/dash-gene-app/'; // Use the correct URL for your Dash app
const iframe = document.createElement('iframe');
// iframe.src = dashAppUrl;
iframe.width = '100%';
iframe.height = '600px'; // Adjust the height as needed
iframe.frameBorder = '0';
dashContainer.appendChild(iframe);
