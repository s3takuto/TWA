var svideo, evideo;
var sfNum, efNum;

window.onload = function(){
    svideo = document.getElementById("sframe");
    evideo = document.getElementById("eframe");

    sfNum = document.getElementById("sfNum");
    efNum = document.getElementById("efNum");

    ERshift();
}

function SLshift(n){
    num = Number(n);
    sfNum.stepDown(num);
    svideo.currentTime = (sfNum.value-1) / FPS;
}

function SRshift(n){
    num = Number(n);
    if (parseInt(sfNum.value)+num < parseInt(efNum.value)){
        sfNum.stepUp(num);
        svideo.currentTime = (sfNum.value-1)/FPS;
    }
}

function ELshift(n){
    num = Number(n);
    if (parseInt(sfNum.value) < parseInt(efNum.value)-num){
        efNum.stepDown(num);
        evideo.currentTime = (efNum.value-1)/FPS;
    }
}

function ERshift(n){
    num = Number(n);
    efNum.stepUp(num);
    evideo.currentTime = (efNum.value-1)/FPS;
}

function cancelDisabled(){
    sfNum.disabled = false;
    efNum.disabled = false;
}