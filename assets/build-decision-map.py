"""Build the book's editable, dependency-free SVG architecture decision map."""
from pathlib import Path
from html import escape
W,H=1400,1100
items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">', '<title id="title">图 2-1 从需求到方案的分层选型图</title>', '<desc id="desc">先明确任务与基线，再比较控制方式；信息获取、授权和恢复分别决策，最后通过评测与预算实验验证。</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>', '<rect width="1400" height="1100" fill="#f8fafc"/>']
def text(x,y,s,size=20,color='#172b4d',weight='normal'):
 items.append(f'<text x="{x}" y="{y}" font-family="PingFang SC, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')
def box(x,y,w,h,title,lines,fill='#ffffff'):
 items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#cbd5e1" stroke-width="1.5"/>')
 text(x+20,y+33,title,21,weight='600')
 for i,line in enumerate(lines):text(x+20,y+66+29*i,line,18,'#334155')
def arrow(x1,y1,x2,y2):
 items.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#64748b" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
text(50,52,'从需求到方案',32,weight='600')
text(50,84,'图 2-1｜比较控制方式，再独立决定信息、授权与恢复。箭头表示设计顺序，不表示自动升级。',19,'#475569')
box(50,114,1300,105,'1  明确任务与验收',['输入、交付物、使用者、错误后果、无法判断时的出口；写出需要确认的业务前提。'],'#eaf2ff')
arrow(700,219,700,242)
box(50,246,1300,105,'2  先比较无需模型的基线',['规则、数据库查询或普通搜索能否满足目标？能则保留为方案；不足时明确模型要补哪一项能力。'])
arrow(700,351,700,375)
text(50,406,'3  比较候选控制方式：可以组合，按任务证据选择',22,weight='600')
box(50,425,310,150,'规则程序',['规则可明确表达','适合校验、计算与提交','仍需处理依赖和异常'])
box(380,425,310,150,'受控模型调用',['材料已给定','需要理解、抽取或生成','应用决定下一阶段'])
box(710,425,310,150,'预定义工作流',['阶段和转移可描述','可含模型、循环与等待','恢复取决于具体实现'])
box(1040,425,310,150,'受约束的智能体',['行动依赖新证据','需反馈、预算与退出','仅开放必要的动态选择'])
for x in (205,535,865,1195):arrow(x,575,x,611)
text(50,645,'4  独立补齐三个维度：任一种控制方式都可能需要这些设计',22,weight='600')
box(50,665,420,160,'信息获取',['给定材料 / 权威业务查询 / 文档检索','说明权限、来源、时效与缺口','有检索不等于有智能体'],'#f0fdfa')
box(490,665,420,160,'动作与授权',['只读 / 建议 / 受控写操作','按后果与业务规则决定是否审批','只读也需要数据访问控制'],'#f0fdfa')
box(930,665,420,160,'状态与恢复',['任务事实、并发与操作标识','超时后核对结果，不盲目重试','保留取消、失败与人工接手路径'],'#f0fdfa')
arrow(700,825,700,850)
box(50,858,1300,120,'5  形成一页方案，用最小实验验证',['列出候选与不选理由、任务集与判对错方法、调用与人工成本、延迟区间、尚未验证的假设。','若质量或预算不满足：回到对应决策修正；不默认增加 Agent、检索或协作角色。'],'#fff7ed')
text(50,1020,'阅读提示：本图是本书的设计检查顺序，不是统计选型器，也不承诺某类架构必然更优。',19,'#475569')
text(50,1055,'需要检索、需要审批、需要自主决策，是不同问题；按同一任务的验收结果比较方案。',19,'#475569')
items.append('</svg>')
Path(__file__).with_name('02-decision-map.svg').write_text('\n'.join(items)+'\n')
