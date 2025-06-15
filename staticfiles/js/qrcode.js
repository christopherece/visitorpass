// QR Code Generator
function generateQRCode() {
    // Ensure QRCode library is loaded
    if (typeof QRCode === 'undefined') {
        console.error('QRCode library not loaded');
        return;
    }

    const qrContainer = document.getElementById('qr-container');
    if (!qrContainer) {
        console.error('QR container not found');
        return;
    }

    // Clear any existing QR code
    qrContainer.innerHTML = '';

    // Create QR code
    const qr = new QRCode(qrContainer, {
        text: window.location.href,
        width: 80,
        height: 80,
        colorDark: '#ffffff',
        colorLight: '#007bff',
        correctLevel: QRCode.CorrectLevel.H
    });

    // Ensure the container is visible
    qrContainer.style.display = 'block';
}

// Initialize QR code when the page loads
document.addEventListener('DOMContentLoaded', function() {
    generateQRCode();
});

// Also try generating on window load in case of timing issues
window.addEventListener('load', function() {
    generateQRCode();
});
