"""导读插图：图 0-1 全书地图。"""
from figlib import Figure


def book_map():
    f = Figure(1000, 640, '图 0-1 全书地图',
               '六篇二十三章的阅读顺序与各篇产出；下方是贯穿案例告警助手从只读草稿到综合演进的路线。',
               label='图 0-1｜全书地图：六篇的阅读顺序、产出与贯穿案例')
    parts = [('建立判断力', ['第一篇 · 第 1—3 章与小结', '产出：一页方案初稿']),
             ('构建可验证的应用', ['第二篇 · 第 4—9 章', '产出：最小应用与任务集']),
             ('设计可控的智能体', ['第三篇 · 第 10—13 章', '产出：执行与恢复设计']),
             ('场景与架构模式', ['第四篇 · 第 14—19 章', '产出：场景方案与取舍']),
             ('生产运行与治理', ['第五篇 · 第 20—22 章', '产出：发布、权限与预算设计']),
             ('综合案例与架构演进', ['第六篇 · 第 23 章', '产出：运维助手的演进记录'])]
    cs = []
    for i, (t, l) in enumerate(parts):
        r, c = divmod(i, 3)
        cs.append(f.card(30 + c * 320, 80 + r * 170, 300, t, l, kind='neutral', badge=i + 1, align='left', h=118))
    f.arrow((cs[0]['r'], cs[0]['cy']), (cs[1]['x'] - 4, cs[1]['cy']))
    f.arrow((cs[1]['r'], cs[1]['cy']), (cs[2]['x'] - 4, cs[2]['cy']))
    gy = cs[2]['b'] + 26
    f.arrow((cs[2]['cx'], cs[2]['b']), (cs[2]['cx'], gy), (cs[3]['cx'], gy), (cs[3]['cx'], cs[3]['y'] - 4))
    f.arrow((cs[3]['r'], cs[3]['cy']), (cs[4]['x'] - 4, cs[4]['cy']))
    f.arrow((cs[4]['r'], cs[4]['cy']), (cs[5]['x'] - 4, cs[5]['cy']))
    by = cs[5]['b'] + 56
    f.group(30, by, 940, 150, '贯穿案例：告警助手的演进', 'state')
    stages = [('只读草稿', ['第 4—6 章'], 'model'), ('固定取证', ['第 7 章'], 'external'),
              ('动态调查', ['第 10 章'], 'model'), ('审批执行', ['第 12 章'], 'human'), ('综合演进', ['第 23 章'], 'state')]
    sc = []
    for i, (t, l, k) in enumerate(stages):
        sc.append(f.card(52 + i * 182, by + 36, 160, t, l, kind=k, badge=i + 1, align='left'))
    for p, q in zip(sc, sc[1:]):
        f.arrow((p['r'], p['cy']), (q['x'] - 4, q['cy']), style='flow')
    f.legend(36, by + 190, ['model', 'external', 'human', 'state'], extra=[('main', '阅读顺序')])
    f.save('00-book-map.svg')


if __name__ == '__main__':
    book_map()
