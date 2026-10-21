"""Build the editable, dependency-free SVG figures for chapter 1."""
from pathlib import Path
from html import escape

FONT = 'PingFang SC, Noto Sans CJK SC, sans-serif'


class Figure:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.items = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(desc)}</desc>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="#f8fafc"/>',
        ]

    def text(self, x, y, s, size=20, color='#172b4d', weight='normal', anchor='start'):
        self.items.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def rect(self, x, y, w, h, fill='#ffffff', stroke='#cbd5e1', dash=None, rx=12):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{d}/>')

    def box(self, x, y, w, h, title, lines=(), fill='#ffffff'):
        self.rect(x, y, w, h, fill)
        self.text(x + 20, y + 33, title, 21, weight='600')
        for i, line in enumerate(lines):
            self.text(x + 20, y + 64 + 28 * i, line, 18, '#334155')

    def arrow(self, *points, label=None, lx=None, ly=None):
        path = ' L'.join(f'{x},{y}' for x, y in points)
        self.items.append(f'<path d="M{path}" stroke="#64748b" stroke-width="2" fill="none" marker-end="url(#arrow)"/>')
        if label:
            self.text(lx, ly, label, 17, '#475569')

    def save(self, name):
        self.items.append('</svg>')
        Path(__file__).with_name(name).write_text('\n'.join(self.items) + '\n')


def control_boundary():
    f = Figure(1400, 860, '图 1-1 控制流由谁决定', '左侧规则程序的下一步由代码分支决定；右侧智能体的下一步由模型在允许范围内提议，校验、授权、执行与终止仍由运行时负责。')
    f.text(50, 52, '控制流由谁决定', 32, weight='600')
    f.text(50, 84, '图 1-1｜区别不在于是否调用模型，而在于下一步动作是否在运行时由模型提议。', 19, '#475569')
    f.rect(50, 110, 620, 640, '#eef2f7', '#94a3b8', '8 6')
    f.text(74, 145, '规则程序：下一步写在代码分支中', 22, weight='600')
    f.box(110, 175, 500, 80, '接收告警')
    f.arrow((360, 255), (360, 285))
    f.box(110, 289, 500, 80, '查询服务指标')
    f.arrow((360, 369), (360, 399))
    f.box(110, 403, 500, 100, '错误率是否超过阈值？', ['判断规则由开发者预先写定'], '#eaf2ff')
    f.arrow((235, 503), (235, 563), label='是', lx=248, ly=540)
    f.arrow((485, 503), (485, 563), label='否', lx=498, ly=540)
    f.box(110, 567, 250, 80, '创建事故单')
    f.box(380, 567, 230, 80, '结束')
    f.text(74, 700, '同样输入与外部状态，走同一条路径', 18, '#334155')
    f.rect(730, 110, 620, 640, '#eef2f7', '#94a3b8', '8 6')
    f.text(754, 145, '智能体：下一步在运行时由模型提议', 22, weight='600')
    f.box(790, 175, 500, 80, '目标与当前任务状态')
    f.arrow((1040, 255), (1040, 285))
    f.box(790, 289, 500, 100, '模型提议下一步', ['查指标、查发布、请求人工或宣布完成'], '#fff7ed')
    f.arrow((1040, 389), (1040, 419))
    f.box(790, 423, 500, 100, '运行时校验与授权', ['不合法或不允许的提议不会执行'], '#eaf2ff')
    f.arrow((1040, 523), (1040, 553))
    f.box(790, 557, 500, 100, '执行并记录观察结果', ['结果写入任务状态'])
    f.arrow((790, 607), (760, 607), (760, 339), (786, 339), label='继续', lx=686, ly=480)
    f.text(754, 700, '终止条件与是否真正完成，由运行时判定', 18, '#334155')
    f.text(50, 800, '阅读提示：右侧方框中只有“模型提议下一步”由模型完成，其余仍是代码职责。', 19, '#475569')
    f.text(50, 832, '模型在固定流程中只做分类或摘要时，控制流仍属于左侧形态。', 19, '#475569')
    f.save('01-control-boundary.svg')


def control_modes():
    f = Figure(1400, 820, '图 1-2 三种控制模式的组合', '确定性代码包住工作流，工作流中只在需要动态调查的局部放入智能体；三者组合在同一个系统中。')
    f.text(50, 52, '三种控制模式的组合', 32, weight='600')
    f.text(50, 84, '图 1-2｜三者不是前后替代的技术代际，而是在同一系统中由外向内嵌套。', 19, '#475569')
    f.rect(50, 110, 860, 640, '#eaf2ff', '#94a3b8')
    f.text(76, 148, '确定性代码', 24, weight='600')
    f.text(76, 180, '身份、权限、配额、事务、最终提交', 18, '#334155')
    f.rect(100, 210, 760, 500, '#f0fdfa', '#94a3b8')
    f.text(126, 248, '工作流', 24, weight='600')
    f.text(126, 280, '长任务编排、等待、审批、补偿；阶段与转移预先定义', 18, '#334155')
    f.rect(150, 315, 660, 160, '#ffffff')
    f.text(176, 350, '固定阶段：接收告警 → 收集材料 → 生成摘要 → 等待审批 → 执行', 18, '#334155')
    f.text(176, 385, '每个阶段的进入条件、失败出口由代码规定', 18, '#334155')
    f.text(176, 420, '阶段内部可以调用模型做分类、抽取或摘要', 18, '#334155')
    f.rect(150, 500, 660, 180, '#fff7ed', '#f59e0b', '8 6')
    f.text(176, 538, '智能体（局部）', 24, weight='600')
    f.text(176, 572, '只放在无法预先穷举、需要根据观察选择下一步的环节', 18, '#334155')
    f.text(176, 604, '例：根据日志异常决定接着查实例版本还是下游依赖', 18, '#334155')
    f.text(176, 636, '可用工具、预算与终止条件由外层规定', 18, '#334155')
    f.box(950, 110, 400, 190, '下一步由谁决定', ['确定性代码：业务分支', '工作流：预定义的状态转移', '智能体：模型在允许范围内提议'])
    f.box(950, 330, 400, 190, '主要风险', ['代码：规则遗漏、依赖失败', '工作流：转移规则、版本迁移', '智能体：漂移、循环、越权、成本'])
    f.box(950, 550, 400, 200, '分配原则', ['能稳定写成规则的，用代码', '拓扑已知的多阶段，用工作流', '必须边看边决定的，才用智能体', '不可逆动作，收回到代码与审批'], '#f0fdfa')
    f.text(50, 795, '阅读提示：内层能力的作用范围由外层决定；智能体的提议仍要经过外层的校验、授权与提交。', 19, '#475569')
    f.save('01-control-modes.svg')


def action_pipeline():
    f = Figure(1400, 700, '图 1-3 动作执行流水线', '模型提议、系统校验、策略裁决、工具执行、结果核对依次进行；校验失败与策略拒绝转为结构化观察返回，需要审批时挂起，结果不明时先查询核对。')
    f.text(50, 52, '动作执行流水线', 32, weight='600')
    f.text(50, 84, '图 1-3｜模型提议，系统校验，策略裁决，工具执行。每一关都可以拦下提议。', 19, '#475569')
    steps = [
        ('模型提议', ['工具名、参数、理由', '只是候选，不是命令'], '#fff7ed'),
        ('系统校验', ['工具存在、Schema', '资源标识、大小与时限'], '#ffffff'),
        ('策略裁决', ['主体、资源、动作', '允许 / 拒绝 / 需审批'], '#eaf2ff'),
        ('工具执行', ['超时、幂等键', '审计、结果规范化'], '#ffffff'),
        ('结果核对', ['读取外部系统结果', '写入任务状态'], '#f0fdfa'),
    ]
    xs = [50, 312, 574, 836, 1098]
    for x, (title, lines, fill) in zip(xs, steps):
        f.box(x, 130, 240, 140, title, lines, fill)
    for a, b in zip(xs, xs[1:]):
        f.arrow((a + 240, 200), (b - 4, 200))
    f.arrow((432, 270), (432, 380))
    f.box(312, 384, 240, 130, '校验失败', ['转为结构化观察', '不把堆栈塞回上下文'])
    f.arrow((660, 270), (660, 380))
    f.box(574, 384, 240, 130, '策略拒绝', ['记录拒绝原因', '作为观察返回'])
    f.arrow((740, 270), (740, 300), (930, 300), (930, 380))
    f.box(836, 384, 240, 130, '需要审批', ['保存状态并挂起', '批准绑定动作与参数'], '#eaf2ff')
    f.arrow((1218, 270), (1218, 380))
    f.box(1098, 384, 252, 130, '结果不明', ['按操作标识查询', '确认前不盲目重试'])
    f.arrow((432, 514), (432, 560), (170, 560), (170, 274), label='返回模型，进入下一轮或停止', lx=190, ly=550)
    f.arrow((694, 514), (694, 560), (436, 560))
    f.text(50, 630, '阅读提示：提示词中的约束不能替代第二、三关；即使模型提议了危险动作，也要有独立机制拦下。', 19, '#475569')
    f.text(50, 662, '审批与结果核对的详细设计见第 7、12 章。', 19, '#475569')
    f.save('01-action-pipeline.svg')


control_boundary()
control_modes()
action_pipeline()
