function copyLink(){

    let link = document.getElementById("shortLink");
    let button = event.target;

    navigator.clipboard.writeText(link.value);

    button.innerHTML = "✅ Copied!";

    setTimeout(()=>{

        button.innerHTML = "📋 Copy";

    },2000);

}
