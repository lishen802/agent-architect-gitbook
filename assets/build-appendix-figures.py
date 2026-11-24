"""附录 F 插图：图 F-1 十种模式结构总览；图 F-2 模式组合示例。"""
from figlib import Figure, chip, text_width

GAP = 20


def cw(s):
    return text_width(s, 17, '600') + 24


def seq(f, x, y, items, h=38):
    out = []
    for s, k in items:
        c = chip(f, x, y, s, k, w=cw(s), h=h)
        if out:
            p = out[-1]
            f.arrow((p['r'] + 2, p['cy']), (c['x'] - 6, c['cy']), style='flow')
        out.append(c)
        x = c['r'] + GAP
    return out


def fan(f, src, x, ycen, items, h=34, gap=5, w=None):
    n = len(items)
    top = ycen - (n * h + (n - 1) * gap) / 2
    w = w or max(cw(s) for s, _ in items)
    out = []
    for i, (s, k) in enumerate(items):
        c = chip(f, x, top + i * (h + gap), s, k, w=w, h=h)
        mx = (src['r'] + c['x']) / 2
        f.arrow((src['r'] + 2, src['cy']), (mx, src['cy']), (mx, c['cy']), (c['x'] - 6, c['cy']), style='flow', rounded=6)
        out.append(c)
    return out


def fan_in(f, srcs, dst):
    for s in srcs:
        mx = (s['r'] + dst['x']) / 2
        f.arrow((s['r'] + 2, s['cy']), (mx, s['cy']), (mx, dst['cy']), (dst['x'] - 6, dst['cy']), style='flow', rounded=6)


def overview():
    CW, CH, X0, Y0 = 455, 186, 30, 70
    H = Y0 + 5 * CH + 4 * 16 + 60
    f = Figure(1000, H, '图 F-1 十种模式的结构总览',
               '十个小图分别展示单次受控调用、提示链、路由、并行、编排者-执行者、评估-优化、受约束的智能体循环、'
               '检索增强生成、人工审批后执行、计划-审核-执行的基本结构。', label='图 F-1｜十种模式的结构总览')
    names = ['单次受控调用', '提示链', '路由', '并行', '编排者-执行者', '评估-优化',
             '受约束的智能体循环', '检索增强生成', '人工审批后执行', '计划-审核-执行']
    boxes = []
    for i, n in enumerate(names):
        col, row = i % 2, i // 2
        x, y = X0 + col * (CW + 30), Y0 + row * (CH + 16)
        f.card(x, y, CW, '', kind='neutral', h=CH)
        f.badge(x + 30, y + 30, i + 1)
        f.text(x + 52, y + 36, n, 19, '#1e293b', '600')
        boxes.append((x + 20, y + 58, x + CW - 20, y + CH - 14))
    M, C, E, Hm, S, N, R = 'model', 'code', 'external', 'human', 'state', 'neutral', 'risk'

    def mid(b, h=38):
        return b[1] + (b[3] - b[1] - h) / 2

    b = boxes[0]
    seq(f, b[0], mid(b), [('校验输入', C), ('模型', M), ('系统校验', C), ('结果', N)])
    b = boxes[1]
    cs = seq(f, b[0], b[1] + 8, [('模型 A', M), ('关口', C), ('模型 B', M), ('关口', C), ('结果', N)])
    fl = chip(f, cs[1]['x'] + 60, b[1] + 70, '失败或人工', R, w=cw('失败或人工'), h=34)
    for g in (cs[1], cs[3]):
        f.arrow((g['cx'], g['b'] + 2), (g['cx'], fl['cy']), (fl['x'] - 6 if g['cx'] < fl['x'] else fl['r'] + 6, fl['cy']),
                style='fail', rounded=6)
    b = boxes[2]
    src = chip(f, b[0], (b[1] + b[3]) / 2 - 19, '分类', M, w=cw('分类'))
    fan(f, src, b[0] + 140, (b[1] + b[3]) / 2, [('链路 A', N), ('链路 B', N), ('无法分类', R)])
    b = boxes[3]
    src = chip(f, b[0], (b[1] + b[3]) / 2 - 19, '输入', N, w=cw('输入'))
    outs = fan(f, src, b[0] + 120, (b[1] + b[3]) / 2, [('调用 1', M), ('调用 2', M), ('调用 3', M)])
    dst = chip(f, b[0] + 280, (b[1] + b[3]) / 2 - 19, '程序汇总', C, w=cw('程序汇总'))
    fan_in(f, outs, dst)
    b = boxes[4]
    src = chip(f, b[0], (b[1] + b[3]) / 2 - 19, '编排者', M, w=cw('编排者'))
    outs = fan(f, src, b[0] + 128, (b[1] + b[3]) / 2, [('执行者 1', M), ('执行者 n', M)], h=34, gap=14)
    dst = chip(f, b[0] + 280, (b[1] + b[3]) / 2 - 19, '编排者汇总', M, w=cw('编排者汇总'))
    fan_in(f, outs, dst)
    b = boxes[5]
    cs = seq(f, b[0], b[1] + 8, [('生成', M), ('评估', C), ('合格结果', N)])
    ly = b[1] + 80
    f.arrow((cs[1]['cx'], cs[1]['b'] + 2), (cs[1]['cx'], ly), (cs[0]['cx'], ly), (cs[0]['cx'], cs[0]['b'] + 8), style='loop', rounded=6)
    f.pill(cs[1]['r'] + 12, ly + 6, '不合格：附反馈，限轮数', anchor='start')
    b = boxes[6]
    cs = seq(f, b[0], b[1] + 8, [('模型提议', M), ('校验策略', C), ('执行', E), ('写入状态', S)])
    ly = b[1] + 80
    f.arrow((cs[3]['cx'], cs[3]['b'] + 2), (cs[3]['cx'], ly), (cs[0]['cx'], ly), (cs[0]['cx'], cs[0]['b'] + 8), style='loop', rounded=6)
    f.pill((cs[0]['cx'] + cs[3]['cx']) / 2, ly + 6, '观察后继续，直到终止条件')
    b = boxes[7]
    seq(f, b[0], mid(b), [('定范围', C), ('权限检索', E), ('生成', M), ('引用核对', C)])
    b = boxes[8]
    cs = seq(f, b[0], b[1] + 8, [('校验策略', C), ('挂起待批', Hm), ('执行前复核', C), ('执行', E)])
    f.pill(b[0], b[1] + 82, '批准绑定动作与参数版本；超时先查询结果', anchor='start')
    b = boxes[9]
    cs = seq(f, b[0], b[1] + 8, [('生成计划', M), ('逐步校验', C), ('人工审核', Hm), ('执行', N)])
    ly = b[1] + 80
    f.arrow((cs[3]['cx'], cs[3]['b'] + 2), (cs[3]['cx'], ly), (cs[0]['cx'], ly), (cs[0]['cx'], cs[0]['b'] + 8), style='loop', rounded=6)
    f.pill((cs[0]['cx'] + cs[3]['cx']) / 2, ly + 6, '执行条件变化：回到计划')
    f.legend(36, H - 24, ['model', 'code', 'external', 'human', 'state', 'risk'], extra=[('loop', '回路')])
    f.save('appf-patterns-overview.svg')


def combination():
    f = Figure(1000, 514, '图 F-2 模式组合示例',
               '用户请求先经路由（模式 3）：知识问答进入检索增强生成（模式 8）；订单查询调用业务接口后由单次受控调用解释结果（模式 1）；'
               '套餐变更生成结构化草稿，用户确认后提交（模式 9）。', label='图 F-2｜模式组合示例：第 14 章客服第三阶段')
    req = f.card(30, 176, 150, '用户请求', kind='neutral', h=60)
    rt = f.card(220, 166, 170, '路由', ['模式 3'], kind='code', h=80)
    f.arrow((req['r'] + 4, req['cy']), (rt['x'] - 8, rt['cy']), style='main')
    rows = [('知识问答', [('检索增强生成', '模式 8', 'external')]),
            ('订单查询', [('业务接口', '权威数据', 'external'), ('解释结果', '模式 1', 'model')]),
            ('套餐变更', [('结构化草稿', '系统校验', 'code'), ('确认后提交', '模式 9', 'human')])]
    for i, (name, steps) in enumerate(rows):
        y = 76 + i * 120
        a = f.card(450, y, 150, name, kind='neutral', h=60)
        mx = (rt['r'] + a['x']) / 2
        f.arrow((rt['r'] + 4, rt['cy']), (mx, rt['cy']), (mx, a['cy']), (a['x'] - 8, a['cy']), style='main')
        prev, x = a, 640
        for t, l, k in steps:
            c = f.card(x, y - 10, 160, t, [l], kind=k, h=80)
            f.arrow((prev['r'] + 4, prev['cy']), (c['x'] - 8, c['cy']), style='main')
            prev, x = c, x + 180
    f.card(30, 404, 940, '', ['只读诊断要按查询结果决定下一项检查时，才评估模式 7'], kind='state', h=52, dashed=True, align='left')
    f.legend(36, 492, ['code', 'model', 'external', 'human', 'state'])
    f.save('appf-pattern-combination.svg')


if __name__ == '__main__':
    overview()
    combination()
