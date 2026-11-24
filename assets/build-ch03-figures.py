"""第 3 章插图：图 3-1 四种“记忆”的层次与归属；图 3-2 超时背后的时间差。"""
from figlib import Figure, text_width


def memory_layers():
    f = Figure(1000, 576, '图 3-1 四种“记忆”的层次与归属',
               'KV Cache 只存在于推理计算内部，上下文只服务一次调用，任务状态贯穿一个任务并可作为执行依据，'
               '应用记忆跨任务保留但使用前要核对来源与时效。', label='图 3-1｜四种“记忆”的层次与归属')
    zones = ['生成内部', '单次调用', '单个任务', '跨任务']
    X0, ZW = 360, 152
    for i, z in enumerate(zones):
        x = X0 + i * ZW
        f.raw(f'<rect x="{x}" y="76" width="{ZW - 6}" height="370" rx="10" fill="#ffffff" stroke="#e2e8f0"/>')
        f.text(x + (ZW - 6) / 2, 102, z, 17, '#475569', '600', 'middle')
    rows = [('KV Cache', ['推理中间计算的复用'], 'model', 0, 1, '推理服务持有'),
            ('上下文', ['本次调用可用的输入'], 'neutral', 1, 1, '应用组装'),
            ('任务状态', ['推进任务的显式记录'], 'state', 1, 2, '应用持有，可作执行依据'),
            ('应用记忆', ['为未来任务保留的信息'], 'state', 1, 3, '应用持有，用前核对时效')]
    y = 124
    for t, l, k, z0, n, holder in rows:
        c = f.card(30, y, 300, t, l, kind=k, align='left', h=76)
        fill, stroke = {'model': ('#fde7c4', '#f59e0b'), 'neutral': ('#e2e8f0', '#94a3b8'),
                        'state': ('#dbe3ec', '#64748b')}[k]
        bx, bw = X0 + z0 * ZW + 8, n * ZW - 22
        f.raw(f'<rect x="{bx}" y="{y + 18}" width="{bw}" height="40" rx="20" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        f.text(bx + bw / 2, y + 44, holder, 17, '#1e293b', '600', 'middle', maxw=bw - 16)
        f.raw(f'<path d="M{c["r"]},{c["cy"]} L{bx - 4},{c["cy"]}" stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="3 4"/>')
        y += 84
    f.card(30, 464, 940, '', ['只有任务状态中经过校验的事实，才能作为审批与执行的依据；其余三种都要按来源和时效重新核对'],
           kind='code', align='left', h=50)
    f.legend(36, 552, ['model', 'state', 'code'])
    f.save('03-memory-layers.svg')


def timeout_gap():
    f = Figure(1000, 640, '图 3-2 超时背后的时间差',
               '应用发出创建工单请求，工单系统已经创建记录，响应在网络中丢失，应用只观察到超时；'
               '直接重试可能重复创建，直接判定失败会漏掉已建工单，应按操作标识查询后再决定。', label='图 3-2｜超时背后的时间差')
    lanes = [('应用', 80), ('网络', 180), ('工单系统', 280)]
    for name, y in lanes:
        f.raw(f'<rect x="30" y="{y}" width="940" height="92" rx="12" fill="#ffffff" stroke="#e2e8f0"/>')
        f.raw(f'<rect x="30" y="{y}" width="118" height="92" rx="12" fill="#f1f5f9" stroke="#e2e8f0"/>')
        f.text(89, y + 52, name, 18, '#334155', '600', 'middle')
    a = f.card(170, 100, 170, '① 发出创建请求', kind='neutral', h=52, tsize=17)
    b = f.card(390, 300, 170, '② 已创建记录', kind='external', h=52, tsize=17)
    c = f.card(600, 200, 150, '③ 响应丢失', kind='risk', h=52, tsize=17)
    d = f.card(790, 100, 160, '④ 观察到超时', kind='risk', h=52, tsize=17)
    f.arrow((a['cx'], a['b']), (a['cx'], b['cy']), (b['x'] - 4, b['cy']), style='main')
    f.arrow((b['r'], b['cy']), (c['cx'], b['cy']), (c['cx'], c['b'] + 4), style='fail')
    f.arrow((c['r'], c['cy']), (d['cx'], c['cy']), (d['cx'], d['b'] + 4), style='loop', label='等待截止', at=(d['cx'] - 2, c['cy'] - 42))
    f.arrow((150, 394), (960, 394), style='flow')
    f.text(940, 420, '时间', 17, '#475569', anchor='end')
    by = 440
    f.text(36, by + 20, '恢复时的三种做法', 18, '#334155', '600')
    o1 = f.card(30, by + 40, 296, '直接重试', ['工单可能被重复创建'], kind='risk')
    o2 = f.card(352, by + 40, 296, '直接判定失败', ['漏掉已经创建的工单'], kind='risk')
    o3 = f.card(674, by + 40, 296, '按操作标识查询再决定', ['已创建 / 未创建 / 不可知'], kind='code', strong=True)
    f.legend(36, 622, ['external', 'code', 'risk'], extra=[('main', '请求'), ('fail', '响应丢失')])
    f.save('03-timeout-gap.svg')


if __name__ == '__main__':
    memory_layers()
    timeout_gap()
