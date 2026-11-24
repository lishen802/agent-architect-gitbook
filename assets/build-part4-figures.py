"""第 14、15 章插图：图 14-1 知识客服的三阶段演进；图 15-1 提交边界与结果不明的恢复。"""
from figlib import Figure, chip


def support_stages():
    f = Figure(1000, 740, '图 14-1 知识客服的三阶段演进',
               '阶段一为固定检索问答；阶段二在其上增加会话状态、澄清与转人工规则和人工交接；'
               '阶段三再增加按职责路由、业务查询接口、结构化草稿校验与确认后提交。每一阶段保留前一阶段的链路。',
               label='图 14-1｜知识客服的三阶段演进：每一阶段只增加新需求要求的部件')
    stages = [
        ('阶段一 · 知识问答', '交付：带来源的回答或缺口', [
            ('问题与身份', 'neutral'), ('确认适用范围', 'code'), ('授权范围内检索', 'external'),
            ('基于材料生成', 'model'), ('引用与结果检查', 'code'), ('回答或说明缺口', 'neutral')]),
        ('阶段二 · 多轮与转人工', '交付：可追踪的会话与交接', [
            ('阶段一链路', 'state'), ('+ 会话状态', 'state'), ('+ 澄清与转接规则', 'code'),
            ('+ 人工接手与交接', 'human')]),
        ('阶段三 · 业务办理', '交付：经核对的业务结果', [
            ('阶段二链路', 'state'), ('+ 按职责路由', 'code'), ('+ 业务查询接口', 'external'),
            ('+ 结构化草稿与校验', 'code'), ('+ 确认后提交', 'human'), ('+ 按业务记录核对', 'code')]),
    ]
    for i, (name, sub, items) in enumerate(stages):
        x = 30 + i * 320
        f.group(x, 80, 300, 560, name, kind='state')
        f.text(x + 20, 122, sub, 17, '#475569')
        y = 146
        prev = None
        for t, k in items:
            c = chip(f, x + 24, y, t, k, w=252, h=48, strong=t.startswith('+'))
            if prev:
                f.arrow((c['cx'], prev['b'] + 2), (c['cx'], c['y'] - 6), style='flow')
            prev = c
            y += 48 + 28
    f.text(36, 676, '“+” 表示本阶段新增的部件；新增依据是新的交付物，而不是对话轮数。', 17, '#475569')
    f.legend(36, 716, ['model', 'code', 'external', 'human', 'state'])
    f.save('14-support-stages.svg')


def submit_boundary():
    f = Figure(1000, 600, '图 15-1 提交边界与结果不明的恢复',
               '采购草稿经校验、必要审批与执行前核对后才能提交；条件变化时回到审批。提交结果不明时先查询与对账：'
               '已创建则进入结果核验，确认未创建且可安全重试才按同一操作标识重试，无法确认时交给人工。',
               label='图 15-1｜提交边界与结果不明的恢复')
    W, G = 210, 30
    xs = [40 + i * (W + G) for i in range(4)]
    r1 = [('需求理解', ['规格、数量、项目'], 'model'), ('草稿与校验', ['目录、权限、预算'], 'code'),
          ('必要审批', ['绑定草稿版本'], 'human'), ('执行前核对', ['商品、金额、条件'], 'code')]
    top = [f.card(x, 112, W, t, l, kind=k, badge=i + 1, h=84, align='left') for i, (x, (t, l, k)) in enumerate(zip(xs, r1))]
    for p, q in zip(top, top[1:]):
        f.arrow((p['r'] + 4, p['cy']), (q['x'] - 8, q['cy']), style='main')
    f.arrow((top[3]['cx'], top[3]['y'] - 4), (top[3]['cx'], 80), (top[2]['cx'], 80), (top[2]['cx'], top[2]['y'] - 8),
            style='loop', label='条件变化：重新审批', at=((top[2]['cx'] + top[3]['cx']) / 2, 72))
    sub = f.card(xs[3], 270, W, '提交', ['携带操作标识'], kind='external', badge=5, h=84, align='left')
    ver = f.card(xs[2], 270, W, '结果核验', ['按业务记录确认'], kind='code', badge=6, h=84, align='left')
    done = f.card(xs[1], 270, W, '完成', ['记录订单号'], kind='state', badge=7, h=84, align='left')
    f.arrow((top[3]['cx'], top[3]['b'] + 4), (sub['cx'], sub['y'] - 8), style='main')
    f.arrow((sub['x'] - 4, sub['cy']), (ver['r'] + 8, ver['cy']), style='main')
    f.arrow((ver['x'] - 4, ver['cy']), (done['r'] + 8, done['cy']), style='ok')
    unk = f.card(xs[3], 440, W, '结果不明', ['超时或页面无反馈'], kind='risk', h=84)
    rec = f.card(xs[2], 440, W, '查询与对账', ['按操作标识或订单号'], kind='code', h=84)
    hum = f.card(xs[0], 440, W, '人工接手', ['附带已知事实'], kind='human', h=84)
    f.arrow((sub['cx'] + 60, sub['b'] + 4), (unk['cx'] + 60, unk['y'] - 8), style='fail', label='超时', at=(sub['cx'] + 60, (sub['b'] + unk['y']) / 2 + 6))
    f.arrow((unk['x'] - 4, unk['cy']), (rec['r'] + 8, rec['cy']), style='main')
    f.arrow((rec['cx'], rec['y'] - 4), (ver['cx'], ver['b'] + 8), style='ok', label='已创建', at=(rec['cx'] - 50, (rec['y'] + ver['b']) / 2 + 6))
    f.arrow((rec['r'] - 30, rec['y'] - 4), (rec['r'] - 30, (rec['y'] + ver['b']) / 2), (sub['cx'] - 40, (rec['y'] + ver['b']) / 2),
            (sub['cx'] - 40, sub['b'] + 8), style='loop')
    f.pill((rec['r'] - 30 + sub['cx'] - 40) / 2, (rec['y'] + ver['b']) / 2 + 6, '未创建：重试', '#475569')
    f.arrow((rec['x'] - 4, rec['cy']), (hum['r'] + 8, hum['cy']), style='fail', label='无法确认', at=((rec['x'] + hum['r']) / 2, rec['cy'] - 14))
    f.legend(36, 576, ['model', 'code', 'human', 'external', 'state', 'risk'])
    f.save('15-submit-boundary.svg')


if __name__ == '__main__':
    support_stages()
    submit_boundary()
