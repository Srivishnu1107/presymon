const avatar = document.getElementById("aiAvatar");
const panel  = document.getElementById("aiPanel");
const msgs   = document.getElementById("aiMessages");


/* ⚡ OPEN / CLOSE */

avatar.onclick = ()=> panel.style.display="flex";
document.getElementById("closeAI").onclick =
  ()=> panel.style.display="none";


/* 🧲 DRAG ANYWHERE */

let drag=false, x=0, y=0;

avatar.onmousedown=e=>{
  drag=true;
  x=e.clientX-avatar.offsetLeft;
  y=e.clientY-avatar.offsetTop;
};

document.onmouseup=()=>drag=false;

document.onmousemove=e=>{
  if(!drag) return;
  avatar.style.left=e.clientX-x+"px";
  avatar.style.top=e.clientY-y+"px";
  avatar.style.right="auto";
  avatar.style.bottom="auto";
};


/* 💬 SEND TEXT */

function sendAI(){

  const input=document.getElementById("aiInput");
  const text=input.value.trim();
  if(!text) return;

  addMsg(text,"userMsg");
  input.value="";

  fetch("/ai_chat",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({q:text})
  })
  .then(r=>r.json())
  .then(d=>{
    addMsg(d.reply,"botMsg");
    speak(d.reply);
  });
}


/* 🗣 VOICE INPUT */

function startVoice(){

  const recog = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

  recog.onresult = e=>{
    const text = e.results[0][0].transcript;
    document.getElementById("aiInput").value = text;
    sendAI();
  };

  recog.start();
}


/* 🔊 VOICE OUTPUT */

function speak(text){
  const u = new SpeechSynthesisUtterance(text);
  u.rate = 1;
  u.pitch = 1.1;
  speechSynthesis.speak(u);
}


/* 🧩 ADD MESSAGE */

function addMsg(t,cls){
  const div=document.createElement("div");
  div.className=cls;
  div.innerText=t;
  msgs.appendChild(div);
  msgs.scrollTop=msgs.scrollHeight;
}


/* 🚨 SYSTEM GUARDIAN MODE */

setInterval(()=>{

  fetch("/live")
  .then(r=>r.json())
  .then(d=>{

    if(d.cpu>90){
      const msg="⚠ Critical CPU usage detected";
      addMsg(msg,"botMsg");
      speak(msg);
    }

    if(d.disk>90){
      const msg="⚠ Disk space dangerously low";
      addMsg(msg,"botMsg");
      speak(msg);
    }

  });

},20000);