const PathArr = [xt, vxt, axt, yt, vyt, ayt];
const idArr = ['xt', 'vxt', 'axt', 'yt', 'vyt', 'ayt']

window.onload = function(){
    const canvases = document.querySelectorAll('canvas');
    canvases.forEach((canvas, index) => {
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.src = PathArr[index];
        img.onload = function(){
            const aspectRatio = parseFloat(img.height) / img.width;

            newWidth = parseInt(window.innerWidth * 0.3);
            newHeight = parseInt(newWidth*aspectRatio);

            canvas.width = newWidth;
            canvas.height = newHeight;
            ctx.drawImage(img, 0, 0, newWidth, newHeight);
        }
    });
}