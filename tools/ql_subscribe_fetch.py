# -*- coding: utf-8 -*-
"""千里马 VIP 订阅中心每日采集（替代 ql_vip_search 泛词全局搜索）
================================================================
原理：登录千里马 VIP → 抓取"订阅信息"页（用户自配订阅器"银信标讯"/"金融标讯2"
关键词标题匹配的每日推送），结构化输出 {title,url,stage,region,date}，
并按看板规则做代码级预过滤（结果类/非银证保/行政/硬件/泛噪声），
只把"公告-招标/变更/预告"阶段的银行/信托/理财/农商/农信/联社相关条目交给
定时任务核实截止日期后进入候选流程。

用法: python3 ql_subscribe_fetch.py [页数, 默认3]
输出: monitor/subscribe_items_YYYYMMDD_HHMM.json
"""
import sys, os, time, json, re
from datetime import datetime, date
from playwright.sync_api import sync_playwright

USER = 'chaxun032322'
PASS = 'Chaxun!2026'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLOSE_OVERLAY_JS = """(()=>{
  document.querySelectorAll('.btn-image-bg').forEach(e=>e.style.display='none');
  document.querySelectorAll('div').forEach(e=>{
    const cs=getComputedStyle(e);
    if((cs.position==='fixed'||cs.position==='absolute') && parseInt(cs.zIndex||'0')>=100
       && e.offsetWidth>200 && e.offsetHeight>200 && !e.querySelector('#log')) e.style.pointerEvents='none';
  });
})()"""

# 机构范围：银行（含农商/农信/联社/开行/进出口/邮储）、理财子、信托；证券/基金/保险/期货排除
ORG_INCLUDE = ['银行','农商','农信','联社','信托','理财','信用合作','村镇银行','开行','进出口银行','邮储','金租','消费金融','汽车金融','财务公司','金控']
ORG_EXCLUDE = ['证券','基金','期货','保险','资管','财富','租赁','保理','小额贷款','担保','典当','供应链','医院','学校','大学','研究院','局','政府','委员会','集团','能源','矿业','交通','铁路','电力','水务','燃气','城投','交投','建工','建设','地产','置业','物业','酒店','航空','航运','港口','化工','材料','食品','药业','医院','报社','电视台','移动','电信','联通','铁塔','邮政']
# 注意：资管/财富出现在排除是因为它们常组成"XX资管公司/XX财富公司"（非银机构）；
# 但"理财"保留（理财子公司）。若标题同时含银行/信托/理财字样则优先纳入。

STAGE_EXCLUDE = ['结果', '中标', '成交', '候选人', '废标', '流标', '终止', '失败']
TITLE_EXCLUDE = ['体检','物业','保安','食堂','餐厅','食材','伙','保洁','绿化','装修','家具','车辆','服装','制服','印刷','宣传','广告','视频','直播','礼品','慰问','办公用品','空调','电梯','消防','安防','监控设备','门禁','装修','监理','勘察','设计施工','EPC','总承包','工程造价','审计服务','法律服务','律师','会计','评估','拍卖','出租','出售','挂牌','转让','报废','回收','维保费','保险','机票','酒店','培训','考察','招聘','劳务派遣','餐饮','厨','冷链','仓储','运输','物流','配送','光伏','风电','充电桩','储能','电池','算力','服务器','交换机','GPU','机房','柴油','发电机','UPS','蓄电池','电缆','光缆','基站','终端设备','一体机','打印机','复印','笔记本电脑','台式','平板电脑','会议设备','音响','LED','显示屏','房屋','土地','商铺','写字楼','房产','农','牧','渔','林','水利','环保','市政','公路','桥梁','隧道','煤矿','石油','天然气','化工','钢铁','有色','建材','水泥','砂石','混凝土','图书','教材','期刊','数据库软件','数据库维保','Oracle','SQL Server','MySQL','中间件','操作系统','虚拟化','云资源','云服务等保','等保测评','密评','密码测评']
# 业务正向词（标题含其一才保留，双保险）
BIZ_INCLUDE = ['系统','平台','软件','开发','研发','改造','升级','建设','外包','驻场','运维','维保','大模型','AI','智能','数据','报送','EAST','信创','国产','数字人民币','数币','估值','核算','TA','代销','理财','财富','托管','资金','同业','金市','风控','反洗钱','合规','授信','核心','渠道','手机银行','网银','客服','RPA','OCR','NLP','知识图谱','咨询','测试']

def login(page):
    page.goto('https://www.qianlima.com/', timeout=60000)
    time.sleep(3)
    page.evaluate(CLOSE_OVERLAY_JS)
    page.evaluate("document.querySelector('#loginBottomLink').click()")
    time.sleep(1.5)
    page.evaluate("document.querySelector('#log').click()")
    time.sleep(1.5)
    page.locator('input:visible[placeholder*="用户名"]').first.fill(USER, timeout=8000)
    page.locator('input:visible[type="password"]').first.fill(PASS, timeout=8000)
    page.locator('div.regist-foot:visible, button:visible:has-text("登录")').last.click(timeout=8000)
    time.sleep(5)

def extract(page):
    return page.evaluate("""(()=>{
      const out=[];
      document.querySelectorAll('a[href*="bid-"]').forEach(a=>{
        const t=(a.innerText||a.textContent||'').trim().replace(/\\s+/g,' ');
        if(t.length>6){
          const row=a.closest('li,tr,div[class*="item"],div[class*="list"]')||a.parentElement;
          const rt=(row?row.innerText:'').replace(/\\s+/g,' ').slice(0,200);
          out.push({title:t.slice(0,90), url:a.href.split('?')[0], row:rt});
        }});
      const seen=new Set(); return out.filter(o=>!seen.has(o.url)&&seen.add(o.url));
    })()""")

def parse_row(it):
    """从行文本解析 阶段/地区/日期。"""
    row = it['row']
    m = re.search(r'(公告|结果|采购意向|预告)-([\u4e00-\u9fa5]+?)([\u4e00-\u9fa5]{2,3}(?:省|市|自治区)?[-－])?([\u4e00-\u9fa9]{2,4})(服务|货物|工程|文件|$)', row)
    dm = re.search(r'(20\d{2}-\d{2}-\d{2})', row)
    stage = m.group(2) if m else ''
    stage_cat = m.group(1) if m else ''
    d = dm.group(1) if dm else ''
    return {'stage': stage, 'stage_cat': stage_cat, 'date': d}

def classify(it):
    t = it['title']
    meta = parse_row(it)
    it.update(meta)
    # 阶段过滤：只要 公告/变更/预告/采购意向
    if meta['stage_cat'] == '结果' or any(k in t for k in STAGE_EXCLUDE):
        it['verdict'] = 'drop_stage'; return it
    # 机构过滤
    has_org_inc = any(k in t for k in ORG_INCLUDE)
    # 明确非银机构：标题含排除词且不含纳入词
    if not has_org_inc:
        it['verdict'] = 'drop_org'; return it
    if any(k in t for k in ['证券公司','券商','基金','期货','保险','保理','融资租赁','小额贷款','供应链']):
        # 银行系基金(理财子)保留：XX理财 已含在 ORG_INCLUDE
        if not any(k in t for k in ['银行','农商','农信','联社','信托','理财']):
            it['verdict'] = 'drop_org'; return it
    # 行政/硬件/噪声
    if any(k in t for k in TITLE_EXCLUDE):
        it['verdict'] = 'drop_noise'; return it
    # 业务正向
    if not any(k in t for k in BIZ_INCLUDE):
        it['verdict'] = 'drop_biz'; return it
    it['verdict'] = 'keep'
    return it

def main():
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    all_items = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36').new_page()
        login(page)
        page.goto('https://vip.qianlima.com/subscribe-center/subscribe-info', timeout=60000)
        time.sleep(6)
        # 进入"银信标讯"订阅器详情（nth(1)=div.subscribe-name；nth(0)是列表文本span）
        # 注意：不在页面侧勾选阶段复选框（勾选"公告"会导致列表清空，原因未查明），
        # 阶段过滤全部由代码 classify() 的 drop_stage 兜底，已实测可靠。
        try:
            page.locator('text=银信标讯').nth(1).click(timeout=8000)
            time.sleep(5)
        except Exception as e:
            print('  订阅器选择失败(用默认全文):', str(e)[:80])
        for pg in range(1, pages + 1):
            items = extract(page)
            for it in items:
                it['page'] = pg
                classify(it)
            all_items.extend(items)
            print(f'  page {pg}: {len(items)} items')
            if pg < pages:
                try:
                    btn = page.locator('button.btn-next')
                    if btn.get_attribute('disabled') is not None:
                        print('  已到最后一页')
                        break
                    btn.click()
                    time.sleep(5)
                except Exception as e:
                    print('  翻页失败:', str(e)[:80])
                    break
        b.close()
    # 去重
    seen = set(); uniq = []
    for it in all_items:
        if it['url'] not in seen:
            seen.add(it['url']); uniq.append(it)
    keep = [i for i in uniq if i['verdict'] == 'keep']
    out = {
        'run_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'pages': pages, 'total': len(uniq), 'keep': len(keep),
        'verdict_counts': {v: sum(1 for i in uniq if i['verdict']==v) for v in ['keep','drop_stage','drop_org','drop_noise','drop_biz']},
        'items': uniq,
    }
    os.makedirs(os.path.join(BASE, 'monitor'), exist_ok=True)
    fn = os.path.join(BASE, 'monitor', f"subscribe_items_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
    json.dump(out, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"总条目 {len(uniq)} | 保留 {len(keep)} | 分布 {out['verdict_counts']}")
    for i in keep:
        print(f"  [keep] {i['date'] or '今'} {i['title'][:60]} | {i['stage']} | {i['url'].split('/')[-1]}")
    print('明细:', fn)

if __name__ == '__main__':
    main()
