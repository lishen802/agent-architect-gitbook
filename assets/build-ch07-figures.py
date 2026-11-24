"""第 7 章插图：图 7-1 工具执行边界；图 7-2 用操作标识核对结果不明的创建请求。"""
from figlib import Figure


def boundary():
    f = Figure(1000, 760, '图 7-1 工具执行边界',
               '固定流程生成的请求与模型提出的调用进入同一条执行路径：参数检查、授权与预算检查、执行适配器调用、结果校验与过滤，'
               '最后形成证据或明确的失败信息。主体、租户、任务标识与截止时间由系统注入，模型不可填写。',
               label='图 7-1｜工具执行边界：两种入口，一条执行路径')
    a = f.card(290, 70, 190, '固定流程', ['应用生成请求'], kind='code', h=82)
    b = f.card(500, 70, 190, '模型提议', ['工具名与参数'], kind='model', h=82)
    X, W = 290, 400
    steps = [('解析与业务参数检查', 'code'), ('身份、资源、动作与预算检查', 'code'),
             ('执行适配器调用外部系统', 'external'), ('校验结果、过滤字段、记录状态', 'code'),
             ('形成证据或明确的失败信息', 'state')]
    cs, y = [], 200
    for i, (t, k) in enumerate(steps):
        cs.append(f.card(X, y, W, t, kind=k, badge=i + 1, h=62, align='left'))
        y += 62 + 40
    mx = X + W / 2
    f.arrow((a['cx'], a['b'] + 4), (a['cx'], cs[0]['y'] - 8), style='main')
    f.arrow((b['cx'], b['b'] + 4), (b['cx'], cs[0]['y'] - 8), style='model')
    for p, q in zip(cs, cs[1:]):
        f.arrow((mx, p['b'] + 4), (mx, q['y'] - 8), style='main')
    # 左侧失败出口
    fails = [(0, '参数不合法', '反馈可公开的问题'), (1, '无权限或超预算', '拒绝，不进适配器'),
             (2, '依赖失败或部分返回', '保留缺口与状态')]
    for i, t, l in fails:
        c = cs[i]
        r = f.card(30, c['cy'] - 38, 220, t, [l], kind='risk', h=76, tsize=18)
        f.arrow((c['x'] - 4, c['cy']), (r['r'] + 8, c['cy']), style='fail')
    # 右侧系统注入
    inj = f.card(750, 200, 220, '系统注入', ['模型不可填写', '', '已认证主体', '租户范围', '任务标识', '调用截止时间', '执行侧凭证'],
                 kind='code', h=266, dashed=True)
    f.arrow((inj['x'] - 4, cs[1]['cy']), (cs[1]['r'] + 8, cs[1]['cy']), style='flow')
    f.arrow((inj['x'] - 4, cs[2]['cy']), (cs[2]['r'] + 8, cs[2]['cy']), style='flow')
    f.legend(36, 736, ['code', 'model', 'external', 'state', 'risk'],
             extra=[('main', '执行顺序'), ('fail', '失败出口')])
    f.save('07-tool-boundary.svg')


def idempotency():
    f = Figure(1000, 820, '图 7-2 用操作标识核对结果不明的创建请求',
               '应用先保存操作标识，再携带它请求工单服务。工单已创建而响应丢失时，应用只看到超时；'
               '它按同一操作标识查询，再按已创建、未创建、不可知三种结果分别处理。',
               label='图 7-2｜用操作标识核对结果不明的创建请求')
    lanes = [('应用', 180, 'code'), ('任务状态存储', 500, 'state'), ('工单服务', 820, 'external')]
    for name, x, k in lanes:
        f.card(x - 110, 66, 220, name, kind=k, h=52)
        f.raw(f'<path d="M{x},122 L{x},606" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="6 6"/>')
    A, S, T = 180, 500, 820
    y = 168
    f.arrow((A, y), (S - 8, y), style='main', label='① 保存操作标识 op-42', at=((A + S) / 2, y - 14))
    y += 70
    f.arrow((A, y), (T - 8, y), style='main', label='② 创建请求，携带 op-42', at=((S + T) / 2, y - 14))
    y += 36
    f.card(T - 120, y, 240, '③ 创建工单 #1001', ['记录 op-42'], kind='external', h=74, tsize=18)
    y += 74 + 40
    f.arrow((T, y), (A + 8, y), style='fail', label='④ 响应丢失', at=((S + T) / 2 + 60, y - 14))
    f.raw(f'<g stroke="#dc2626" stroke-width="3" stroke-linecap="round"><path d="M{S + 60},{y - 10} L{S + 80},{y + 10}"/>'
          f'<path d="M{S + 80},{y - 10} L{S + 60},{y + 10}"/></g>')
    y += 26
    f.card(A - 120, y, 240, '⑤ 超时：结果不明', ['不当作未执行'], kind='risk', h=74, tsize=18)
    y += 74 + 40
    f.arrow((A, y), (T - 8, y), style='main', label='⑥ 按 op-42 查询', at=((S + T) / 2, y - 14))
    y += 58
    f.arrow((T, y), (A + 8, y), style='ok', label='⑦ 返回 #1001 与状态', at=((S + T) / 2, y - 14))
    f.text(36, 650, '查询结果的三种处理', 18, '#334155', '600')
    outs = [('已创建', '记录工单号，不再创建', 'external'),
            ('未创建', '按约定用同一标识重试', 'code'),
            ('不可知', '保持结果不明，对账或人工', 'human')]
    for i, (t, l, k) in enumerate(outs):
        f.card(30 + i * 320, 668, 300, t, [l], kind=k, h=84)
    f.legend(36, 796, ['code', 'state', 'external', 'human', 'risk'],
             extra=[('fail', '响应丢失')])
    f.save('07-idempotency.svg')


if __name__ == '__main__':
    boundary()
    idempotency()
