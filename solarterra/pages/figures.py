import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def _sci_ticks(values, nticks=6, threshold=3):
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    vmin = float(np.nanmin(arr))
    vmax = float(np.nanmax(arr))
    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin == vmax:
        return None
    maxabs = max(abs(vmin), abs(vmax))
    if maxabs == 0:
        return None
    exp = int(np.floor(np.log10(maxabs)))
    if abs(exp) < threshold:
        return None
    base = 10 ** exp
    ticks = np.linspace(vmin, vmax, nticks)
    mant = ticks / base

    def fmt_m(x):
        s = f"{x:.3g}"
        return "0" if s == "-0" else s

    sup = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
    exp_sup = "".join(sup.get(ch, ch) for ch in str(exp))
    ticktext = [f"{fmt_m(m)}·10{exp_sup}" for m in mant]
    return ticks.tolist(), ticktext


def _apply_sci_ticks(fig, y_values, *, row=None, col=1):
    res = _sci_ticks(y_values)
    if not res:
        return
    vals, texts = res
    # Be robust: try row/col for subplots, fallback to figure-wide update
    try:
        if row is None:
            fig.update_yaxes(tickmode="array", tickvals=vals, ticktext=texts)
        else:
            fig.update_yaxes(tickmode="array", tickvals=vals, ticktext=texts, row=row, col=col)
    except Exception:
        fig.update_yaxes(tickmode="array", tickvals=vals, ticktext=texts)


def scatter(q_params, p_params, data):

    fig = go.Figure()

    field = q_params['list_of_fieldnames'][0]
    print("LOOKING AT FIELDS")
    # for field in q_params['list_of_fieldnames']:
    #     print(field)

    fig.add_trace(go.Scatter(
        x=data['dt_timestamp'], y=data[field], connectgaps=True, mode="lines+markers"))

    fig.update_traces(connectgaps=True, marker=dict(size=4))
    ts = p_params['ts_limits_dt']
    fig.update_layout(
        xaxis_range=[ts[0], ts[1]],
        yaxis_title=q_params['var_instance'].get_axis_label(),
    )

    fig.update_xaxes(
        title_font_size=24,  # x-axis label size
        tickfont_size=16     # x-axis tick size
    )

    fig.update_yaxes(
        title_font_size=20,  # y-axis label size
        tickfont_size=16     # y-axis tick size
    )

    if q_params['var_instance'].is_log():
        fig.update_yaxes(type="log")
    else:
        _apply_sci_ticks(fig, data[field])

    config = {'displayModeBar': False}
    plot_div = fig.to_html(config=config, full_html=False,
                           div_id=f"plot_div_{q_params['var_id']}", default_width="100%")

    return plot_div


def n_trace(q_params, p_params, data):

    fields = q_params['list_of_fieldnames']

    fig = make_subplots(rows=len(fields), cols=1,
                        shared_xaxes=True, vertical_spacing=0.05)
    ts = p_params['ts_limits_dt']
    for index, field in enumerate(fields):
        fig.add_trace(go.Scatter(
            x=data['dt_timestamp'],
            y=data[field],
            connectgaps=True,
            mode="lines+markers",
        ),
            row=index + 1,
            col=1
        )

        fig['layout'][f"yaxis{index+1}"]['title'] = field
        fig['layout'][f"xaxis{index+1}"]['range'] = [ts[0], ts[1]]

    fig.update_traces(marker=dict(size=4))

    #TODO: я определенно сделала это неищящно + для многокомпонентных переменных криво выдираются labelaxis
    fig.update_xaxes(
        title_font_size=24,  # x-axis label size
        tickfont_size=16     # x-axis tick size
    )
    fig.update_yaxes(
        title_font_size=20,  # y-axis label size
        tickfont_size=16     # y-axis tick size
    )

    fig.update_layout(
        height=700,
        xaxis_range=[ts[0], ts[1]],
        showlegend=False,
    )

    # Apply scientific ticks with middle dot (·) per subplot
    for index, field in enumerate(fields):
        _apply_sci_ticks(fig, data[field], row=index + 1, col=1)

    config = {'displayModeBar': False}
    plot_div = fig.to_html(config=config, full_html=False,
                           div_id=f"plot_div_{q_params['var_id']}", default_width="100%")

    return plot_div
