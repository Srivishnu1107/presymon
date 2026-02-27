const box = document.getElementById("notifications");
const tipBox = document.getElementById("tip");

/* -------------------------
   Notifications every 5s
--------------------------*/
async function getLive(){

    const r = await fetch("/live");
    const d = await r.json();

    let level="green";
    let msg="System Healthy";

    if(d.cpu>80 || d.ram>80 || d.disk>85){
        level="red";
        msg="⚠ High Usage Detected";
    }
    else if(d.cpu>60){
        level="yellow";
        msg="Moderate Load";
    }

    const div=document.createElement("div");
    div.className="note "+level;
    div.innerText =
        new Date().toLocaleTimeString() +
        " | CPU:"+d.cpu+"%  RAM:"+d.ram+"%  Disk:"+d.disk+"%  → "+msg;

    box.prepend(div);

    if(box.children.length>20)
        box.removeChild(box.lastChild);
}


/* -------------------------
   AI suggestions every 10s
--------------------------*/
async function getTip(){
    const r = await fetch("/ai_tip");
    const t = await r.text();
    tipBox.innerText=t;
}


/* -------------------------
   30 day forecast grid
--------------------------*/
function buildForecast(){

    const f=document.getElementById("forecast");

    for(let i=1;i<=30;i++){

        const val=Math.random()*100;

        const d=document.createElement("div");
        d.innerText=i;

        if(val<40) d.className="day green";
        else if(val<70) d.className="day yellow";
        else d.className="day red";

        d.onclick=()=>window.location="/day/"+i;

        f.appendChild(d);
    }
}


/* -------------------------
   PDF
--------------------------*/
function downloadReport(){
    window.location="/report";
}


/* Start */
setInterval(getLive,5000);
setInterval(getTip,10000);
buildForecast();