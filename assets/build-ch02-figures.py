"""第 2 章插图：图 2-1 从需求到方案的分层选型图。"""
from figlib import Figure


def decision_map():
    f = Figure(1000, 1008, '图 2-1 从需求到方案的分层选型图',
               '先明确任务与验收、比较无需模型的基线，再选择控制方式；信息获取、动作与授权、状态与恢复分别决定；'
               '最后形成一页方案并用最小实验验证，不满足时回到对应决策。', label='图 2-1｜从需求到方案的分层选型图')
    a = f.card(70, 76, 900, '明确任务与验收', ['使用者、交付物、错误后果，以及无法判断时的出口'], kind='neutral', badge=1, align='left')
    b = f.card(70, a['b'] + 36, 900, '先比较无需模型的基线', ['规则、查询、搜索或模板能否满足目标？不足时写明模型要补哪一项能力'],
               kind='neutral', badge=2, align='left')
    f.arrow((520, a['b']), (520, b['y'] - 4))
    g3 = b['b'] + 56
    f.group(70, g3, 900, 170, '③ 选择控制方式：可以组合，按任务证据选择', 'state')
    specs = [('规则程序', ['规则可明确表达', '校验、计算、提交'], 'code'),
             ('受控模型调用', ['材料已给定', '理解、抽取或生成'], 'model'),
             ('预定义工作流', ['阶段与转移可描述', '可含模型与等待'], 'neutral'),
             ('受约束的智能体', ['下一步依赖新证据', '需反馈、预算与退出'], 'model')]
    for i, (t, l, k) in enumerate(specs):
        f.card(90 + i * 220, g3 + 34, 200, t, l, kind=k)
    f.arrow((520, b['b']), (520, g3 - 18))
    g4 = g3 + 170 + 50
    f.group(70, g4, 900, 170, '④ 独立补齐三个维度：任一种控制方式都可能需要', 'state')
    specs = [('信息获取', ['给定材料 / 业务查询 / 检索', '权限、来源、时效与缺口'], 'external'),
             ('动作与授权', ['只读 / 建议 / 受控写操作', '按后果决定是否审批'], 'code'),
             ('状态与恢复', ['任务事实与操作标识', '超时后先核对再重试'], 'state')]
    for i, (t, l, k) in enumerate(specs):
        f.card(90 + i * 295, g4 + 34, 270, t, l, kind=k)
    f.arrow((520, g3 + 170), (520, g4 - 18))
    e = f.card(70, g4 + 170 + 44, 900, '形成一页方案，用最小实验验证',
               ['写明候选与不选理由、判定方法、成本与延迟假设、会推翻当前选择的结果'], kind='human', badge=5, align='left', strong=True)
    f.arrow((520, g4 + 170), (520, e['y'] - 4))
    ly = e['b'] + 34
    f.arrow((300, e['b']), (300, ly), (40, ly), (40, g4 + 85), (66, g4 + 85), style='loop',
            label='质量或预算不满足：回到对应决策修正', at=(560, ly + 6))
    f.raw(f'<path d="M40,{g4 + 85} L40,{g3 + 85}" stroke="#64748b" stroke-width="2" fill="none" stroke-dasharray="7 5"/>')
    f.arrow((40, g3 + 85), (66, g3 + 85), style='loop')
    f.legend(40, ly + 50, ['code', 'model', 'external', 'human', 'state'], neutral=False)
    f.legend(40, ly + 78, [], extra=[('main', '设计顺序'), ('loop', '回路')])
    f.save('02-decision-map.svg')


if __name__ == '__main__':
    decision_map()
