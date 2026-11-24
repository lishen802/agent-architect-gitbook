"""第 6 章插图：图 6-1 评测闭环；图 6-2 分母漏斗。"""
import math
from figlib import Figure, edge_point, text_width


def eval_loop():
    f = Figure(1000, 700, '图 6-1 评测闭环',
               '需求与验收规则、检查项与判定方法、任务集、候选结果、逐项判定、带分母的汇总、设计调整依次相连；'
               '设计调整后补题并重新运行全部任务，规则含糊时回到需求修订规则。', label='图 6-1｜评测闭环')
    nodes = [('需求与验收规则', '先写什么算通过', 'human'),
             ('检查项与判定方法', '程序/人工/模型辅助', 'code'),
             ('任务集', '开发题与保留题分开', 'state'),
             ('候选结果', '保留每次试验与版本', 'model'),
             ('逐项判定', '写明理由，允许待定', 'code'),
             ('带分母的汇总', '对象与分母写清', 'state'),
             ('设计调整', '一次只改一处', 'human')]
    CX, CY, RX, RY = 500, 368, 350, 222  # 卡片宽 232，相邻卡片至少留出约 40px
    cs = []
    for i, (t, l, k) in enumerate(nodes):
        a = math.radians(-90 + 360 / 7 * i)
        x, y = CX + RX * math.cos(a), CY + RY * math.sin(a)
        cs.append(f.card(x - 116, y - 44, 232, t, [l], kind=k, badge=i + 1, align='left', h=88))
    for i in range(6):
        p, q = cs[i], cs[i + 1]
        f.arrow(edge_point(p, q['cx'], q['cy']), edge_point(q, p['cx'], p['cy'], 8), style='main',
                towards=(q['cx'], q['cy']))
    p, q = cs[6], cs[2]
    f.arrow(edge_point(p, q['cx'], q['cy']), edge_point(q, p['cx'], p['cy'], 8), style='loop',
            towards=(q['cx'], q['cy']), label='补题后重新运行全部任务', at=(CX + 10, CY + 10))
    p, q = cs[6], cs[0]
    f.arrow((p['cx'], p['y'] - 4), (p['cx'], q['cy']), (q['x'] - 8, q['cy']), style='loop',
            label='规则含糊：修订并升版本', at=(p['cx'], q['cy'] - 30))
    f.legend(36, 676, ['human', 'code', 'state', 'model'], extra=[('main', '每轮顺序'), ('loop', '回路')])
    f.save('06-eval-loop.svg')


def denominator():
    f = Figure(1000, 548, '图 6-2 分母漏斗',
               '计划 6 题，完成生成 5 题，返回报告的契约检查 5 题全部通过，任务通过只有 T02、T05 两题；'
               '只汇报 5/5 会掩盖 T06 的超时和 T01、T03、T04 的语义失败。', label='图 6-2｜分母漏斗：同一批记录的四个口径')
    ids = ['T01', 'T02', 'T03', 'T04', 'T05', 'T06']
    X0, CW = 250, 96
    for i, t in enumerate(ids):
        f.text(X0 + i * CW + 44, 96, t, 17, '#475569', '600', 'middle')
    P = ('#e6f7f4', '#2dd4bf', '#0f766e')
    F = ('#fef2f2', '#f87171', '#b91c1c')
    N = ('#f1f5f9', '#cbd5e1', '#94a3b8')
    S = ('#ffffff', '#94a3b8', '#334155')
    rows = [('计划任务', [S] * 6, '6 / 6', None),
            ('完成生成', [P] * 5 + [F], '5 / 6', {5: '超时'}),
            ('报告契约通过', [P] * 5 + [N], '5 / 5', {5: '无报告'}),
            ('任务通过', [F, P, F, F, P, F], '2 / 6', {0: '因果', 2: '冲突', 3: '范围', 5: '超时'})]
    y = 112
    for name, cells, cnt, notes in rows:
        f.text(36, y + 36, name, 18, '#1e293b', '600')
        for i, (fill, stroke, ink) in enumerate(cells):
            dash = ' stroke-dasharray="5 4"' if fill == N[0] else ''
            f.raw(f'<rect x="{X0 + i * CW}" y="{y}" width="{CW - 8}" height="54" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
            mark = (notes or {}).get(i)
            word = {'计划任务': '列入', '完成生成': '完成', '报告契约通过': '有效', '任务通过': '通过'}[name]
            sym = mark or ('' if fill == N[0] else word)
            f.text(X0 + i * CW + 44, y + 33, sym, 17, ink, '600', 'middle')
        f.text(880, y + 36, cnt, 20, '#1e293b', '700', 'middle')
        y += 78
    f.card(250, 434, 720, '', ['只报“5 / 5 契约通过”，会掩盖 1 次超时与 3 份语义失败的报告'], kind='risk', align='left', h=48)
    # 图例与上方说明框留出 32px
    LY = 514
    items = [(('#ffffff', '#94a3b8', ''), '已列入计划'), (P, '满足本层口径'), (F, '失败'),
             (('#f1f5f9', '#cbd5e1', ' stroke-dasharray="5 4"'), '未进入这一层')]
    lx = 36
    for (fill, stroke, extra), name in items:
        extra = extra if extra.startswith(' ') else ''
        f.raw(f'<rect x="{lx}" y="{LY}" width="22" height="16" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{extra}/>')
        f.text(lx + 30, LY + 13, name, 17, '#475569')
        lx += 30 + text_width(name, 17) + 24
    f.save('06-denominator.svg')


if __name__ == '__main__':
    eval_loop()
    denominator()
