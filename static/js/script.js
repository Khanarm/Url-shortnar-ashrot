function copyLink(button){

    let link = document.getElementById("shortLink");

    navigator.clipboard.writeText(link.value);

    button.innerHTML = "✅ Copied!";


    setTimeout(function(){

        button.innerHTML = "📋 Copy";

    },2000);

}
