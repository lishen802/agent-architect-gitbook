"""第 1 章插图：图 1-1 至 1-3。运行：python3 assets/build-ch01-figures.py"""
from figlib import Figure


def control_boundary():
    f = Figure(1000, 820, '图 1-1 控制流由谁决定',
               '左侧规则程序的下一步由代码分支决定；右侧智能体的下一步由模型在允许范围内提议，'
               '校验、授权、执行与终止判定仍由运行时负责。', label='图 1-1｜控制流由谁决定')
    # 左：规则程序
    f.group(30, 84, 450, 650, '规则程序：下一步写在代码分支中', 'state')
    a = f.card(75, 120, 360, '接收告警', kind='neutral')
    b = f.card(75, 214, 360, '查询服务指标', kind='external')
    c = f.card(75, 308, 360, '错误率是否超过阈值？', ['判断规则由开发者预先写定'], kind='code')
    f.arrow((a['cx'], a['b']), (b['cx'], b['y'] - 4))
    f.arrow((b['cx'], b['b']), (c['cx'], c['y'] - 4))
    d = f.card(55, 476, 190, '创建事故单', kind='external')
    e = f.card(265, 476, 190, '结束', kind='neutral')
    f.arrow((d['cx'], c['b']), (d['cx'], d['y'] - 4), label='是', at=(d['cx'] + 26, c['b'] + 40))
    f.arrow((e['cx'], c['b']), (e['cx'], e['y'] - 4), label='否', at=(e['cx'] + 26, c['b'] + 40))
    f.text(255, 610, '同样的输入与外部状态', 17, '#475569', anchor='middle')
    f.text(255, 636, '总是走同一条路径', 17, '#475569', anchor='middle')
    # 右：智能体
    f.group(520, 84, 450, 650, '智能体：下一步由模型在运行时提议', 'state')
    s = f.card(580, 118, 340, '目标与当前任务状态', kind='state')
    m = f.card(580, 200, 340, '模型提议下一步', ['查指标、查发布、请求人工或完成'], kind='model', strong=True)
    v = f.card(580, 313, 340, '运行时校验与授权', ['不合法或不允许的提议不执行'], kind='code')
    x = f.card(580, 426, 340, '执行并记录观察', ['结果写入任务状态'], kind='external')
    t = f.card(580, 539, 340, '运行时判定是否终止', ['完成验收 / 预算耗尽 / 无进展'], kind='code')
    for p, q in ((s, m), (m, v), (v, x), (x, t)):
        f.arrow((p['cx'], p['b']), (q['cx'], q['y'] - 4))
    f.arrow((t['x'], t['cy']), (548, t['cy']), (548, m['cy']), (m['x'] - 4, m['cy']), style='loop',
            label='继续', at=(548, (t['cy'] + m['cy']) / 2 + 6))
    end = f.card(580, 660, 340, '终止：结束或交给人工', kind='human')
    f.arrow((t['cx'], t['b']), (end['cx'], end['y'] - 4), style='ok')
    f.legend(36, 786, ['model', 'code', 'external', 'state'], extra=[('main', '主路径'), ('loop', '回路')])
    f.save('01-control-boundary.svg')


def control_modes():
    f = Figure(1000, 724, '图 1-2 四种控制方式的组合',
               '确定性代码包住工作流；受控模型调用可以嵌在代码或工作流阶段中；'
               '只有需要边观察边决定的局部环节，才放入受约束的智能体。', label='图 1-2｜四种控制方式的组合')
    f.group(30, 84, 620, 560, '① 规则程序：身份、权限、事务、最终提交', 'code', dashed=False)
    f.card(56, 116, 300, '② 受控模型调用', ['嵌在代码中：分类、抽取、摘要'], kind='model')
    f.group(56, 246, 568, 378, '③ 预定义工作流：阶段与转移预先规定', 'neutral', dashed=False)
    names = [('接收告警', 'neutral'), ('收集材料', 'neutral'), ('生成摘要', 'model'), ('审批执行', 'human')]
    cards = []
    for i, (n, k) in enumerate(names):
        cards.append(f.card(72 + i * 138, 282, 124, n, kind=k))
    for p, q in zip(cards, cards[1:]):
        f.arrow((p['r'], p['cy']), (q['x'] - 4, q['cy']), style='flow')
    f.group(80, 424, 520, 180, '④ 受约束的智能体（局部）', 'model')
    p1 = f.card(100, 466, 140, '模型提议', kind='model')
    p2 = f.card(270, 466, 140, '系统校验', kind='code')
    p3 = f.card(440, 466, 140, '执行观察', kind='external')
    f.arrow((p1['r'], p1['cy']), (p2['x'] - 4, p2['cy']), style='flow')
    f.arrow((p2['r'], p2['cy']), (p3['x'] - 4, p3['cy']), style='flow')
    f.arrow((p3['cx'], p3['b']), (p3['cx'], 560), (p1['cx'], 560), (p1['cx'], p1['b'] + 4), style='loop')
    f.text(340, 590, '工具、预算与终止条件由外层规定', 17, '#475569', anchor='middle')
    f.arrow((cards[1]['cx'], cards[1]['b']), (cards[1]['cx'], 410), style='model',
            label='取证阶段内部', at=(cards[1]['cx'] + 82, 390))
    # 右侧：下一步由谁决定
    f.text(680, 112, '下一步由谁决定', 19, '#1e293b', '600')
    rows = [(1, '规则程序', ['业务代码分支'], 'code'),
            (2, '受控模型调用', ['业务代码；模型只完成一步'], 'model'),
            (3, '预定义工作流', ['预定义的状态与转移'], 'neutral'),
            (4, '受约束的智能体', ['模型在允许范围内提议', '运行时校验并持有终止权'], 'model')]
    y = 134
    for n, t, lines, k in rows:
        c = f.card(680, y, 290, t, lines, kind=k, badge=n, align='left')
        y = c['b'] + 14
    f.card(680, y + 4, 290, '', ['①—③ 控制流仍在代码中', '只有 ④ 把下一步交给模型'], kind='state', align='left')
    f.legend(36, 694, ['code', 'model', 'external', 'human', 'state'], extra=[('loop', '回路')])
    f.save('01-control-modes.svg')


def action_pipeline():
    f = Figure(1040, 664, '图 1-3 动作执行流水线',
               '模型提议、系统校验、策略裁决、工具执行、结果核对依次进行；校验失败与策略拒绝转为结构化观察返回模型；'
               '需要审批时挂起，批准后复核再执行；结果不明时按操作标识查询，再对账或交给人工。',
               label='图 1-3｜动作执行流水线：模型提议，系统校验，策略裁决，工具执行')
    spec = [('模型提议', ['工具、参数、理由', '只是候选'], 'model'),
            ('系统校验', ['参数与 Schema', '资源与限额'], 'code'),
            ('策略裁决', ['主体、资源、动作', '允许/拒绝/审批'], 'code'),
            ('工具执行', ['超时、幂等键', '审计与规范化'], 'external'),
            ('结果核对', ['读取外部结果', '写入任务状态'], 'external')]
    xs = [40 + i * 196 for i in range(5)]
    main = []
    for i, (x, (t, lines, k)) in enumerate(zip(xs, spec)):
        c = f.card(x, 140, 176, t, lines, kind=k, strong=True)
        f.badge(x + 20, 140, i + 1, k)
        main.append(c)
    for p, q in zip(main, main[1:]):
        f.arrow((p['r'], p['cy']), (q['x'] - 4, q['cy']), style='main')
    # 顶部回路：观察返回模型
    f.arrow((main[4]['cx'], main[4]['y']), (main[4]['cx'], 100), (main[0]['cx'], 100), (main[0]['cx'], main[0]['y'] - 4),
            style='loop', label='观察写入任务状态，进入下一轮或由运行时终止', at=(540, 106))
    # 分支行
    vf = f.card(xs[1], 350, 176, '校验失败', ['转为结构化观察', '不回传堆栈'], kind='risk')
    pr = f.card(xs[2], 350, 176, '策略拒绝', ['记录拒绝原因', '作为观察返回'], kind='risk')
    ap = f.card(xs[3], 350, 176, '需要审批', ['保存状态并挂起', '批准绑定参数版本'], kind='human')
    un = f.card(xs[4], 350, 176, '结果不明', ['按操作标识查询', '确认前不重试'], kind='risk')
    f.arrow((main[1]['cx'], main[1]['b']), (vf['cx'], vf['y'] - 4), style='fail')
    f.arrow((main[2]['cx'], main[2]['b']), (pr['cx'], pr['y'] - 4), style='fail')
    gy = main[2]['b'] + 34
    f.arrow((main[2]['cx'] + 60, main[2]['b']), (main[2]['cx'] + 60, gy), (ap['cx'] - 40, gy), (ap['cx'] - 40, ap['y'] - 4),
            style='flow')
    f.arrow((ap['cx'] + 40, ap['y']), (ap['cx'] + 40, main[3]['b'] + 4), style='ok',
            label='批准后复核', at=(ap['cx'] + 52, gy + 30), anchor='start')
    f.arrow((main[4]['cx'], main[4]['b']), (un['cx'], un['y'] - 4), style='fail',
            label='无法确认', at=(un['cx'] + 12, gy + 30), anchor='start')
    # 失败回路回到模型
    ry = vf['b'] + 40
    f.raw(f'<path d="M{pr["cx"]},{pr["b"]} L{pr["cx"]},{ry}" stroke="#dc2626" stroke-width="2" fill="none" stroke-dasharray="7 5"/>')
    f.arrow((vf['cx'], vf['b']), (vf['cx'], ry), (main[0]['cx'], ry), (main[0]['cx'], main[0]['b'] + 4), style='fail')
    f.raw(f'<path d="M{pr["cx"]},{ry} L{vf["cx"]},{ry}" stroke="#dc2626" stroke-width="2" fill="none" stroke-dasharray="7 5"/>')
    f.pill(main[0]['cx'], (main[0]['b'] + ry) / 2 + 40, '返回模型', '#dc2626')
    hu = f.card(xs[4], 508, 176, '对账或人工接手', ['以外部记录为准'], kind='human')
    f.arrow((un['cx'], un['b']), (hu['cx'], hu['y'] - 4), style='flow')
    f.legend(40, 634, ['model', 'code', 'external', 'human', 'risk'], extra=[('main', '主路径'), ('fail', '异常')])
    f.save('01-action-pipeline.svg')


if __name__ == '__main__':
    control_boundary()
    control_modes()
    action_pipeline()
