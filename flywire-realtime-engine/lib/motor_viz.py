import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lib.visualize import (
    build_brain_figure,
    activity_to_color,
    _compute_brain_bounds,
    compute_global_activity,
)
from lib.big_pickle import profiled


def _build_ground_trace():
    size = 2.5
    n_lines = 11
    lines_x, lines_y, lines_z = [], [], []
    for i in range(n_lines):
        pos = -size + 2 * size * i / (n_lines - 1)
        lines_x.extend([pos, pos, None])
        lines_y.extend([-size, size, None])
        lines_z.extend([0, 0, None])
        lines_x.extend([-size, size, None])
        lines_y.extend([pos, pos, None])
        lines_z.extend([0, 0, None])
    return go.Scatter3d(
        x=lines_x, y=lines_y, z=lines_z,
        mode='lines',
        line=dict(color='rgba(100,120,140,0.25)', width=1),
        showlegend=False, hoverinfo='skip', name='Ground',
    )


def _build_path_trace(body_states):
    pts = body_states[-1]['path']
    if len(pts) < 2:
        return go.Scatter3d(x=[], y=[], z=[], mode='lines', showlegend=False, hoverinfo='skip')
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [0.005] * len(pts)
    return go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode='lines',
        line=dict(color='rgba(68,136,204,0.6)', width=2),
        showlegend=False, hoverinfo='skip', name='Path',
    )


def _build_skeleton_traces(body_state):
    items = body_state.get('skeleton_items', [])
    traces = []
    for item in items:
        if item['type'] == 'mesh':
            v = item['verts']
            f = item['faces']
            traces.append(go.Mesh3d(
                x=v[:, 0], y=v[:, 1], z=v[:, 2],
                i=f[:, 0], j=f[:, 1], k=f[:, 2],
                color=item['color'],
                opacity=0.9,
                lighting=dict(ambient=0.4, diffuse=0.6, specular=0.1),
                showlegend=False, hoverinfo='skip',
            ))
        elif item['type'] == 'line':
            pts = item['points']
            traces.append(go.Scatter3d(
                x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
                mode='lines+markers',
                line=dict(color=item['color'], width=item.get('width', 2)),
                marker=dict(size=2, color=item['color']),
                showlegend=False, hoverinfo='skip',
            ))
        elif item['type'] == 'leg':
            pts = item['points']
            traces.append(go.Scatter3d(
                x=pts[:, 0], y=pts[:, 1], z=pts[:, 2],
                mode='lines+markers',
                line=dict(color=item['color'], width=item.get('width', 4)),
                marker=dict(size=[0, 0, 0, 0, 3], color=item['color']),
                showlegend=False, hoverinfo='skip',
            ))
    return traces


def _build_skeleton_frame_traces(body_state):
    return _build_skeleton_traces(body_state)


def _body_axis_range(body_states):
    all_x, all_y, all_z = [], [], []
    for state in body_states:
        pos = state['pos']
        all_x.append(pos[0])
        all_y.append(pos[1])
        all_z.append(pos[2])
        j = state.get('leg_joints', {})
        for name, vals in j.items():
            for k in ['hip', 'knee', 'foot']:
                p = vals.get(k)
                if p is not None:
                    all_x.append(p[0])
                    all_y.append(p[1])
                    all_z.append(p[2])
    if not all_x:
        return [-1.5, 1.5], [-1.5, 1.5], [-0.3, 0.8]
    margin = 0.8
    return (
        [min(all_x) - margin, max(all_x) + margin],
        [min(all_y) - margin, max(all_y) + margin],
        [-0.1, max(all_z) + margin],
    )


@profiled("renderer_dual_animation")
def create_dual_figure(
    neuropil_names, meshes, centers, classifications,
    history, body_states, motor_commands, behavior_name="walking",
):
    timesteps = len(history)

    brain_traces_init = build_brain_figure(
        neuropil_names, meshes, centers, classifications,
        history, behavior_name, 0,
    )

    body_traces_init = _build_skeleton_traces(body_states[0])

    ground_trace = _build_ground_trace()
    path_trace = _build_path_trace(body_states[:1])

    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.5, 0.5],
        specs=[[{'type': 'scene'}, {'type': 'scene'}]],
        subplot_titles=('Brain Activity', 'Body Movement'),
    )

    for trace in brain_traces_init:
        fig.add_trace(trace, row=1, col=1)

    fig.add_trace(ground_trace, row=1, col=2)
    for trace in body_traces_init:
        fig.add_trace(trace, row=1, col=2)
    fig.add_trace(path_trace, row=1, col=2)

    brain_bounds = _compute_brain_bounds(neuropil_names, meshes)
    pad_b = 30000
    bx = [brain_bounds['x'][0] - pad_b, brain_bounds['x'][1] + pad_b]
    by = [brain_bounds['y'][0] - pad_b, brain_bounds['y'][1] + pad_b]
    bz = [brain_bounds['z'][0] - pad_b, brain_bounds['z'][1] + pad_b]

    body_xr, body_yr, body_zr = _body_axis_range(body_states)

    body_offset = len(brain_traces_init) + 1

    frames = []
    for t in range(1, timesteps):
        act = history[t]
        act_min, act_max = act.min(), act.max()
        act_range = act_max - act_min if act_max > act_min else 1.0
        act_norm = (act - act_min) / act_range

        brain_frame = []
        for idx in range(len(neuropil_names)):
            brain_frame.append(go.Mesh3d(color=activity_to_color(act_norm[idx])))

        body_state = body_states[t] if t < len(body_states) else body_states[-1]
        body_frame = [go.Scatter3d()]
        body_frame.extend(_build_skeleton_frame_traces(body_state))
        body_frame.append(_build_path_trace(body_states[:t + 1]))

        frames.append(go.Frame(
            data=brain_frame + body_frame,
            name=str(t),
        ))

    fig.update_layout(
        title=dict(
            text=f'<b>Fly Brain — Closed-Loop Walking</b>',
            font=dict(size=16, color='white'), x=0.5,
        ),
        scene=dict(
            xaxis=dict(visible=False, showticklabels=False, range=bx),
            yaxis=dict(visible=False, showticklabels=False, range=by),
            zaxis=dict(visible=False, showticklabels=False, range=bz),
            bgcolor='#111111',
            camera=dict(eye=dict(x=1.2, y=1.2, z=0.6), center=dict(x=0, y=0, z=0)),
            aspectmode='data',
        ),
        scene2=dict(
            xaxis=dict(visible=False, showticklabels=False, range=body_xr),
            yaxis=dict(visible=False, showticklabels=False, range=body_yr),
            zaxis=dict(visible=False, showticklabels=False, range=body_zr),
            bgcolor='#1a1a2a',
            camera=dict(
                eye=dict(x=body_states[0]['pos'][0] + 1.5, y=body_states[0]['pos'][1] + 1.0, z=body_states[0]['pos'][2] + 0.6),
                center=dict(x=body_states[0]['pos'][0], y=body_states[0]['pos'][1], z=body_states[0]['pos'][2]),
            ),
            aspectmode='data',
        ),
        paper_bgcolor='black', plot_bgcolor='black',
        font=dict(color='white', size=11),
        margin=dict(l=10, r=10, t=50, b=10), height=700,
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 40, 'redraw': True}, 'fromcurrent': True, 'transition': {'duration': 0}}],
                    'label': 'Play', 'method': 'animate',
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                    'label': 'Pause', 'method': 'animate',
                },
            ],
            'direction': 'left', 'pad': {'r': 10, 't': 87},
            'showactive': False, 'type': 'buttons', 'x': 0.1, 'xanchor': 'right', 'y': 0, 'yanchor': 'top',
        }],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'args': [[str(t)], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                    'label': f'{t * 2}', 'method': 'animate',
                }
                for t in range(0, timesteps, max(1, timesteps // 30))
            ],
            'tickcolor': 'white', 'font': {'color': 'white'},
            'bgcolor': '#222222', 'activebgcolor': '#444444',
            'currentvalue': {'font': {'size': 12, 'color': 'white'}, 'prefix': 'Time (ms): ', 'visible': True},
        }],
    )

    fig.frames = frames
    return fig
