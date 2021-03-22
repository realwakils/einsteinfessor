function pasteToBox() {
    navigator.clipboard.readText()
        .then(clipText => {
            document.getElementById("contentForm").value = clipText;
            document.getElementById("formSubmitBtn").click();
        })
        .catch(err => {
            console.error('Failed to read clipboard contents: ', err);
            alert("Kunne ikke få data fra din udklipsholder (hvad du har kopieret)... Prøv igen eller prøv manuelt");
        });
}

$(document).ready(function() {
    $("body").tooltip({ selector: '[data-toggle=tooltip]' });
});

/* $(document).ready(function() {
    var width = document.getElementById('infobox').clientWidth;
    var wrapperBox = document.getElementById('wrapper_infobox');
    wrapperBox.style.width = width + 'px';
    setTimeout(updateWidth, 100);
});

function updateWidth() {
    var width = document.getElementById('infobox').clientWidth;
    var wrapperBox = document.getElementById('wrapper_infobox');
    wrapperBox.style.width = width + 'px';
    setTimeout(updateWidth, 20);
} */

function killBtn(el) {
    el.animate([
        { transform: 'translateY(0px)' },
        { transform: 'translateY(-999px)' }
    ], {
        duration: 500,
    });
    setTimeout(() => el.style.display = 'none', 200)
}