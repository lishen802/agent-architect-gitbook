"""第 5 章插图：图 5-1 最小链路与四种出口。"""
from figlib import Figure


def minimal_chain():
    f = Figure(1000, 760, '图 5-1 最小链路与四种出口',
               '读取并校验证据包、检查空证据、构造输入、在截止时间内调用模型、检查完整性、校验业务约束；'
               '各阶段分别提前落到 invalid_input、needs_review、unavailable，全部通过才返回 draft。',
               label='图 5-1｜告警助手的最小链路与四种出口')
    steps = [('读取并校验证据包', 'code'), ('检查证据是否为空', 'code'), ('构造任务指令与输入', 'neutral'),
             ('在截止时间内调用模型', 'model'), ('检查生成是否完整', 'code'), ('解析并校验业务约束', 'code')]
    cs = []
    y = 80
    for i, (t, k) in enumerate(steps):
        cs.append(f.card(60, y, 400, t, kind=k, badge=i + 1, align='left', h=56))
        y += 86
    for p, q in zip(cs, cs[1:]):
        f.arrow((p['cx'], p['b']), (q['cx'], q['y'] - 4))
    dr = f.card(60, y + 10, 400, 'draft：待审阅草稿', ['展示报告与证据，等待人工审阅'], kind='human', strong=True)
    f.arrow((cs[-1]['cx'], cs[-1]['b']), (dr['cx'], dr['y'] - 4), style='ok', label='assessment = draft',
            at=(cs[-1]['cx'] - 14, (cs[-1]['b'] + dr['y']) / 2 + 6), anchor='end')
    e1 = f.card(560, cs[0]['y'] - 10, 410, 'invalid_input', ['证据包不满足输入约定，要求调用方修正'], kind='risk')
    f.arrow((cs[0]['r'], cs[0]['cy']), (e1['x'] - 4, cs[0]['cy']), style='fail')
    e2 = f.card(560, cs[1]['y'] + 8, 410, 'needs_review · no_evidence', ['不调用模型，交给人工补充材料'], kind='human')
    f.arrow((cs[1]['r'], cs[1]['cy']), (510, cs[1]['cy']), (510, e2['cy']), (e2['x'] - 4, e2['cy']), style='flow')
    top, bot = cs[3]['cy'] - 40, cs[5]['cy'] + 40
    e3 = f.card(560, top, 410, 'unavailable', ['超时或服务错误', '截断或拒绝', '输出不合格（invalid_output）'],
                kind='risk', h=bot - top)
    for c in cs[3:6]:
        f.arrow((c['r'], c['cy']), (e3['x'] - 4, c['cy']), style='fail')
    e4 = f.card(560, dr['y'], 410, 'needs_review · insufficient_data', ['模型报告材料不足，展示信息缺口'], kind='human', h=dr['h'])
    f.arrow((cs[-1]['cx'] + 150, cs[-1]['b']), (cs[-1]['cx'] + 150, dr['y'] - 24), (520, dr['y'] - 24), (520, e4['cy']),
            (e4['x'] - 4, e4['cy']), style='flow')
    f.legend(36, dr['b'] + 46, ['code', 'model', 'human', 'risk'], extra=[('main', '主路径'), ('fail', '提前结束')])
    f.save('05-minimal-chain.svg')


if __name__ == '__main__':
    minimal_chain()
