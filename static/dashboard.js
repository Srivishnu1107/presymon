function chart(id,label,color){
    return new Chart(document.getElementById(id),{
        type:'line',
        data:{
            labels:Array(20).fill(""),
            datasets:[{
                label:label,
                data:[],
                borderColor:color,
                tension:0.4,   // 🔥 smooth curve
                borderWidth:3,
                pointRadius:0
            }]
        },
        options:{
            responsive:true,
            plugins:{legend:{display:false}},
            scales:{y:{min:0,max:100}}
        }
    });
}

const cpu = chart("cpu","CPU","#00e5ff");
const ram = chart("ram","RAM","#7cff6b");
const disk = chart("disk","Disk","#ffd166");
const gpu = chart("gpu","GPU","#ff6bff");


setInterval(()=>{
    fetch("/live").then(r=>r.json()).then(d=>{
        const vals=[d.cpu,d.ram,d.disk,d.gpu];
        [cpu,ram,disk,gpu].forEach((c,i)=>{
            c.data.datasets[0].data.push(vals[i]);
            if(c.data.datasets[0].data.length>20)
                c.data.datasets[0].data.shift();
            c.update();
        });
    });
},1000);


setInterval(()=>{
    fetch("/ai").then(r=>r.json()).then(d=>{
        document.getElementById("aiBox").innerText=d.tip;
    });
},10000);


fetch("/forecast").then(r=>r.json()).then(data=>{
    const box=document.getElementById("days");

    data.forEach((v,i)=>{
        let c="green";
        if(v>80)c="red";
        else if(v>60)c="yellow";

        box.innerHTML+=`<div class="day ${c}">${i+1}</div>`;
    });
});