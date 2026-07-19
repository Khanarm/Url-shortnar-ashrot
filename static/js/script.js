function copyLink(button){

    let link = document.getElementById("shortLink");

    navigator.clipboard.writeText(link.value);

    button.innerHTML = "✅ Copied!";


    setTimeout(function(){

        button.innerHTML = "📋 Copy";

    },2000);

}

function generateQR(){

    let link = document.getElementById("shortLink").value;

    let qrUrl = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=" 
                + encodeURIComponent(link);


    let qrBox = document.getElementById("qrCode");

    qrBox.innerHTML = `
        <img src="${qrUrl}" alt="QR Code">
    `;

}
