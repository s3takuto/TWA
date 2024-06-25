var file;
var submit;
window.onload = function(){
    file = document.getElementById("fl");
    submit = document.getElementById("sb");
}

function fileUploaded(){
    if (file.files.length > 0){
        submit.disabled = false;
    }else{
        submit.disabled = true;
    }
}