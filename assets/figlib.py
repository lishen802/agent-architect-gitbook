"""本书 SVG 插图的公共绘图模块（仅依赖 Python 标准库）。

统一视觉语言：
- 画布宽 960–1040px，所有文字 >= MIN_FONT，放进 GitBook 约 740px 正文栏后等效字号不低于 12px；
- 显式浅色圆角底板（暗色主题下也不会出现透明底黑字）；
- 固定语义配色，每张图附图例：模型=橙，代码校验与策略=蓝，外部能力与结果=青，
  人工=绿，状态与存储=灰，风险与失败=红；
- 主路径 2.5px 深色实线，回路与异常路径虚线；箭头标签带底色，避免压字；
- 节点文字垂直居中、卡片高度按行数计算；超出卡片宽度的文字在生成时直接报错。
"""
import math
from html import escape
from pathlib import Path
import unicodedata

FONT = "'PingFang SC','Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC',sans-serif"
INK = '#1e293b'
SUB = '#475569'
LINE = '#334155'
MUTED = '#94a3b8'

KINDS = {
    'model':    ('#fff4e5', '#f59e0b', '#b45309', '模型'),
    'code':     ('#eaf2ff', '#60a5fa', '#1d4ed8', '代码校验与策略'),
    'external': ('#e6f7f4', '#2dd4bf', '#0f766e', '外部能力与结果'),
    'human':    ('#ecfdf3', '#4ade80', '#15803d', '人工'),
    'state':    ('#f1f5f9', '#94a3b8', '#475569', '状态与存储'),
    'risk':     ('#fef2f2', '#f87171', '#b91c1c', '风险与失败'),
    'neutral':  ('#ffffff', '#cbd5e1', '#334155', '一般步骤'),
}
ARROWS = {
    'main':  (LINE, 2.5, None),
    'flow':  ('#64748b', 2.0, None),
    'loop':  ('#64748b', 2.0, '7 5'),
    'fail':  ('#dc2626', 2.0, '7 5'),
    'ok':    ('#0f766e', 2.5, None),
    'model': ('#d97706', 2.0, '7 5'),
}


def text_width(s, size, weight='normal'):
    w = 0.0
    for c in s:
        if unicodedata.east_asian_width(c) in 'WF':
            w += 1.0
        elif c == ' ':
            w += 0.32
        elif c in 'ijl.,:;|!\'`()[]':
            w += 0.34
        elif c in 'mwMW@%':
            w += 0.86
        elif c.isupper() or c.isdigit():
            w += 0.64
        else:
            w += 0.56
    return w * size * (1.04 if weight not in ('normal', '400') else 1.0)


class Figure:
    def __init__(self, w, h, title, desc, label=None):
        assert 960 <= w <= 1040, '画布宽度应在 960–1040px'
        self.w, self.h = w, h
        self.min_font = 12 * w / 740
        self.out = []
        self.used = []
        self.has_neutral = False  # 画过白色“一般步骤”卡片时，图例自动补上这一项
        self.title = title
        self.out.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">')
        self.out.append(f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>')
        defs = ['<defs>',
                '<filter id="sh" x="-10%" y="-10%" width="120%" height="130%">'
                '<feDropShadow dx="0" dy="1.5" stdDeviation="2" flood-color="#0f172a" flood-opacity="0.08"/></filter>']
        for name, (color, _, _) in ARROWS.items():
            defs.append(f'<marker id="ah-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" '
                        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0.8 L9.5,5 L0,9.2 z" fill="{color}"/></marker>')
        defs.append('</defs>')
        self.out.append(''.join(defs))
        self.out.append(f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="18" fill="#f8fafc" stroke="#e2e8f0"/>')
        if label:
            self.text(36, 44, label, 18, SUB, '600')

    # ---- primitives -------------------------------------------------
    def _font(self, size):
        if size + 1e-6 < self.min_font:
            raise ValueError(f'{self.title}: 字号 {size} 低于下限 {self.min_font:.1f}')

    def text(self, x, y, s, size=18, color=INK, weight='normal', anchor='start', maxw=None):
        self._font(size)
        if maxw is not None and text_width(s, size, weight) > maxw:
            raise ValueError(f'{self.title}: 文字超宽 “{s}” {text_width(s, size, weight):.0f} > {maxw:.0f}')
        self.out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
                        f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')

    def raw(self, s):
        self.out.append(s)

    def mark(self, kind):
        if kind == 'neutral':
            self.has_neutral = True
        if kind not in self.used and kind != 'neutral':
            self.used.append(kind)

    def card(self, x, y, w, title, lines=(), kind='neutral', h=None, badge=None, align='center',
             dashed=False, tsize=19, lsize=17, shadow=True, strong=False, pad=18):
        fill, stroke, ink, _ = KINDS[kind]
        self.mark(kind)
        lh = lsize * 1.5
        th = tsize * 1.3 if title else 0
        gap = 6 if title and lines else 0
        content = th + gap + lh * len(lines)
        if h is None:
            h = content + 30
        assert content + 10 <= h, f'{title}: 卡片高度不足'
        d = ' stroke-dasharray="7 5"' if dashed else ''
        sw = 2.2 if strong else 1.5
        f = ' filter="url(#sh)"' if shadow else ''
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" '
                        f'stroke="{stroke}" stroke-width="{sw}"{d}{f}/>')
        left = x + pad
        if badge is not None:
            self.badge(x + pad + 13, y + h / 2 if not lines else y + (h - content) / 2 + th / 2 + 1, badge, kind)
            left = x + pad + 36
        avail = x + w - pad - left
        top = y + (h - content) / 2
        if align == 'center' and badge is None:
            cx = x + w / 2
            anchor = 'middle'
        else:
            cx = left
            anchor = 'start'
        if title:
            self.text(cx, top + tsize * 1.0, title, tsize, INK, '600', anchor, maxw=avail if anchor == 'start' else w - 2 * pad)
        for i, line in enumerate(lines):
            self.text(cx, top + th + gap + lh * i + lsize * 1.08, line, lsize, SUB, 'normal', anchor,
                      maxw=avail if anchor == 'start' else w - 2 * pad)
        return dict(x=x, y=y, w=w, h=h, cx=x + w / 2, cy=y + h / 2, r=x + w, b=y + h)

    def group(self, x, y, w, h, label, kind='state', dashed=True, size=18, sub=None):
        fill, stroke, ink, _ = KINDS[kind]
        d = ' stroke-dasharray="8 6"' if dashed else ''
        self.out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" fill-opacity="0.55" '
                        f'stroke="{stroke}" stroke-width="1.5"{d}/>')
        tw = text_width(label, size, '600') + 24
        self.out.append(f'<rect x="{x + 16}" y="{y - 14}" width="{tw:.0f}" height="28" rx="14" fill="#ffffff" stroke="{stroke}" stroke-width="1.2"/>')
        self.text(x + 28, y + 6, label, size, ink, '600')
        if sub:
            self.text(x + 16 + tw + 12, y + 6, sub, 17, SUB)

    def badge(self, cx, cy, n, kind='neutral'):
        ink = KINDS[kind][2] if kind != 'neutral' else '#334155'
        self.out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="13" fill="{ink}"/>')
        self.text(cx, cy + 5.6, str(n), 17, '#ffffff', '700', 'middle')

    def pill(self, x, y, s, color=SUB, size=17, anchor='middle', bg='#ffffff', border='#e2e8f0'):
        tw = text_width(s, size)
        if anchor == 'middle':
            x0 = x - tw / 2 - 8
        elif anchor == 'start':
            x0 = x - 8
        else:
            x0 = x - tw - 8
        self.out.append(f'<rect x="{x0:.1f}" y="{y - size * 0.95:.1f}" width="{tw + 16:.1f}" height="{size * 1.45:.1f}" '
                        f'rx="{size * 0.72:.1f}" fill="{bg}" stroke="{border}" stroke-width="1"/>')
        self.text(x, y, s, size, color, 'normal', anchor)

    def arrow(self, *pts, style='main', label=None, at=None, lcolor=None, anchor='middle', rounded=10,
              towards=None):
        """towards：本箭头意图指向的目标点（通常是目标卡片中心），用于检查方向没有画反。"""
        color, width, dash = ARROWS[style]
        segs = [math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) for i in range(1, len(pts))]
        total = sum(segs)
        if total < 12:
            raise ValueError(f'{self.title}: 箭头过短 {total:.1f}px，起止 {pts[0]} → {pts[-1]}')
        if any(l == 0 for l in segs):
            raise ValueError(f'{self.title}: 箭头含零长度线段 {pts}')
        (x0, y0), (x1, y1) = pts[0], pts[-1]
        if towards is not None:
            tx, ty = towards
            if (x1 - x0) * (tx - x0) + (y1 - y0) * (ty - y0) <= 0:
                raise ValueError(f'{self.title}: 箭头方向与目标相反，起 {pts[0]} 止 {pts[-1]} 目标 {towards}')
        if len(pts) == 2 and math.hypot(x1 - x0, y1 - y0) < 12:
            raise ValueError(f'{self.title}: 箭头过短')
        d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
        for i in range(1, len(pts)):
            x, y = pts[i]
            if rounded and 0 < i < len(pts) - 1:
                px, py = pts[i - 1]
                nx, ny = pts[i + 1]
                r = min(rounded, abs(x - px) / 2 + abs(y - py) / 2, abs(nx - x) / 2 + abs(ny - y) / 2)
                ax = x - r * _sgn(x - px); ay = y - r * _sgn(y - py)
                bx = x + r * _sgn(nx - x); by = y + r * _sgn(ny - y)
                d += f' L{ax:.1f},{ay:.1f} Q{x:.1f},{y:.1f} {bx:.1f},{by:.1f}'
            else:
                d += f' L{x:.1f},{y:.1f}'
        ds = f' stroke-dasharray="{dash}"' if dash else ''
        self.out.append(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="none" '
                        f'stroke-linecap="round" stroke-linejoin="round"{ds} marker-end="url(#ah-{style})"/>')
        if label:
            lx, ly = at
            self.pill(lx, ly, label, lcolor or (color if style in ('fail', 'ok', 'model') else SUB), anchor=anchor)

    def legend(self, x, y, kinds=None, extra=(), neutral=True):
        """kinds: 语义色块；extra: [('main','主路径'),('loop','回路')] 线型说明。"""
        kinds = list(kinds if kinds is not None else self.used)
        if neutral and self.has_neutral and 'neutral' not in kinds:
            kinds.append('neutral')
        cx = x
        for k in kinds:
            fill, stroke, _, name = KINDS[k]
            self.out.append(f'<rect x="{cx}" y="{y - 13}" width="22" height="16" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            self.text(cx + 30, y, name, 17, SUB)
            cx += 30 + text_width(name, 17) + 20
        for style, name in extra:
            color, width, dash = ARROWS[style]
            ds = f' stroke-dasharray="{dash}"' if dash else ''
            self.out.append(f'<path d="M{cx},{y - 5} L{cx + 30},{y - 5}" stroke="{color}" stroke-width="{width}"{ds} marker-end="url(#ah-{style})"/>')
            self.text(cx + 40, y, name, 17, SUB)
            cx += 40 + text_width(name, 17) + 20
        if cx - 20 > self.w - 20:
            raise ValueError(f'{self.title}: 图例超出画布')
        return cx

    def save(self, name):
        self.out.append('</svg>')
        Path(__file__).with_name(name).write_text('\n'.join(self.out) + '\n', encoding='utf-8')
        print('wrote', name)


def _sgn(v):
    return (v > 0) - (v < 0)


def chip(fig, x, y, s, kind='neutral', w=None, h=40, dashed=False, strong=False):
    """单行小节点：宽度按文字自动计算。"""
    if w is None:
        w = text_width(s, 17, '600') + 30
    return fig.card(x, y, w, s, kind=kind, h=h, tsize=17, shadow=False, dashed=dashed, strong=strong, pad=min(18, (w - text_width(s, 17, '600')) / 2))


def edge_point(c, tx, ty, pad=4):
    """从卡片中心指向 (tx, ty) 的射线与卡片边框的交点，外扩 pad。"""
    cx, cy = c['cx'], c['cy']
    dx, dy = tx - cx, ty - cy
    hw, hh = c['w'] / 2 + pad, c['h'] / 2 + pad
    s = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return (cx + dx * s, cy + dy * s)
