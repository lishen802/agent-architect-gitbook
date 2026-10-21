"""Build the book's editable, dependency-free SVG reference architecture."""
from pathlib import Path
from html import escape
W,H=1400,1090
items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">', '<title id="title">图 S-1 AI 应用参考架构</title>', '<desc id="desc">入口与身份之下是由代码负责的应用控制面，包含编排、上下文组装、模型网关、输出校验、策略与授权、任务状态和人工协作；模型服务、知识检索和工具执行器挂在控制面之下；评测与观测贯穿各层。</desc>', '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>', f'<rect width="{W}" height="{H}" fill="#f8fafc"/>']
def text(x,y,s,size=20,color='#172b4d',weight='normal'):
 items.append(f'<text x="{x}" y="{y}" font-family="PingFang SC, Noto Sans CJK SC, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(s)}</text>')
def box(x,y,w,h,title,lines,fill='#ffffff'):
 items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#cbd5e1" stroke-width="1.5"/>')
 text(x+20,y+33,title,21,weight='600')
 for i,line in enumerate(lines):text(x+20,y+66+29*i,line,18,'#334155')
def arrow(x1,y1,x2,y2):
 items.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#64748b" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
text(50,52,'AI 应用参考架构',32,weight='600')
text(50,84,'图 S-1｜模型与外部能力都挂在应用控制面上，由代码决定调用顺序、校验结果和授权动作。',19,'#475569')
box(50,110,1300,90,'入口与身份',['认证、租户、会话与限流；把调用者身份注入后续各层，身份与凭证不经由模型转述。'],'#eaf2ff')
arrow(700,200,700,228)
items.append('<rect x="50" y="232" width="1300" height="450" rx="14" fill="#eef2f7" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="8 6"/>')
text(74,265,'应用控制面：确定性骨架，由代码负责',22,weight='600')
box(80,285,500,150,'编排',['固定流程 / 工作流 / 受约束的智能体循环','决定何时调用模型、调用什么能力','持有预算、终止权与失败出口'])
box(610,285,345,150,'上下文组装',['为本次调用选择指令与材料','标注来源、版本与访问范围','控制输入规模'])
box(985,285,335,150,'模型网关',['供应商适配与超时','限流、重试与用量记录','记录模型与提示版本'])
box(80,465,290,170,'输出校验',['格式与 Schema','业务约束与引用关系','截断与拒绝的处理'])
box(395,465,290,170,'策略与授权',['主体、资源与动作','审批规则与参数绑定','模型提议不等于授权'])
box(710,465,290,170,'任务状态',['阶段、版本与待执行动作','操作标识与执行结果','与对话历史分开保存'])
box(1025,465,295,170,'人工协作',['审阅、审批与接手','交接材料与责任人','挂起后的恢复条件'])
text(80,665,'关键路径：模型提议 → 输出校验 → 策略裁决 → 工具执行 → 结果核对并记录状态',19,'#1e3a8a','600')
for x in (260,700,1140):arrow(x,682,x,712)
box(50,716,420,150,'知识与检索',['文档处理、索引与查询','检索前按权限过滤','保留版本与适用范围'],'#f0fdfa')
box(490,716,420,150,'工具执行器',['工具契约、参数与超时','幂等、审计与结果规范化','可经 MCP 等协议接入'],'#f0fdfa')
box(930,716,420,150,'模型服务',['托管接口或自建推理','只返回候选内容','不持有业务凭证'],'#f0fdfa')
box(50,890,1300,100,'评测与观测（贯穿各层）',['任务集与判定、调用链追踪、模型与提示版本、成本与延迟；线上失败样例回流到任务集。'],'#fff7ed')
text(50,1030,'阅读提示：这是完整形态，第一版通常只需编排、上下文组装、模型适配、输出校验与评测样例。',19,'#475569')
text(50,1063,'组件按出现的需求信号逐个加入；图中方框表示职责，不要求各自部署为独立服务。',19,'#475569')
items.append('</svg>')
Path(__file__).with_name('s1-reference-architecture.svg').write_text('\n'.join(items)+'\n')
