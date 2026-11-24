"""第 4 章插图：图 4-1 一次调用的四层结果。"""
from figlib import Figure


def four_layers():
    f = Figure(1000, 680, '图 4-1 一次调用的四层结果',
               '调用完成、生成完整、契约有效由程序判定，任何一层失败都返回 unavailable；'
               '任务有效由评测与人工审阅判定，未达标时记录失败并回到设计。', label='图 4-1｜一次调用的四层结果')
    f.group(30, 84, 520, 400, '程序在运行时判定', 'code')
    f.group(30, 516, 520, 120, '评测与人工审阅判定', 'human')
    specs = [('调用完成', ['服务端返回，客户端能读取']),
             ('生成完整', ['没有截断、拒绝或异常结束']),
             ('契约有效', ['字段、类型与应用规则成立'])]
    left = []
    y = 116
    for i, (t, l) in enumerate(specs):
        left.append(f.card(56, y, 468, t, l, kind='code', badge=i + 1, align='left'))
        y += 122
    last = f.card(56, 540, 468, '任务有效', ['内容确实帮助值班人员完成工作'], kind='human', badge=4, align='left')
    for p, q in zip(left, left[1:] + [last]):
        f.arrow((p['cx'], p['b']), (q['cx'], q['y'] - 4), label='是', at=(p['cx'] + 30, (p['b'] + q['y']) / 2 + 6))
    fails = [('调用失败', ['超时、鉴权、限流 → unavailable']),
             ('截断或拒绝', ['半份结果不当作完成 → unavailable']),
             ('契约不符', ['invalid_output → unavailable'])]
    for p, (t, l) in zip(left, fails):
        c = f.card(612, p['y'], 358, t, l, kind='risk', h=p['h'])
        f.arrow((p['r'], p['cy']), (c['x'] - 4, c['cy']), style='fail', label='否', at=(582, p['cy'] - 12))
    c = f.card(612, last['y'], 358, '任务未达标', ['记录失败原因，回到提示、材料或设计'], kind='risk', h=last['h'])
    f.arrow((last['r'], last['cy']), (c['x'] - 4, c['cy']), style='fail', label='否', at=(582, last['cy'] - 12))
    f.legend(36, 664, ['code', 'human', 'risk'], extra=[('main', '通过'), ('fail', '失败去向')])
    f.save('04-four-layers.svg')


if __name__ == '__main__':
    four_layers()
