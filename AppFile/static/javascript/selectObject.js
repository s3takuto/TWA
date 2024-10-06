var canvas, ctx, img;
var length, XIP, YIP;
var submitButton;
var baseFlag = trackFlag = false;
var selectBaseFlag = selectTrackFlag = false;
var textBoxFlag = false;
var lineFlag = false;
var line_sx = line_sy = line_ex = line_ey = -1;
var rectFlag = false;
var rect_sx = rect_sy = rect_ex = rect_ey = -1;

function checkRadio(){
    if (document.selectMode.mode[0].checked){
        selectBaseFlag = true;
        selectTrackFlag = false;
    }else if (document.selectMode.mode[1].checked){
        selectBaseFlag = false;
        selectTrackFlag = true;
    }
}
window.onload = function () {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    img = new Image();
    img.src = imagePath;
    img.onload = function(){
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        //RGB(99,237,1) 黄緑色
        ctx.strokeStyle = 'rgb('+99+','+237+','+1+')';
        ctx.lineWidth = 2;
    }
    length = document.getElementById("length");
    XIP = document.getElementById("XIP");
    YIP = document.getElementById("YIP");
    submitButton = document.getElementById("decision");
}
function OnMousedown(event){
    if (selectBaseFlag){
        lineFlag = true;
        rectFlag = false;
        var line = event.target.getBoundingClientRect();
        line_sx = line_ex = event.clientX - line.left;
        line_sy = line_ey = event.clientY - line.top;
    }else if (selectTrackFlag){
        rectFlag = true;
        lineFlag = false;
        var rect = event.target.getBoundingClientRect();
        rect_sx = rect_ex = event.clientX - rect.left;
        rect_sy = rect_ey = event.clientY - rect.top;
    }
}
function draw(str){
    if (str == "line"){
        ctx.moveTo(line_sx, line_sy);
        ctx.lineTo(line_ex, line_ey);
    }else if (str == "rect"){
        ctx.moveTo(rect_sx, rect_sy);
        ctx.lineTo(rect_ex, rect_sy);
        ctx.moveTo(rect_sx, rect_ey);
        ctx.lineTo(rect_ex, rect_ey);
        ctx.moveTo(rect_ex, rect_sy);
        ctx.lineTo(rect_ex, rect_ey);
        ctx.moveTo(rect_sx, rect_sy);
        ctx.lineTo(rect_sx, rect_ey);
    }
}
function OnMousemove(event){
        if (lineFlag){
        var line = event.target.getBoundingClientRect();
        line_ex = event.clientX - line.left;
        line_ey = event.clientY - line.top;
        ctx.drawImage(img, 0, 0);
        ctx.beginPath();
        draw("line");
        if (trackFlag){
            draw("rect")
        }
        ctx.stroke();
    }else if (rectFlag){
        var rect = event.target.getBoundingClientRect();
        rect_ex = event.clientX - rect.left;
        rect_ey = event.clientY - rect.top;
        ctx.drawImage(img, 0, 0);
        ctx.beginPath();
        draw("rect");
        if (baseFlag){
            draw("line");
        }
        ctx.stroke();
    }
}
function canselDisabled(){
    if (baseFlag && trackFlag && textBoxFlag){
        submitButton.disabled = false;
    }else{
        submitButton.disabled = true;
    }
}
function OnMouseup(event){
    if (lineFlag){
        baseFlag = true;
        lineFlag = false;
        var line_params = {
            line_sx : line_sx, 
            line_sy : line_sy, 
            line_ex : line_ex, 
            line_ey : line_ey
        };
        fetch("/setPoint", {
            method : "POST", 
            headers : {
                "Content-Type" : "application/json", 
            }, 
            body: JSON.stringify({
                type : "line",
                params : line_params
            }), 
        })
        .catch(error => {
            console.error("Error: ", error);
        });
    }else if (rectFlag){
        trackFlag = true;
        rectFlag = false;
        var left, top, width, height;
        if (rect_sx < rect_ex){
            left = rect_sx;
            width = rect_ex - rect_sx;
        }else{
            left = rect_ex;
            width = rect_sx - rect_ex;
        }
        if (rect_sy < rect_ey){
            top = rect_sy;
            height = rect_ey - rect_sy;
        }else{
            top = rect_ey;
            height = rect_sy - rect_ey;
        }
        var rect_params = {
            left : left,  
            top : top, 
            width : width, 
            height : height
        };
        fetch("/setPoint", {
            method : "POST", 
            headers : {
                "Content-Type" : "application/json", 
            }, 
            body: JSON.stringify({
                type : "rect",
                params : rect_params
            }), 
        })
        .catch(error => {
            console.error("Error: ", error);
        });
    }
    canselDisabled();
}
function check(){
    if (length.value.trim()!="" && XIP.value.trim()!="" && YIP.value.trim()!=""){
        textBoxFlag = true;
    }else{
        textBoxFlag = false;
    }
    canselDisabled();
}