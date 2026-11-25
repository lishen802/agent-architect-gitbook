"""第 8 章插图：图 8-1 一次调用的上下文预算；图 8-2 上下文组装流水线；图 8-3 记忆写入与读取的控制点。"""
from figlib import Figure, KINDS, SUB, INK, chip, edge_point, text_width


def budget():
    f = Figure(1000, 600, '图 8-1 一次调用的上下文预算',
               '窗口 32000 Token：输出预留 4000，安全余量 3200，可用输入 24800。固定项 3000、必需项 3500 必须全部放下；'
               '弹性项按优先级整条选入 10400，未用 7900。其他租户的记忆、超出历史上限的早期摘要和超出剩余预算的日志样本未纳入。'
               '数字为教学构造。', label='图 8-1｜一次调用的上下文预算（教学数字，单位 Token）')
    X0, W, TOTAL = 40, 920, 32000
    k = W / TOTAL
    segs = [('固定项', 3000, 'code', False), ('必需项', 3500, 'external', False), ('弹性项', 10400, 'state', False),
            ('未用', 7900, 'neutral', True), ('安全余量', 3200, 'neutral', True), ('输出预留', 4000, 'model', False)]
    BY, BH = 132, 74
    x = X0
    xs = []
    f.raw(f'<clipPath id="bar"><rect x="{X0}" y="{BY}" width="{W}" height="{BH}" rx="10"/></clipPath><g clip-path="url(#bar)">')
    labels = []
    for name, n, kind, dashed in segs:
        fill, stroke, ink, _ = KINDS[kind]
        f.mark(kind)
        w = n * k
        d = ' stroke-dasharray="6 4"' if dashed else ''
        f.raw(f'<rect x="{x:.1f}" y="{BY}" width="{w:.1f}" height="{BH}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{d}/>')
        labels.append((x, w, name, n, kind, ink))
        xs.append((x, x + w))
        x += w
    f.raw('</g>')
    for x, w, name, n, kind, ink in labels:
        f.text(x + w / 2, BY + 31, name, 17, ink if kind != 'neutral' else SUB, '600', 'middle', maxw=w - 6)
        f.text(x + w / 2, BY + 56, f'{n}', 17, ink if kind != 'neutral' else SUB, 'normal', 'middle', maxw=w - 6)
    # 外框圆角
    f.raw(f'<rect x="{X0}" y="{BY}" width="{W}" height="{BH}" rx="10" fill="none" stroke="#64748b" stroke-width="1.5"/>')

    def brace(x1, x2, y, label, up=True):
        s = -1 if up else 1
        f.raw(f'<path d="M{x1:.1f},{y} L{x1:.1f},{y + s * 12} L{x2:.1f},{y + s * 12} L{x2:.1f},{y}" '
              f'fill="none" stroke="#475569" stroke-width="1.6"/>')
        f.pill((x1 + x2) / 2, y + s * 12 + (-8 if up else 26), label, INK, 17)

    brace(X0, X0 + W, BY - 8, '模型窗口 32000（教学配置）')
    brace(xs[0][0], xs[3][1], BY + BH + 8, '可用输入 24800 = 32000 − 输出预留 4000 − 安全余量 3200', up=False)

    # 下方四列明细
    cols = [('固定项 3000', 'code', ['I1 指令与契约 2200', 'T1 工具定义 800'], '必须全部放下'),
            ('必需项 3500', 'external', ['S1 任务状态 600', 'Q1 当前问题 200', 'E1 指标 900', 'E2 发布记录 400',
                                       'E3 日志聚合 1400'], '放不下则不调用模型'),
            ('弹性项 10400', 'state', ['H1 近三轮对话 2500', 'M1 服务依赖说明 700', 'E4 日志样本 A 6000',
                                     'M2 同类处置经验 1200'], '按优先级整条选入'),
            ('未纳入', 'risk', ['X1 其他租户记忆', '原因：租户不符', 'H2 早期对话摘要', '原因：超历史上限',
                              'E5 日志样本 B 9000', '原因：超剩余预算'], '记入清单与原因')]
    CW, GAP, CY = 222, 10, 272
    for i, (t, kind, lines, foot) in enumerate(cols):
        cx = X0 + i * (CW + GAP)
        lines = list(lines) + [''] * (6 - len(lines))  # 补齐行数，四列内容顶端对齐
        f.card(cx, CY, CW, t, lines, kind=kind, h=222, align='left', tsize=18, lsize=17, pad=16)
        f.text(cx + 16, CY + 222 + 28, foot, 17, SUB)
    lx = f.legend(40, 576, ['code', 'external', 'state', 'model', 'risk'], neutral=False)
    f.raw(f'<rect x="{lx}" y="{576 - 13}" width="22" height="16" rx="4" fill="#ffffff" stroke="#cbd5e1" '
          f'stroke-width="1.5" stroke-dasharray="4 3"/>')
    f.text(lx + 30, 576, '未用与余量', 17, SUB)
    f.save('08-context-budget.svg')


def pipeline():
    f = Figure(1000, 940, '图 8-2 上下文组装流水线',
               '候选材料先包封来源与可信等级，再按认证上下文过滤范围与有效期，按固定、必需、弹性分配预算，'
               '需要时生成带来源的压缩材料，按稳定前缀在前、当前问题在后的顺序组装，最后记录纳入与丢弃的清单。'
               '必需项放不下时返回待审结果，不调用模型。', label='图 8-2｜上下文组装流水线：从候选材料到调用清单')
    f.group(30, 88, 940, 150, '候选材料', kind='state')
    f.pill(150, 94, '每条都带 ID、来源、时间与可信等级', SUB, 17, anchor='start')
    srcs = [('指令与输出契约', 'code'), ('工具定义', 'code'), ('任务状态', 'state'), ('当前问题', 'human'),
            ('工具结果', 'external'), ('检索材料（第 9 章）', 'external'), ('长期记忆', 'state'), ('会话历史', 'state')]
    for i, (t, kind) in enumerate(srcs):
        r, c = divmod(i, 4)
        chip(f, 54 + c * 228, 116 + r * 56, t, kind=kind, w=208)
    X, W = 325, 350
    steps = [('包封：来源、时间、可信等级', 'code'), ('范围过滤：租户、用户、有效期', 'code'),
             ('预算分配：固定 → 必需 → 弹性', 'code'), ('压缩：生成带来源的新材料', 'model'),
             ('排序：稳定前缀在前，问题在后', 'code'), ('记录清单：纳入、丢弃与原因', 'state')]
    cs, y = [], 290
    for i, (t, kind) in enumerate(steps):
        cs.append(f.card(X, y, W, t, kind=kind, badge=i + 1, h=62, align='left', tsize=18, dashed=(kind == 'model')))
        y += 62 + 32
    f.arrow((X + W / 2, 242), (X + W / 2, cs[0]['y'] - 8), style='main')
    for p, q in zip(cs, cs[1:]):
        f.arrow((X + W / 2, p['b'] + 4), (X + W / 2, q['y'] - 8), style='main')
    # 压缩产生的新材料回到预算分配
    f.arrow((cs[3]['r'] + 4, cs[3]['cy']), (cs[3]['r'] + 24, cs[3]['cy']), (cs[3]['r'] + 24, cs[2]['cy']),
            (cs[2]['r'] + 8, cs[2]['cy']), style='loop', rounded=8, towards=(cs[2]['cx'], cs[2]['cy']))
    # 左侧失败出口
    e1 = f.card(30, cs[1]['cy'] - 40, 250, '越界或过期', ['丢弃，记入清单'], kind='risk', h=80, tsize=18)
    e2 = f.card(30, cs[2]['cy'] - 40, 250, '必需项放不下', ['needs_review，不调用'], kind='risk', h=80, tsize=18)
    f.arrow((X - 4, cs[1]['cy']), (e1['r'] + 8, cs[1]['cy']), style='fail')
    f.arrow((X - 4, cs[2]['cy']), (e2['r'] + 8, cs[2]['cy']), style='fail')
    f.text(155, cs[3]['cy'] - 6, '压缩可选：', 17, SUB, 'normal', 'middle')
    f.text(155, cs[3]['cy'] + 20, '规则提取优先于模型摘要', 17, SUB, 'normal', 'middle')
    # 右侧输出
    OX, OW = 716, 254
    f.group(OX, 300, OW, 460, '本次调用的上下文', kind='neutral', dashed=False)
    order = [('指令与输出契约', 'code'), ('工具定义', 'code'), ('任务状态', 'state'), ('长期记忆', 'state'),
             ('证据', 'external'), ('近期对话', 'state'), ('当前问题', 'human')]
    oy = 336
    for t, kind in order:
        chip(f, OX + 20, oy, t, kind=kind, w=OW - 40, h=44)
        oy += 44 + 12
    # 稳定前缀标注
    f.raw(f'<path d="M{OX + OW - 12},{336} L{OX + OW - 4},{336} L{OX + OW - 4},{336 + 100} L{OX + OW - 12},{336 + 100}" '
          f'fill="none" stroke="#1d4ed8" stroke-width="1.6"/>')
    f.text(OX + 20, 336 + 7 * 56 + 14, '前两项稳定，可作缓存前缀', 17, '#1d4ed8')
    f.arrow((cs[4]['r'] + 4, cs[4]['cy']), (OX - 8, cs[4]['cy']), style='main')
    audit = f.card(OX, 774, OW, '评测与审计', ['按清单复现每次调用'], kind='state', h=80, tsize=18)
    assert audit['y'] + 10 < cs[5]['cy'] < audit['b'] - 10
    f.arrow((cs[5]['r'] + 4, cs[5]['cy']), (OX - 8, cs[5]['cy']), style='flow')
    f.legend(36, 888, ['code', 'state', 'external', 'human', 'model', 'risk'])
    f.legend(36, 916, [], extra=[('main', '处理顺序'), ('fail', '失败出口'), ('loop', '压缩后回到第 3 步重新分配')], neutral=False)
    f.save('08-assembly-pipeline.svg')


def memory():
    f = Figure(1000, 860, '图 8-3 记忆写入与读取的控制点',
               '写入路径：用户陈述、权威系统记录、人工确认的结论和模型推断都先经过写入前系统校验，结果分为拒绝、待审、接受；'
               '模型推断最多进入待审。读取路径：范围取自认证上下文，只读可信、未过期的最新版本，作为带来源的数据进入预算分配。'
               '删除请求要同时清理摘要、索引、缓存等派生副本。', label='图 8-3｜记忆写入与读取的控制点')
    f.text(36, 92, '写入路径', 18, INK, '600')
    srcs = [('用户陈述', '偏好、更正', 'human'), ('权威系统记录', '带有效期', 'external'),
            ('人工确认的结论', '事故关闭后', 'human'), ('模型推断与摘要', '最多进入待审', 'model')]
    sc = []
    for i, (t, l, kind) in enumerate(srcs):
        sc.append(f.card(30, 112 + i * 90, 220, t, [l], kind=kind, h=74, tsize=18, dashed=(kind == 'model')))
    chk = f.card(320, 112, 330, '写入前系统校验',
                 ['范围取自认证上下文', '来源引用必须存在', '来源与记忆类型匹配', '有效期与内容大小', '指令样式内容标记待审'],
                 kind='code', h=344, align='left', strong=True)
    for c in sc:
        assert chk['y'] + 10 < c['cy'] < chk['b'] - 10
        f.arrow((c['r'] + 4, c['cy']), (chk['x'] - 8, c['cy']), style='model' if c is sc[3] else 'flow',
                towards=(chk['cx'], chk['cy']))
    outs = [('拒绝', '记录原因，不写入', 'risk'), ('待审', '人工确认后才可读取', 'human'),
            ('接受', '写入新版本，旧版标为替换', 'state')]
    oc = []
    for i, (t, l, kind) in enumerate(outs):
        oc.append(f.card(730, 120 + i * 116, 240, t, [l], kind=kind, h=84, tsize=18))
    for i, c in enumerate(oc):
        f.arrow((chk['r'] + 4, c['cy']), (c['x'] - 8, c['cy']), style='fail' if i == 0 else 'main')
    SY = 500
    store = f.card(250, SY, 480, '记忆存储', ['命名空间：租户 / 用户或团队 / 用途', '每条：来源、版本、有效期、状态'],
                   kind='state', h=96, tsize=19)
    acc = oc[2]
    f.arrow((acc['cx'], acc['b'] + 4), (acc['cx'], 478), (store['r'] - 50, 478), (store['r'] - 50, store['y'] - 8),
            style='main', towards=(store['cx'], store['cy']))
    dl = f.card(30, SY + 8, 180, '删除请求', ['用户或合规要求'], kind='human', h=80, tsize=18)
    f.arrow((dl['r'] + 4, dl['cy']), (store['x'] - 8, dl['cy']), style='fail')
    der = f.card(790, SY, 180, '派生副本', ['摘要、索引、缓存', '需要同步清除'], kind='state', h=96, tsize=18, dashed=True)
    f.arrow((store['r'] + 4, store['cy']), (der['x'] - 8, store['cy']), style='fail')
    f.raw(f'<path d="M30,{SY + 126} L970,{SY + 126}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="6 6"/>')
    f.text(36, SY + 162, '读取路径', 18, INK, '600')
    RY = SY + 182
    reads = [('当前任务', ['认证上下文给出', '租户与用户'], 'code'), ('按命名空间查询', ['越界条目查不到'], 'code'),
             ('过滤', ['仅可信、未过期', '最新版本'], 'code'), ('进入预算分配', ['作为带来源的数据'], 'code')]
    rc = []
    for i, (t, l, kind) in enumerate(reads):
        rc.append(f.card(30 + i * 240, RY, 210, t, l, kind=kind, h=100, tsize=18))
    for p, q in zip(rc, rc[1:]):
        f.arrow((p['r'] + 4, p['cy']), (q['x'] - 8, q['cy']), style='main')
    f.arrow((rc[1]['cx'], rc[1]['y'] - 4), (rc[1]['cx'], store['b'] + 8), style='flow',
            towards=(rc[1]['cx'], store['cy']))
    f.legend(36, 836, ['human', 'external', 'model', 'code', 'state', 'risk'], extra=[('fail', '拒绝与删除')])
    f.save('08-memory-control.svg')


if __name__ == '__main__':
    budget()
    pipeline()
    memory()
