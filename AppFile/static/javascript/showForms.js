const fArray = ["CF","LF","QF","CosF","SinF", "ELF"];
var mFormX, mFormY;
var selectX, selectY;

var leftX = "\\(x=";
var leftY = "\\(y=";
var rightFin = "\\)";

var CFForm = "a";
var LFForm = "at + b";
var QFForm = "at^2 + bt + c";
var CosFForm = "A \\cos \\left( \\omega t - \\phi \\right) + B";
var SinFForm = "A \\sin \\left( \\omega t - \\phi \\right) + B";
var ELFForm = "A e^{\\alpha t} + Bt + C";

var ffArray = [CFForm, LFForm, QFForm, CosFForm, SinFForm, ELFForm];

window.onload = function(){
    mFormX = document.getElementById("mFormX");
    mFormY = document.getElementById("mFormY");
    mFormX.innerHTML = leftX+CFForm+rightFin;
    mFormY.innerHTML = leftY+CFForm+rightFin;
    MathJax.Hub.Typeset(mFormX);
    MathJax.Hub.Typeset(mFormY);

    selectX = document.getElementById("selectX");
    selectY = document.getElementById("selectY");
}

function showFormX(){
    for (var i=0; i<fArray.length; i++){
        if(selectX.value == fArray[i]){
            mFormX.innerHTML = leftX + ffArray[i]+rightFin;
            MathJax.Hub.Typeset(mFormX);
        }
    }    
}
function showFormY(){
    for (var i=0; i<fArray.length; i++){
        if(selectY.value == fArray[i]){
            mFormY.innerHTML = leftY + ffArray[i]+rightFin;
            MathJax.Hub.Typeset(mFormY);
        }
    }
}