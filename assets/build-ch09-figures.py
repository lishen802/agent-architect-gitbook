"""第 9 章插图：图 9-1 知识处理链路；图 9-2 检索与回答链路；图 9-3 分层定位失败。"""
from figlib import Figure, SUB, chip


def ingest():
    f = Figure(1000, 690, '图 9-1 知识处理链路',
               '手册库与复盘库的页面依次经过解析、切分和加元数据，写入倒排索引与向量索引，向量由同一嵌入模型生成；'
               '解析发现隐藏内容或异常字符时标为待审，不入库。源系统的变更事件驱动三类同步：内容更新按文档替换全部段落，'
               '权限变化同步到段落元数据，删除覆盖向量、缓存与评测样例；版本核对比较源系统与索引中的文档版本，发现滞后。',
               label='图 9-1｜知识处理链路：从源文档到可检索、可撤回的段落')
    Y1 = 100
    src = f.card(40, Y1, 210, '源系统', ['手册库、复盘库', '页面带权限与版本'], kind='external', h=100, tsize=18)
    steps = [('解析', ['可见正文', '与文档结构']), ('切分', ['按标题、步骤', '与表格行']), ('加元数据', ['服务、版本、状态', '类型、权限、来源'])]
    cs = []
    for i, (t, l) in enumerate(steps):
        cs.append(f.card(290 + i * 235, Y1, 210, t, l, kind='code', h=100, tsize=18, badge=i + 1,
                         align='left'))
    f.arrow((src['r'] + 4, src['cy']), (cs[0]['x'] - 8, src['cy']), style='main')
    for p, q in zip(cs, cs[1:]):
        f.arrow((p['r'] + 4, p['cy']), (q['x'] - 8, q['cy']), style='main')
    Y2 = 270
    risk = f.card(110, Y2, 200, '隐藏内容或异常', ['标为待审，不入库'], kind='risk', h=90, tsize=18)
    f.arrow((cs[0]['x'] + 50, cs[0]['b'] + 4), (cs[0]['x'] + 50, risk['cy']), (risk['r'] + 8, risk['cy']),
            style='fail', rounded=8, towards=(risk['cx'], risk['cy']))
    store = f.card(650, Y2, 320, '知识索引', ['倒排索引：BM25', '向量索引：嵌入向量', '段落带 doc_id 与版本'],
                   kind='state', h=130, tsize=18, badge=4, align='left')
    model = f.card(420, Y2 + 20, 190, '嵌入模型', ['入库与查询同一个'], kind='model', h=90, tsize=18)
    f.arrow((cs[2]['cx'], cs[2]['b'] + 4), (cs[2]['cx'], store['y'] - 8), style='main')
    assert model['x'] + 20 < cs[1]['x'] + 60 < model['r'] - 20, '生成向量的箭头应落在嵌入模型卡片上'
    f.arrow((cs[1]['x'] + 60, cs[1]['b'] + 4), (cs[1]['x'] + 60, model['y'] - 8), style='model',
            towards=(model['cx'], model['cy']))
    f.arrow((model['r'] + 4, model['cy']), (store['x'] - 8, model['cy']), style='model')
    # 源系统变更
    GY = 470
    f.group(30, GY, 940, 120, '源系统变更与核对', kind='state')
    f.arrow((70, src['b'] + 4), (70, GY - 18), style='flow', label='变更事件', at=(70, 438), anchor='start',
            towards=(70, GY + 60))
    sync = [('内容更新', ['按文档替换全部段落'], 'code'), ('权限变化', ['同步段落的访问范围'], 'code'),
            ('删除', ['向量、缓存、评测样例'], 'code'), ('版本核对', ['源版本对比索引版本'], 'code')]
    sc = []
    for i, (t, l, kind) in enumerate(sync):
        sc.append(f.card(48 + i * 230, GY + 24, 214, t, l, kind=kind, h=80, tsize=18))
    f.arrow((store['cx'] + 60, GY - 4), (store['cx'] + 60, store['b'] + 8), style='flow', label='同步到索引',
            at=(store['cx'] + 70, GY - 30), anchor='start', towards=(store['cx'] + 60, store['cy']))
    f.legend(36, 630, ['external', 'code', 'model', 'state', 'risk'])
    f.legend(36, 660, [], extra=[('main', '处理顺序'), ('model', '生成向量'), ('flow', '变更与同步'), ('fail', '不入库')],
             neutral=False)
    f.save('09-ingest-pipeline.svg')


def query():
    f = Figure(1000, 860, '图 9-2 检索与回答链路',
               '问题与认证上下文先确定服务、版本与用户组；在权限预过滤后并行运行 BM25 与向量检索，用 RRF 融合，'
               '可选地对前 N 个候选重排；证据适用性检查排除服务或版本不符的材料，没有适用证据时返回证据不足，不生成结论；'
               '模型生成带引用的陈述，引用核对检查段落、摘录与数字，未通过的陈述退回或标为待审。各步结果写入调用清单。',
               label='图 9-2｜检索与回答链路：从问题到有依据的回答')
    X, W = 300, 400
    steps = [('确定范围：服务、版本、用户组', 'code'), ('预过滤后检索：BM25 与向量并行', 'code'),
             ('融合：RRF 按名次合并', 'code'), ('重排：前 N 个候选', 'model'),
             ('适用性检查：服务、版本、状态', 'code'), ('生成：带引用的陈述', 'model'),
             ('引用核对：段落、摘录、数字', 'code')]
    cs, y = [], 100
    for i, (t, kind) in enumerate(steps):
        cs.append(f.card(X, y, W, t, kind=kind, badge=i + 1, h=58, align='left', tsize=18, dashed=(i == 3)))
        y += 58 + 26
    for i, (p, q) in enumerate(zip(cs, cs[1:])):
        f.arrow((X + W / 2, p['b'] + 4), (X + W / 2, q['y'] - 8), style='loop' if i in (2, 3) else 'main')
    # 不重排时第 3 步直达第 5 步
    f.arrow((X - 4, cs[2]['cy'] + 14), (X - 18, cs[2]['cy'] + 14), (X - 18, cs[4]['y'] + 14), (X - 8, cs[4]['y'] + 14),
            style='main', rounded=8, towards=(cs[4]['cx'], cs[4]['cy']))
    # 左侧输入与失败出口
    q = f.card(30, cs[0]['cy'] - 45, 230, '值班人员的问题', ['带认证上下文'], kind='human', h=90, tsize=18)
    f.arrow((q['r'] + 4, cs[0]['cy']), (X - 8, cs[0]['cy']), style='main')
    f.text(145, cs[3]['cy'] - 6, '第 4 步可选，', 17, SUB, 'normal', 'middle')
    f.text(145, cs[3]['cy'] + 20, '不重排时 3 直达 5', 17, SUB, 'normal', 'middle')
    e1 = f.card(30, cs[4]['cy'] - 20, 230, '证据不足', ['说明缺口与已查范围', '不生成结论'], kind='risk', h=100, tsize=18)
    f.arrow((X - 4, cs[4]['y'] + 44), (e1['r'] + 8, cs[4]['y'] + 44), style='fail')
    e2 = f.card(30, cs[6]['cy'] - 40, 230, '未通过的陈述', ['退回重写或标为待审'], kind='risk', h=80, tsize=18)
    f.arrow((X - 4, cs[6]['cy']), (e2['r'] + 8, cs[6]['cy']), style='fail')
    assert e1['b'] + 10 < e2['y'], '左侧两个出口重叠'
    # 右侧：任务状态、索引、调用清单
    RX, RW = 740, 230
    st = f.card(RX, cs[0]['cy'] - 40, RW, '任务状态', ['服务与运行版本'], kind='state', h=80, tsize=18)
    f.arrow((st['x'] - 4, cs[0]['cy']), (X + W + 8, cs[0]['cy']), style='flow', towards=(cs[0]['cx'], cs[0]['cy']))
    idx = f.card(RX, cs[1]['cy'] - 30, RW, '知识索引', ['图 9-1'], kind='state', h=80, tsize=18)
    assert st['b'] + 6 < idx['y'], '右侧卡片重叠'
    f.arrow((idx['x'] - 4, cs[1]['cy']), (X + W + 8, cs[1]['cy']), style='flow', towards=(cs[1]['cx'], cs[1]['cy']))
    GY = cs[3]['y'] - 10
    f.group(RX - 10, GY, RW + 20, 250, '写入调用清单', kind='neutral', dashed=False)
    items = [('原问题与改写查询', 'state'), ('两路结果与名次', 'state'), ('排除的候选与原因', 'state'), ('引用核对结果', 'state')]
    for i, (t, kind) in enumerate(items):
        chip(f, RX + 10, GY + 30 + i * 52, t, kind=kind, w=RW - 20, h=42)
    gb = GY + 250
    f.arrow((X + W + 4, cs[6]['cy']), (RX + RW / 2, cs[6]['cy']), (RX + RW / 2, gb + 8), style='flow', rounded=8,
            towards=(RX + RW / 2, GY + 120))
    out = f.card(X, cs[6]['b'] + 34, W, '带引用的回答', ['陈述加带版本的链接'], kind='human', h=80, tsize=18)
    f.arrow((X + W / 2, cs[6]['b'] + 4), (X + W / 2, out['y'] - 8), style='main')
    f.legend(36, 808, ['human', 'code', 'model', 'state', 'risk'])
    f.legend(36, 836, [], extra=[('main', '处理顺序'), ('flow', '数据与记录'), ('fail', '失败出口'),
                                 ('loop', '可选的第 4 步')], neutral=False)
    f.save('09-query-pipeline.svg')


def layers():
    f = Figure(1040, 600, '图 9-3 分层定位失败',
               '一条问题依次经过四个检查点：知识库里有没有答案（人工标注），相关段落是否进入前 k 名（recall@k、MRR），'
               '是否进入上下文（从调用清单计算命中），回答是否受证据支持（忠实度与引用正确率，需语义判定）。'
               '任一检查点为否时归入对应的失败类别：知识缺失、检索失败、上下文丢失、使用失败，各有不同的修正方向。',
               label='图 9-3｜分层定位失败：先判断在哪一层出错，再决定改什么')
    W, GAP, X0, Y1 = 200, 30, 30, 110
    checks = [('知识覆盖', ['库里有答案吗？', '依据：人工标注'], 'human'),
              ('检索', ['进入前 k 名吗？', 'recall@k、MRR'], 'code'),
              ('上下文', ['进入上下文吗？', '清单中的命中'], 'code'),
              ('回答', ['受证据支持吗？', '忠实度、引用正确率'], 'human')]
    fails = [('知识缺失', ['补文档，或回答', '“没有依据”']), ('检索失败', ['改切分、分词', '或检索方式']),
             ('上下文丢失', ['查适用性规则', '与预算分配']), ('使用失败', ['改输出契约、', '上下文或模型'])]
    cc, fc = [], []
    for i, ((t, l, kind), (ft, fl)) in enumerate(zip(checks, fails)):
        x = X0 + i * (W + GAP)
        cc.append(f.card(x, Y1, W, t, l, kind=kind, h=120, tsize=18))
        fc.append(f.card(x, Y1 + 200, W, ft, fl, kind='risk', h=110, tsize=18))
        f.arrow((cc[-1]['cx'], cc[-1]['b'] + 4), (cc[-1]['cx'], fc[-1]['y'] - 8), style='fail', label='否',
                at=(cc[-1]['cx'] + 24, cc[-1]['b'] + 46), anchor='start')
    for p, q in zip(cc, cc[1:]):
        f.arrow((p['r'] + 4, p['cy']), (q['x'] - 8, q['cy']), style='main')
    ok = chip(f, cc[-1]['r'] + GAP, cc[-1]['cy'] - 20, '交付', kind='human', w=64)
    f.arrow((cc[-1]['r'] + 4, cc[-1]['cy']), (ok['x'] - 8, cc[-1]['cy']), style='main')
    assert ok['r'] < 1020, '“交付”超出画布'
    f.text(X0 + 4, 478, '标注为“无依据”的问题不计入 recall 的分母，单独检查是否返回“证据不足”。', 17, SUB)
    f.text(X0 + 4, 506, '人工一栏包括语义判定：可以由人完成，也可以由经过抽样校验的模型评分器完成。', 17, SUB)
    f.legend(36, 552, ['human', 'code', 'risk'])
    f.legend(36, 580, [], extra=[('main', '是：进入下一层'), ('fail', '否：归入失败类别')], neutral=False)
    f.save('09-eval-layers.svg')


if __name__ == '__main__':
    ingest()
    query()
    layers()
