"""第一篇小结插图：图 P1-1 AI 应用参考架构。"""
from figlib import Figure


def reference_architecture():
    f = Figure(1000, 812, '图 P1-1 AI 应用参考架构',
               '入口与身份之下是由代码负责的应用控制面；模型服务只经模型网关调用，知识检索经上下文组装按权限取用，'
               '工具执行器只在策略与授权放行后执行；评测与观测贯穿各层。', label='图 P1-1｜AI 应用参考架构')
    X0, W = 30, 780
    IX, IW = X0 + 18, W - 36
    cw = (IW - 48) / 4
    col = [IX + i * (cw + 16) for i in range(4)]
    top = f.card(X0, 70, W, '入口与身份', ['认证、租户、会话与限流；身份由系统注入下游，不经模型转述'], kind='code')
    gy = top['b'] + 44
    f.group(X0, gy, W, 364, '应用控制面：确定性骨架，由代码负责', 'code')
    f.arrow((X0 + W / 2, top['b']), (X0 + W / 2, gy - 18))
    band_y = gy + 30
    f.raw(f'<rect x="{IX}" y="{band_y}" width="{IW}" height="40" rx="20" fill="#ffffff" stroke="#93c5fd" stroke-width="1.2"/>')
    f.text(X0 + W / 2, band_y + 26, '关键路径：模型提议 → 系统校验 → 策略裁决 → 工具执行 → 结果核对', 17, '#1d4ed8', '600', 'middle')
    ra = band_y + 56
    f.card(col[0], ra, cw * 2 + 16, '编排', ['固定流程 / 工作流 / 智能体循环', '持有预算、终止权与失败出口'], kind='neutral')
    f.card(col[2], ra, cw, '任务状态', ['阶段与版本', '操作标识与结果'], kind='state')
    f.card(col[3], ra, cw, '人工协作', ['审阅与审批', '接手与交接'], kind='human')
    rb = ra + 126
    mg = f.card(col[0], rb, cw, '模型网关', ['适配与超时', '用量与版本'], kind='code')
    cx = f.card(col[1], rb, cw, '上下文组装', ['选择指令与材料', '标注来源与版本'], kind='neutral')
    f.card(col[2], rb, cw, '系统校验', ['格式与 Schema', '业务约束与引用'], kind='code')
    po = f.card(col[3], rb, cw, '策略与授权', ['主体、资源、动作', '审批绑定参数'], kind='code')
    cy = gy + 364 + 64
    ms = f.card(col[0], cy, cw, '模型服务', ['只返回候选', '不持有业务凭证'], kind='model')
    kb = f.card(col[1], cy, cw, '知识与检索', ['索引与查询', '保留版本与范围'], kind='external')
    te = f.card(col[3], cy, cw, '工具执行器', ['契约、幂等、审计', '可经 MCP 接入'], kind='external')
    f.arrow((mg['cx'], mg['b']), (ms['cx'], ms['y'] - 4), style='main', label='唯一调用出口', at=(mg['cx'], gy + 364 + 30))
    f.arrow((cx['cx'], cx['b']), (kb['cx'], kb['y'] - 4), style='main', label='按权限检索', at=(cx['cx'], gy + 364 + 30))
    f.arrow((po['cx'], po['b']), (te['cx'], te['y'] - 4), style='main', label='放行后才执行', at=(po['cx'], gy + 364 + 30))
    f.text(col[2] + cw / 2, cy + 46, '外部业务系统', 17, '#475569', anchor='middle')
    f.text(col[2] + cw / 2, cy + 72, '只经工具执行器访问', 17, '#475569', anchor='middle')
    f.arrow((te['x'], te['cy']), (col[2] + cw - 8, te['cy']), style='flow')
    # 评测与观测：贯穿各层的侧栏
    sx, sw = 836, 140
    f.card(sx, 70, sw, '评测与观测', ['贯穿各层', '', '任务集与判定', '调用链追踪', '成本与延迟', '失败样例回流'], kind='state', h=ms['b'] - 70)
    for yy in (top['cy'], gy + 176, ms['cy']):
        f.raw(f'<path d="M{X0 + W},{yy} L{sx},{yy}" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 4"/>')
        f.raw(f'<circle cx="{sx}" cy="{yy}" r="4" fill="#94a3b8"/>')
    f.legend(30, ms['b'] + 56, ['code', 'model', 'external', 'human', 'state'], extra=[('main', '受约束的调用路径')])
    f.save('p1-reference-architecture.svg')


if __name__ == '__main__':
    reference_architecture()
