#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-19 网页版候选决策页：与决策组件同源（pending_candidates.json），静态托管 hstender.cn/decide.html。
手机浏览器打开→点选→生成决策指令→一键复制→粘贴到 Kimi 项目对话执行。零服务端、零凭据。
由每次 safe_deploy 前手动/管线调用刷新；部署范围由 safe_deploy.sh git add 纳入。

11-19 登录界面改版：抄金融IT厂商中标看板登录作业（周老师钦定，以后同类外网加密登录页一律按此模板）——
深色渐变门禁背景 + 白卡（右上个人签章 seal.gif dataURI）+ 姓名/密码双字段（别名 周红青=周老师）+
同一设备 30 分钟免密会话（localStorage 存 DEK+时间戳）+ 连错 3 次出提示与「重置密码」按钮（静态页，
重置=联系管理员在会话中一句话重置 .decide_pwd 后重建部署）。

11-20 改版（周老师 00:31 三点意见落地）：
① 决策本体 UI 对齐侧栏「标讯候选决策」组件（refresh_board_widgets.py 同源）：桌面表格交互
   编号|招标单位/项目|预算|投标截止|业务标签|投标建议|决策（chips），不再用手机卡片式；
② 修复 30 分钟免密失效真 bug：原实现 dek 存 base64、恢复时按 hex 解析（ab 函数），
   必然解密失败→每次都要输密码。改为存 hex（hexE），与 ab 解析一致；
③ 窄屏（手机）表格横向滚动，交互与桌面一致。"""
import json, datetime, base64
from pathlib import Path

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
OUT = BIDDING / "decide.html"
SEAL = BIDDING / "gate" / "seal.gif"   # 11-19 个人签章（与厂商看板同源 seal.gif 的本地副本）

PWD_FILE = BIDDING / ".decide_pwd"

def load_pwd():
    if PWD_FILE.exists():
        return PWD_FILE.read_text().strip()
    return ""

APP_CSS = r'''
  /* ===== 决策应用本体（11-20 对齐侧栏组件表格交互） ===== */
  #app { display:none; padding:16px; max-width:1120px; margin:0 auto; }
  .head { display:flex; justify-content:space-between; align-items:baseline; margin:4px 2px 12px; flex-wrap:wrap; gap:4px; }
  h1.a { font-size:18px; }
  .meta { font-size:12px; color:#888; }
  .tip { font-size:12px; color:#999; margin:0 2px 12px; line-height:1.7; }
  .tbl-wrap { overflow-x:auto; -webkit-overflow-scrolling:touch; }
  table.dl { width:100%; border-collapse:collapse; font-size:13px; background:#fff; }
  table.dl th, table.dl td { text-align:left; padding:8px 10px; border-bottom:1px solid #eceff3; vertical-align:top; }
  table.dl th { font-size:11.5px; color:#8a94a6; font-weight:500; white-space:nowrap; background:#fafbfc; }
  table.dl td.num { color:#8a94a6; text-align:center; white-space:nowrap; }
  table.dl td.kv { white-space:nowrap; font-variant-numeric:tabular-nums; }
  .co { font-weight:600; font-size:13px; }
  .pj { font-size:12px; color:#666; margin-top:3px; line-height:1.5; }
  .tag-in, .rec-sel { width:100%; box-sizing:border-box; padding:6px 8px; font-size:12.5px; border:1px solid #dfe5ee; border-radius:7px; background:#fbfcfe; color:#1b2433; outline:none; font-family:inherit; min-width:90px; }
  .tag-in:focus, .rec-sel:focus { border-color:#0b5cad; background:#fff; }
  .tag-in.bad { border-color:#d5483f; }
  .tag-err { font-size:11px; color:#d5483f; margin-top:3px; }
  .rec-seg { display:flex; gap:6px; }
  .chip { flex:1; padding:6px 0; font-size:12.5px; border-radius:7px; border:1px solid #dfe5ee; background:#fafafa; color:#666; cursor:pointer; white-space:nowrap; font-family:inherit; min-width:56px; }
  .chip.pos[aria-pressed="true"] { background:#2f6fed; color:#fff; border-color:#2f6fed; }
  .chip.neg[aria-pressed="true"] { background:#d5483f; color:#fff; border-color:#d5483f; }
  .empty { text-align:center; color:#888; padding:40px 0; font-size:14px; }
  .foot { position:sticky; bottom:0; background:#f6f7f9; padding:10px 0 16px; }
  .gen { width:100%; padding:14px 0; font-size:16px; font-weight:600; border:none; border-radius:10px; background:#2f6fed; color:#fff; cursor:pointer; }
  .gen:disabled { opacity:.5; }
  .copybtn { width:100%; margin-top:8px; padding:10px 0; font-size:14px; font-weight:600; border:1px solid #2f6fed; border-radius:10px; background:#fff; color:#2f6fed; cursor:pointer; }
  .stat { text-align:center; font-size:12px; color:#888; margin-top:8px; }
  .msg { font-size:13px; margin-top:8px; line-height:1.6; }
  .msg.ok { color:#2e9e5b; } .msg.err { color:#d5483f; }
  textarea { width:100%; height:90px; margin-top:10px; padding:8px; font-size:13px; border:1px solid #ddd; border-radius:8px; box-sizing:border-box; }
'''

APP_HTML = r'''
<div class="head"><h1 class="a">标讯候选决策</h1><span class="meta" id="batch"></span></div>
<div class="tip">点选「纳入 / 不纳入」（本机自动保存，刷新不丢）→ 底部生成决策指令 → 一键复制 → 粘贴到 Kimi「银信标讯」项目对话发送即执行。</div>
<div class="tbl-wrap"><table class="dl"><thead><tr>
  <th style="width:44px">编号</th><th>招标单位 / 项目</th><th style="width:76px">预算</th>
  <th style="width:96px">投标截止</th><th style="width:150px">业务标签</th>
  <th style="width:118px">投标建议</th><th style="width:132px">决策</th>
</tr></thead><tbody id="body"></tbody></table></div>
<div class="foot">
  <button class="gen" id="gen">生成决策指令并复制</button>
  <div class="stat" id="stat"></div>
  <div class="msg" id="msg"></div>
  <textarea id="out" readonly style="display:none"></textarea>
  <button class="copybtn" id="copybtn" style="display:none">📋 复制指令</button>
</div>
'''

APP_JS = r'''
function start(DATA){
  document.getElementById('app').style.display='block';
  var VALID=DATA.valid_tags||[];
  var decisions={};
  var $=function(id){return document.getElementById(id)};
  $('batch').textContent=DATA.batch+' 批次 · '+DATA.items.length+' 条候选';

  function esc(x){return String(x==null?'':x).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function defaults(){var d={};DATA.items.forEach(function(it){d[it.push_no]={decision:null,tags:it.tags,rec:it.rec}});return d}
  var KEY='decide-'+DATA.batch;
  function persist(){try{localStorage.setItem(KEY,JSON.stringify(decisions))}catch(e){}}
  function restore(){try{var v=localStorage.getItem(KEY);if(v){decisions=JSON.parse(v);return}}catch(e){}decisions=defaults()}
  function splitTags(s){return String(s||'').split(/[,，、;；\s]+/).map(function(t){return t.trim()}).filter(Boolean)}
  function tagError(s){var ts=splitTags(s);if(ts.length>3)return '最多3个标签';for(var i=0;i<ts.length;i++){if(VALID.length&&VALID.indexOf(ts[i])<0)return '「'+ts[i]+'」不在标签库'}return ''}
  function stat(){var n=Object.keys(decisions).filter(function(k){return decisions[k].decision}).length;$('stat').textContent='已决 '+n+' / '+DATA.items.length+' 条（本机自动保存）'}
  function render(){
    var B=$('body');
    if(!DATA.items.length){B.parentNode.parentNode.innerHTML='<div class="empty">本批次暂无待确认候选</div>';stat();return}
    var dl='<datalist id="taglib">'+VALID.map(function(t){return '<option value="'+esc(t)+'">'}).join('')+'</datalist>';
    var h='';
    DATA.items.forEach(function(it){
      var d=decisions[it.push_no]||(decisions[it.push_no]={decision:null,tags:it.tags,rec:it.rec});
      var te=tagError(d.tags);
      h+='<tr>'
        +'<td class="num">'+it.push_no+'</td>'
        +'<td><div class="co">'+esc(it.company)+'</div><div class="pj">'+esc(it.project)+'</div></td>'
        +'<td class="kv">'+esc(it.budget)+'</td>'
        +'<td class="kv">'+esc(it.deadline)+'</td>'
        +'<td><input list="taglib" class="tag-in'+(te?' bad':'')+'" data-no="'+it.push_no+'" value="'+esc(d.tags)+'" placeholder="最多3个，逗号分隔"/>'
        +(te?'<div class="tag-err">'+esc(te)+'</div>':'')+'</td>'
        +'<td><select class="rec-sel" data-no="'+it.push_no+'">'
        +['强烈建议投标','建议投标','可关注'].map(function(r){return '<option'+(r===d.rec?' selected':'')+'>'+r+'</option>'}).join('')
        +'</select></td>'
        +'<td><div class="rec-seg">'
        +'<button type="button" class="chip pos" data-no="'+it.push_no+'" data-v="纳入" aria-pressed="'+(d.decision==='纳入')+'">纳入</button>'
        +'<button type="button" class="chip neg" data-no="'+it.push_no+'" data-v="不纳入" aria-pressed="'+(d.decision==='不纳入')+'">不纳入</button>'
        +'</div></td></tr>';
    });
    B.innerHTML=dl+h;
    B.querySelectorAll('.chip').forEach(function(c){
      c.addEventListener('click',function(){
        var no=+c.dataset.no;
        decisions[no].decision=(decisions[no].decision===c.dataset.v)?null:c.dataset.v;
        persist();stat();
        c.closest('tr').querySelectorAll('.chip').forEach(function(x){
          x.setAttribute('aria-pressed',decisions[no].decision===x.dataset.v?'true':'false');
        });
      });
    });
    B.querySelectorAll('.tag-in').forEach(function(t){
      t.addEventListener('input',function(){decisions[+t.dataset.no].tags=t.value;persist()});
      t.addEventListener('change',function(){decisions[+t.dataset.no].tags=t.value.trim();persist();render()});
      t.addEventListener('blur',function(){render()});
    });
    B.querySelectorAll('.rec-sel').forEach(function(sel){
      sel.addEventListener('change',function(){decisions[+sel.dataset.no].rec=sel.value;persist()});
    });
    stat();
  }
  $('gen').addEventListener('click',function(){
    var parts=[],errs=[];
    DATA.items.forEach(function(it){
      var d=decisions[it.push_no];if(!d||!d.decision)return;
      var te=tagError(d.tags);
      if(te){errs.push('第'+it.push_no+'行 '+it.company+'：'+te);return}
      var s=it.push_no+(d.decision==='纳入'?'纳入':'不纳入');
      var ts=splitTags(d.tags),orig=splitTags(it.tags);
      if(ts.join()!==orig.join())s+='（标签：'+ts.join('、')+'）';
      if(d.rec!==it.rec)s+='（建议：'+d.rec+'）';
      parts.push(s);
    });
    if(errs.length){$('msg').className='msg err';$('msg').innerHTML=errs.join('<br/>');return}
    if(!parts.length){$('msg').className='msg err';$('msg').textContent='请先点选至少一条';return}
    var txt='【候选决策 '+DATA.batch+'】'+parts.join('；');
    $('out').style.display='block';$('out').value=txt;$('copybtn').style.display='block';
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(function(){
        $('msg').className='msg ok';$('msg').textContent='已复制 '+parts.length+' 条决策指令，请到 Kimi「银信标讯」项目对话粘贴发送';
      },function(){$('msg').className='msg ok';$('msg').textContent='复制失败，请长按上方文本框手动复制'});
    }else{$('msg').className='msg ok';$('msg').textContent='请长按上方文本框手动复制后发送到 Kimi 对话'}
  });
  $('copybtn').addEventListener('click',function(){
    var txt=$('out').value;
    if(!txt){$('msg').className='msg err';$('msg').textContent='请先生成决策指令';return}
    function okMsg(m){$('msg').className='msg ok';$('msg').textContent=m}
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(function(){okMsg('已复制，请到 Kimi「银信标讯」项目对话粘贴发送')},function(){
        $('out').select();document.execCommand&&document.execCommand('copy');okMsg('已复制（兼容模式），请到 Kimi 对话粘贴发送');
      });
    }else{$('out').select();document.execCommand&&document.execCommand('copy');okMsg('已复制（兼容模式），请到 Kimi 对话粘贴发送')}
  });
  restore();render();
}
'''

GATE_JS = r'''
(function(){
  var BLOB=JSON.parse(document.getElementById('blob').textContent);
  /* ===== 11-19 登录门禁（厂商看板同款作业；11-20 修复免密：dek 统一 hex 编解码） ===== */
  var SEAL_URI = /*__SEAL__*/'';
  var GRACE_KEY = 'decide_gate_grace_v1', GRACE_MS = 30 * 60 * 1000;   // 同一设备 30 分钟免密会话
  var NAME_KEY = 'decide_gate_name_v1';
  var ALIAS = {'周红青':'周老师'};          // 姓名别名（与厂商看板口径一致）
  var ALLOWED = ['周老师'];
  var __fails = 0, __busy = false;
  function esc(x){return String(x==null?'':x).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function ab(h){var a=new Uint8Array(h.length/2);for(var i=0;i<a.length;i++)a[i]=parseInt(h.substr(i*2,2),16);return a;}
  function hexE(buf){var u8=new Uint8Array(buf),s='';for(var i=0;i<u8.length;i++){s+=('0'+u8[i].toString(16)).slice(-2);}return s;}
  function pbkdf2(pwd,salt,iter){
    var enc=new TextEncoder();
    return crypto.subtle.importKey('raw',enc.encode(pwd),'PBKDF2',false,['deriveKey']).then(function(k){
      return crypto.subtle.deriveKey({name:'PBKDF2',salt:salt,iterations:iter,hash:'SHA-256'},k,{name:'AES-GCM',length:256},false,['decrypt']);
    });
  }
  function gateShow(html){var g=document.getElementById('gate');g.innerHTML=html;g.classList.remove('hide');g.style.display='flex';}
  function gateHide(){var g=document.getElementById('gate');g.classList.add('hide');setTimeout(function(){g.style.display='none'},250);}
  function decryptData(dekBuf){
    return crypto.subtle.importKey('raw',dekBuf,'AES-GCM',false,['decrypt']).then(function(k){
      return crypto.subtle.decrypt({name:'AES-GCM',iv:ab(BLOB.iv)},k,ab(BLOB.ct));
    }).then(function(pt){return JSON.parse(new TextDecoder().decode(pt));});
  }
  /* 30 分钟免密：本机会话记忆（DEK+时间戳，过期/解密失败即回落密码常态） */
  function gateBoot(){
    try{
      var g=JSON.parse(localStorage.getItem(GRACE_KEY)||'null');
      if(g&&g.dek&&(Date.now()-g.t)<GRACE_MS){
        decryptData(ab(g.dek)).then(function(DATA){gateHide();start(DATA);}).catch(function(){
          localStorage.removeItem(GRACE_KEY);gateLock();
        });
        return;
      }
      localStorage.removeItem(GRACE_KEY);
    }catch(e){}
    gateLock();
  }
  function gateLock(){
    var lastName='';
    try{lastName=localStorage.getItem(NAME_KEY)||'';}catch(e){}
    gateShow('<div class="gate-card" id="gCard">'
      +(SEAL_URI?'<img class="gseal" src="'+SEAL_URI+'" alt="" aria-hidden="true">':'')
      +'<div class="gico">🔐</div>'
      +'<h2>标讯候选决策</h2>'
      +'<div class="gsub">授权访问 · 银信标讯看板</div>'
      +'<div class="gfield"><label>姓名</label><input id="gName" type="text" placeholder="请输入姓名" autocomplete="username" value="'+esc(lastName)+'"></div>'
      +'<div class="gfield"><label>访问密码</label><input id="gPwd" type="password" placeholder="请输入访问密码" autocomplete="current-password"></div>'
      +'<button type="button" id="gLogin" class="gbtn">登 录</button>'
      +'<div class="gerr" id="gErr"></div>'
      +'<div id="gExtra"></div>'
      +'<div class="gprog" id="gProg" style="display:none"><span class="spinner"></span>验证中…</div>'
      +'</div>');
    var nameEl=document.getElementById('gName'),pwdEl=document.getElementById('gPwd');
    var go=function(){
      if(__busy)return;
      if(!nameEl.value.trim()){nameEl.focus();return;}
      if(!pwdEl.value){pwdEl.focus();return;}
      tryUnlock(nameEl.value.trim(),pwdEl.value);
    };
    [nameEl,pwdEl].forEach(function(el){el.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();go();}});});
    document.getElementById('gLogin').addEventListener('click',go);
    [nameEl,pwdEl].forEach(function(el){el.addEventListener('input',function(){
      var e2=document.getElementById('gErr');if(e2)e2.textContent='';
    });});
    pwdEl.focus();
  }
  function failUnlock(msg){
    __fails++;__busy=false;
    document.getElementById('gProg').style.display='none';
    document.getElementById('gName').disabled=false;
    var pe=document.getElementById('gPwd');pe.disabled=false;
    document.getElementById('gErr').textContent=msg;
    var card=document.getElementById('gCard');card.classList.remove('shake');void card.offsetWidth;card.classList.add('shake');
    if(__fails>=3){
      document.getElementById('gExtra').innerHTML='<div class="ghint">已连续输错 '+__fails
        +' 次，请核对姓名与密码（注意大小写）。<br/>如遗忘密码，点下方「重置密码」。</div>'
        +'<button type="button" class="greset" id="gReset">重置密码</button>';
      document.getElementById('gReset').addEventListener('click',function(){
        document.getElementById('gExtra').innerHTML='<div class="ghint">密码重置请联系看板管理员（在 Kimi 会话中说一句话即可重置）；重置后重新打开本页，使用新密码登录。</div>';
      });
    }
    pe.focus();pe.setSelectionRange(pe.value.length,pe.value.length);
  }
  function tryUnlock(name,pwd){
    __busy=true;
    document.getElementById('gErr').textContent='';
    document.getElementById('gProg').style.display='';
    document.getElementById('gName').disabled=true;
    document.getElementById('gPwd').disabled=true;
    var realName=ALIAS[name]||name;
    if(ALLOWED.indexOf(realName)<0){failUnlock('姓名未授权');return;}
    pbkdf2(pwd,ab(BLOB.salt),BLOB.iter).then(function(kek){
      return crypto.subtle.decrypt({name:'AES-GCM',iv:ab(BLOB.wiv)},kek,ab(BLOB.wct));
    }).then(function(dek){
      try{localStorage.setItem(NAME_KEY,name);}catch(e){}
      try{localStorage.setItem(GRACE_KEY,JSON.stringify({t:Date.now(),dek:hexE(dek)}));}catch(e){}  // 免密会话起算（hex，与 ab 解析一致）
      return decryptData(dek);
    }).then(function(DATA){
      gateHide();start(DATA);
    }).catch(function(){
      failUnlock('姓名或密码不正确');
    });
  }
  document.addEventListener('DOMContentLoaded',gateBoot);
'''

GATE_CSS = r'''
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
  body { font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:#f6f7f9; color:#1a1a1a; }
  /* ===== 11-19 登录门禁：抄金融IT厂商中标看板登录作业（周老师钦定模板） ===== */
  :root { --accent:#0b5cad; --ink:#1b2433; --ink2:#46536a; --ink3:#8a94a6; --line:#dfe5ee; }
  #gate { position:fixed; inset:0; z-index:100; background:radial-gradient(1200px 600px at 20% -10%,#16345e 0%,#0d1f3a 55%,#0a1830 100%); display:flex; align-items:center; justify-content:center; padding:20px; }
  #gate.hide { opacity:0; transition:opacity .25s; }
  .gate-card { position:relative; background:rgba(255,255,255,.97); border-radius:18px; box-shadow:0 24px 80px rgba(0,0,0,.45); width:400px; max-width:100%; padding:34px 30px 28px; text-align:center; }
  .gate-card .gseal { position:absolute; top:14px; right:14px; width:56px; transform:rotate(-8deg); opacity:.92; pointer-events:none; filter:drop-shadow(0 1px 3px rgba(160,30,30,.22)); }
  .gate-card .gico { width:56px; height:56px; margin:0 auto 16px; border-radius:16px; background:linear-gradient(135deg,#0b5cad,#123a6d); display:flex; align-items:center; justify-content:center; font-size:26px; }
  .gate-card h2 { font-size:17px; font-weight:700; }
  .gate-card .gsub { font-size:12px; color:var(--ink3); margin-top:6px; }
  .gate-card .gfield { margin-top:14px; text-align:left; }
  .gate-card .gfield label { display:block; font-size:11.5px; color:var(--ink3); margin-bottom:5px; letter-spacing:.05em; }
  .gate-card .gfield input { width:100%; box-sizing:border-box; padding:10px 12px; border:1px solid var(--line); border-radius:9px; font-size:14px; background:#fbfcfe; color:var(--ink); outline:none; transition:border-color .15s, box-shadow .15s; text-align:center; }
  .gate-card .gfield input:focus { border-color:var(--accent); box-shadow:0 0 0 3px rgba(11,92,173,.12); background:#fff; }
  .gate-card .gfield input:disabled { opacity:.6; }
  .gate-card .gbtn { width:100%; margin-top:18px; padding:11px; border:none; border-radius:10px; background:var(--accent); color:#fff; font-size:14px; font-weight:700; cursor:pointer; }
  .gate-card .gbtn:disabled { opacity:.6; cursor:wait; }
  .gate-card .gerr { color:#c0392b; font-size:12px; margin-top:8px; min-height:16px; }
  .gate-card .ghint { margin-top:10px; font-size:12px; color:#8a6d1a; background:#fff8e6; border:1px solid #ecd9a0; border-radius:8px; padding:7px 10px; text-align:left; line-height:1.6; }
  .gate-card .greset { margin-top:8px; width:100%; padding:8px; border:1px solid var(--line); border-radius:9px; background:#fff; font-size:12.5px; color:var(--ink2); cursor:pointer; }
  .gate-card .greset:hover { border-color:var(--accent); color:var(--accent); }
  .gate-card .gprog { display:flex; align-items:center; justify-content:center; gap:7px; margin-top:14px; font-size:12.5px; color:var(--ink2); }
  .gate-card .gprog .spinner { width:14px; height:14px; border:2px solid var(--line); border-top-color:var(--accent); border-radius:50%; animation:gspin .7s linear infinite; }
  @keyframes gspin { to { transform:rotate(360deg); } }
  .shake { animation:shake .4s; }
  @keyframes shake { 0%,100% { transform:translateX(0); } 25% { transform:translateX(-7px); } 75% { transform:translateX(7px); } }
'''

GATE_HTML = r'''
<div id="gate"></div>
<div id="app">
__APP_HTML__
</div>
<script type="application/json" id="blob">__BLOB__</script>
<script>
__GATE_JS__
__APP_JS__
})();
</script>
'''

OPEN_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex,nofollow,noarchive"/>
<title>标讯候选决策 · 银信标讯看板</title>
<style>__APP_CSS__</style>
</head>
<body>
__APP_HTML__
<script type="application/json" id="cand-data">__DATA__</script>
<script>
(function(){
  var DATA=JSON.parse(document.getElementById('cand-data').textContent);
__APP_JS__
})();
</script>
</body>
</html>'''

GATED_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<meta name="robots" content="noindex,nofollow,noarchive"/>
<title>标讯候选决策 · 银信标讯看板</title>
<style>__GATE_CSS____APP_CSS__</style>
</head>
<body>
__GATE_HTML__
</body>
</html>'''


def main():
    batch = datetime.date.today().isoformat()
    items = []
    p = BIDDING / "pending_candidates.json"
    if p.exists():
        for e in json.loads(p.read_text(encoding="utf-8")):
            if e.get("status") == "待确认":
                items.append({"push_no": e.get("push_no"), "company": e.get("company", ""),
                              "project": e.get("project", ""), "budget": e.get("budget", "-"),
                              "deadline": e.get("deadline", ""), "tags": e.get("tags", ""),
                              "rec": e.get("rec", "可关注")})
    try:
        import importlib.util as vu
        vs = vu.spec_from_file_location("cfg", str(BIDDING / "config.py"))
        vm = vu.module_from_spec(vs); vs.loader.exec_module(vm)
        valid = sorted(getattr(vm, "VALID_TAGS", []))
    except Exception:
        valid = []
    data = json.dumps({"batch": batch, "items": items, "valid_tags": valid}, ensure_ascii=False)
    pwd = load_pwd()
    if pwd:
        import os, hashlib
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        ITER = 310000
        dek = os.urandom(32); salt = os.urandom(16)
        kek = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, ITER, dklen=32)
        iv = os.urandom(12)
        ct = AESGCM(dek).encrypt(iv, data.encode(), None)
        wiv = os.urandom(12)
        wct = AESGCM(kek).encrypt(wiv, dek, None)
        blob = {"v":1,"iter":ITER,"salt":salt.hex(),"iv":iv.hex(),"ct":ct.hex(),"wiv":wiv.hex(),"wct":wct.hex()}
        payload = json.dumps(blob, ensure_ascii=False)
        seal_uri = "data:image/gif;base64," + base64.b64encode(SEAL.read_bytes()).decode() if SEAL.exists() else ""
        page = (GATED_HTML.replace("__GATE_CSS__", GATE_CSS)
                          .replace("__APP_CSS__", APP_CSS)
                          .replace("__GATE_HTML__", GATE_HTML)
                          .replace("__APP_HTML__", APP_HTML)
                          .replace("__GATE_JS__", GATE_JS)
                          .replace("__APP_JS__", APP_JS)
                          .replace("__BLOB__", payload)
                          .replace("/*__SEAL__*/''", "/*__SEAL__*/'" + seal_uri + "'"))
        OUT.write_text(page, encoding="utf-8")
        print(f"decide.html written (GATED): {len(items)} items, batch {batch}")
    else:
        page = (OPEN_HTML.replace("__APP_CSS__", APP_CSS)
                         .replace("__APP_HTML__", APP_HTML)
                         .replace("__APP_JS__", APP_JS)
                         .replace("__DATA__", data.replace("</", "<\\/")))
        OUT.write_text(page, encoding="utf-8")
        print(f"decide.html written (OPEN): {len(items)} items, batch {batch} — 未设密码！写 .decide_pwd 后重建即为加密版")


if __name__ == "__main__":
    main()
