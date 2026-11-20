#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标讯候选决策·共用核心（2026-11-20「晨报·决策一体」组件与 decide.html 网页同源改造）。

契约（两个消费方必须共同遵守；改本文件 = 两边同时生效）：
- 数据：bidding-daily/pending_candidates.json 中 status==「待确认」条目；
  行字段 push_no/company/project/budget/deadline/tags/rec。
- 列序：COLUMNS（编号|招标单位/项目|预算|投标截止|业务标签|投标建议|决策），表头 HEAD_HTML。
- 交互：chips 纳入/不纳入（再点取消）、标签输入即存（change/blur 时校验标红）、
  建议下拉三值（强烈建议投标/建议投标/可关注）、行内标签白名单校验（最多3个）。
- 提交载荷：{batch, decisions:[{push_no, decision, tags(逗号串), rec}]}——组件 emit 与
  网页生成指令文本解析同构，自动化执行器（automation_36a68632）只认这一种结构。

差异由各消费方自带适配层（不进本文件）：
- 组件 refresh_board_widgets.py：DaimonWidget 草稿 saveInput / emit('submit') /
  onStatusChange / onDataChange + 执行进度面板（六阶段估算耗时）。
- 网页 build_decide_page.py：localStorage 草稿 + 生成指令文本 + 复制 + 加密门禁。

自动化判据引用注意：组件三判据若校验"决策区条数"，以本模块 load_data()["items"] 长度为准。
"""
import datetime
import json
from pathlib import Path

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
PENDING_JSON = BIDDING / "pending_candidates.json"

# 列序契约（两边表头/JS 渲染共用；列宽由消费方 CSS 各自控制）
COLUMNS = ["编号", "招标单位 / 项目", "预算", "投标截止", "业务标签", "投标建议", "决策"]
HEAD_HTML = "<thead><tr>" + "".join(f"<th>{c}</th>" for c in COLUMNS) + "</tr></thead>"

REC_OPTIONS = ["强烈建议投标", "建议投标", "可关注"]


def load_items():
    """待确认候选列表（与 pending 台账同源；status 缺失的旧条目视为待确认）。"""
    if not PENDING_JSON.exists():
        return []
    try:
        data = json.loads(PENDING_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    items = []
    for e in data:
        if str(e.get("status", "待确认")) in ("待确认", "None", ""):
            items.append({
                "push_no": e.get("push_no"), "company": e.get("company", ""),
                "project": e.get("project", ""), "budget": e.get("budget", "-"),
                "deadline": e.get("deadline", ""), "tags": e.get("tags", ""),
                "rec": e.get("rec", "可关注"),
            })
    return items


def load_valid_tags():
    try:
        import importlib.util as vu
        vs = vu.spec_from_file_location("cfg", str(BIDDING / "config.py"))
        vm = vu.module_from_spec(vs)
        vs.loader.exec_module(vm)
        return sorted(getattr(vm, "VALID_TAGS", []))
    except Exception:
        return []


def build_data(today=None):
    """渲染决策表所需的完整数据包（组件与网页共用同一份）。"""
    batch = (today or datetime.date.today()).isoformat()
    return {"batch": batch, "items": load_items(), "valid_tags": load_valid_tags()}


def data_json(data):
    """嵌入 <script type="application/json"> 的安全序列化（防 </script> 截断）。"""
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


# ── 共用渲染/状态机 JS（浏览器端 window.DecisionCore）────────────────────────
# 适配层通过 opts 注入：body(tbody id/元素)、persist(decisions)、onStat(n,total)。
CORE_JS = r"""
window.DecisionCore = {
  create: function(opts){
    var DATA = opts.data, VALID = DATA.valid_tags || [];
    var decisions = {}, persistFn = opts.persist || function(){}, onStat = opts.onStat || function(){};
    var bodyEl = typeof opts.body === 'string' ? document.getElementById(opts.body) : opts.body;
    function esc(x){ return String(x==null?'':x).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]}); }
    function defaults(){ var d={}; DATA.items.forEach(function(it){ d[it.push_no]={decision:null,tags:it.tags,rec:it.rec}; }); return d; }
    function splitTags(s){ return String(s||'').split(/[,，、;；\s]+/).map(function(t){return t.trim()}).filter(Boolean); }
    function tagError(s){
      var ts = splitTags(s);
      if (ts.length > 3) return '最多 3 个标签';
      for (var i=0;i<ts.length;i++){ if (VALID.length && VALID.indexOf(ts[i])<0) return '「'+ts[i]+'」不在标签库'; }
      return '';
    }
    function get(){ return decisions; }
    function updateStat(){ var n=Object.keys(decisions).filter(function(k){return decisions[k].decision}).length; onStat(n, DATA.items.length); }
    function render(){
      if (!DATA.items.length){ bodyEl.innerHTML=''; updateStat(); return; }
      var dl = '<datalist id="taglib">'+VALID.map(function(t){return '<option value="'+esc(t)+'">'}).join('')+'</datalist>';
      var h = dl;
      DATA.items.forEach(function(it){
        var d = decisions[it.push_no] || (decisions[it.push_no]={decision:null,tags:it.tags,rec:it.rec});
        var te = tagError(d.tags);
        h += '<tr data-no="'+it.push_no+'">'
          + '<td class="num">'+esc(it.push_no)+'</td>'
          + '<td><div class="co">'+esc(it.company)+'</div><div class="pj">'+esc(it.project)+'</div></td>'
          + '<td class="num">'+esc(it.budget)+'</td>'
          + '<td class="num">'+esc(it.deadline)+'</td>'
          + '<td><input list="taglib" placeholder="最多3个，逗号分隔" class="tag-in'+(te?' bad':'')+'" data-no="'+it.push_no+'" value="'+esc(d.tags)+'"/>'
          + (te?'<div class="tag-err">'+esc(te)+'</div>':'')+'</td>'
          + '<td><select class="rec-sel" data-no="'+it.push_no+'">'
          + __REC_OPTIONS__.map(function(r){return '<option'+(r===d.rec?' selected':'')+'>'+r+'</option>'}).join('')
          + '</select></td>'
          + '<td><div class="rec-seg">'
          + '<button type="button" class="chip pos" data-no="'+it.push_no+'" data-v="纳入" aria-pressed="'+(d.decision==='纳入')+'">纳入</button>'
          + '<button type="button" class="chip neg" data-no="'+it.push_no+'" data-v="不纳入" aria-pressed="'+(d.decision==='不纳入')+'">不纳入</button>'
          + '</div></td></tr>';
      });
      bodyEl.innerHTML = h;
      bodyEl.querySelectorAll('.chip').forEach(function(c){
        c.addEventListener('click', function(){
          var no = +c.dataset.no;
          decisions[no].decision = (decisions[no].decision===c.dataset.v) ? null : c.dataset.v;
          persistFn(decisions); updateStat();
          c.closest('tr').querySelectorAll('.chip').forEach(function(x){
            x.setAttribute('aria-pressed', decisions[no].decision===x.dataset.v ? 'true':'false');
          });
        });
      });
      bodyEl.querySelectorAll('.tag-in').forEach(function(t){
        t.addEventListener('input', function(){ decisions[+t.dataset.no].tags=t.value; persistFn(decisions); });
        t.addEventListener('change', function(){ decisions[+t.dataset.no].tags=t.value.trim(); persistFn(decisions); render(); });
        t.addEventListener('blur', function(){ render(); });
      });
      bodyEl.querySelectorAll('.rec-sel').forEach(function(sel){
        sel.addEventListener('change', function(){ decisions[+sel.dataset.no].rec=sel.value; persistFn(decisions); updateStat(); });
      });
      updateStat();
    }
    // 收集提交载荷；errors 非空时禁止提交
    function collect(){
      var ds=[], errs=[];
      DATA.items.forEach(function(it){
        var d = decisions[it.push_no]; if (!d || !d.decision) return;
        var te = tagError(d.tags);
        if (te){ errs.push('第'+it.push_no+'行：'+te); return; }
        ds.push({push_no:it.push_no, decision:d.decision, tags:splitTags(d.tags).join(','), rec:d.rec});
      });
      return {list:ds, errors:errs};
    }
    return {
      render: render, collect: collect, get: get,
      snapshot: function(){ return JSON.parse(JSON.stringify(decisions)); },
      restore: function(saved){ decisions = (saved && typeof saved==='object') ? saved : defaults(); render(); persistFn(decisions); },
      reset: function(){ decisions = defaults(); render(); persistFn(decisions); }
    };
  }
};
""".replace("__REC_OPTIONS__", json.dumps(REC_OPTIONS, ensure_ascii=False))
