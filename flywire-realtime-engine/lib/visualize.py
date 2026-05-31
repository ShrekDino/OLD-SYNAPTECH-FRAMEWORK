import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from lib.big_pickle import profiled

COLOR_SCALE = [
    [0.0, '#1a1a5a'],
    [0.2, '#2a3a8a'],
    [0.4, '#4488dd'],
    [0.6, '#f0aa30'],
    [0.8, '#ee4422'],
    [1.0, '#ff1100'],
]

def activity_to_color(activity):
    t = max(activity, 0.0)
    t = min(t, 1.0)
    if t < 0.2:
        r = 0.1 + 0.2 * (t / 0.2)
        g = 0.1 + 0.5 * (t / 0.2)
        b = 0.35 + 0.35 * (t / 0.2)
    elif t < 0.4:
        r = 0.3 + 1.0 * ((t - 0.2) / 0.2)
        g = 0.6 - 0.15 * ((t - 0.2) / 0.2)
        b = 0.7 - 0.45 * ((t - 0.2) / 0.2)
    elif t < 0.6:
        r = 1.0
        g = 0.94 - 0.4 * ((t - 0.4) / 0.2)
        b = 0.2 - 0.13 * ((t - 0.4) / 0.2)
    elif t < 0.8:
        r = 1.0
        g = 0.54 - 0.4 * ((t - 0.6) / 0.2)
        b = 0.07 - 0.05 * ((t - 0.6) / 0.2)
    else:
        r = 1.0
        g = 0.14 - 0.14 * ((t - 0.8) / 0.2)
        b = 0.02 - 0.02 * ((t - 0.8) / 0.2)
    r = max(0, min(1, r))
    g = max(0, min(1, g))
    b = max(0, min(1, b))
    return f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'

def build_brain_figure(neuropil_names, meshes, centers, classifications, history, behavior_name, timestep=0):
    n_np = len(neuropil_names)
    act = history[timestep]
    act_min, act_max = act.min(), act.max()
    act_range = act_max - act_min if act_max > act_min else 1.0
    act_norm = (act - act_min) / act_range

    traces = []
    for idx, name in enumerate(neuropil_names):
        verts, faces = meshes[name]
        color = activity_to_color(act_norm[idx])
        group = classifications[name]['group']
        side = classifications[name]['side']
        hover_text = (
            f"<b>{name}</b><br>"
            f"Group: {group}<br>"
            f"Side: {side}<br>"
            f"Activity: {act[idx]:.3f}"
        )
        trace = go.Mesh3d(
            x=verts[:, 0], y=verts[:, 1], z=verts[:, 2],
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            color=color,
            opacity=0.85,
            name=name,
            hovertemplate=hover_text + '<extra></extra>',
            lighting=dict(ambient=0.5, diffuse=0.6, specular=0.05, roughness=0.4),
            lightposition=dict(x=100, y=200, z=100),
            flatshading=True,
            contour=dict(show=True, color='rgba(255,255,255,0.08)', width=2),
            showlegend=False,
        )
        traces.append(trace)

    return traces

def compute_global_activity(history):
    return history.mean(axis=1)

def make_legend_traces(neuropil_names, classifications):
    groups_seen = set()
    group_colors = {
        'optic': '#44aa44',
        'sensory_olfactory': '#44aaff',
        'sensory_auditory': '#88ddff',
        'sensory_visual': '#aaddff',
        'central_mushroom_body': '#ffaa44',
        'central_complex': '#ff44aa',
        'central_lateral_complex': '#ff88cc',
        'central_superior': '#cc88ff',
        'central_inferior': '#aa66dd',
        'central_ventrolateral': '#dd66aa',
        'central_ventromedial': '#884488',
        'motor_sez': '#ff6644',
        'motor_gnathal': '#cc4433',
        'other': '#888888',
    }
    legend_traces = []
    for name in neuropil_names:
        g = classifications[name]['group']
        if g not in groups_seen:
            groups_seen.add(g)
            c = group_colors.get(g, '#888888')
            label = g.replace('_', ' ').title()
            legend_traces.append(go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode='markers',
                marker=dict(size=5, color=c),
                name=label,
                showlegend=True,
            ))
    return legend_traces

def _compute_brain_bounds(neuropil_names, meshes):
    """Compute the bounding box of all neuropil meshes in data coordinates."""
    xs, ys, zs = [], [], []
    for name in neuropil_names:
        verts, _ = meshes[name]
        xs.extend([verts[:, 0].min(), verts[:, 0].max()])
        ys.extend([verts[:, 1].min(), verts[:, 1].max()])
        zs.extend([verts[:, 2].min(), verts[:, 2].max()])
    return {
        'x': (min(xs), max(xs)),
        'y': (min(ys), max(ys)),
        'z': (min(zs), max(zs)),
    }


@profiled("renderer_animation")
def create_animation(neuropil_names, meshes, centers, classifications, history, behavior_name="resting"):
    timesteps = history.shape[0]

    # Compute data-driven axis ranges from actual mesh coordinates
    bounds = _compute_brain_bounds(neuropil_names, meshes)
    pad_x = (bounds['x'][1] - bounds['x'][0]) * 0.1
    pad_y = (bounds['y'][1] - bounds['y'][0]) * 0.1
    pad_z = (bounds['z'][1] - bounds['z'][0]) * 0.1
    x_range = [bounds['x'][0] - pad_x, bounds['x'][1] + pad_x]
    y_range = [bounds['y'][0] - pad_y, bounds['y'][1] + pad_y]
    z_range = [bounds['z'][0] - pad_z, bounds['z'][1] + pad_z]

    # Compute centroid for camera focus
    centroid = np.array([
        (bounds['x'][0] + bounds['x'][1]) / 2,
        (bounds['y'][0] + bounds['y'][1]) / 2,
        (bounds['z'][0] + bounds['z'][1]) / 2,
    ])

    init_traces = build_brain_figure(
        neuropil_names, meshes, centers, classifications, history, behavior_name, 0
    )

    frames = []
    for t in range(1, timesteps):
        act = history[t]
        act_min, act_max = act.min(), act.max()
        act_range = act_max - act_min if act_max > act_min else 1.0
        act_norm = (act - act_min) / act_range

        frame_traces = []
        for idx, name in enumerate(neuropil_names):
            color = activity_to_color(act_norm[idx])
            frame_traces.append(go.Mesh3d(color=color))
        frames.append(go.Frame(data=frame_traces, name=str(t)))

    global_act = compute_global_activity(history)
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.85, 0.15],
        specs=[[{'type': 'scene'}, {'type': 'scatter'}]],
    )

    for trace in init_traces:
        fig.add_trace(trace, row=1, col=1)

    fig.add_trace(go.Scatter(
        x=list(range(timesteps)),
        y=global_act,
        mode='lines',
        line=dict(color='#ff4422', width=2),
        fill='tozeroy',
        fillcolor='rgba(255,68,34,0.15)',
        name='Global Activity',
        hovertemplate='Time: %{x}<br>Activity: %{y:.3f}<extra></extra>',
    ), row=1, col=2)

    fig.update_layout(
        title=dict(
            text=f'<b>Fly Brain Neuropil Activity — {behavior_name.title()}</b>',
            font=dict(size=18, color='white'),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(visible=False, showticklabels=False, range=x_range),
            yaxis=dict(visible=False, showticklabels=False, range=y_range),
            zaxis=dict(visible=False, showticklabels=False, range=z_range),
            bgcolor='#111111',
            camera=dict(
                eye=dict(x=1.2, y=1.2, z=0.6),
                center=dict(x=0, y=0, z=0),
            ),
            aspectmode='data',
        ),
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white', size=11),
        margin=dict(l=10, r=10, t=50, b=10),
        height=700,
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 40, 'redraw': True},
                                     'fromcurrent': True,
                                     'transition': {'duration': 0}}],
                    'label': 'Play',
                    'method': 'animate',
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': False},
                                       'mode': 'immediate',
                                       'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate',
                },
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top',
        }],
        sliders=[{
            'active': 0,
            'steps': [
                {
                    'args': [[str(t)], {'frame': {'duration': 0, 'redraw': True},
                                        'mode': 'immediate',
                                        'transition': {'duration': 0}}],
                    'label': f'{t}',
                    'method': 'animate',
                }
                for t in range(0, timesteps, max(1, timesteps // 20))
            ],
            'tickcolor': 'white',
            'font': {'color': 'white'},
            'bgcolor': '#222222',
            'activebgcolor': '#444444',
            'currentvalue': {
                'font': {'size': 12, 'color': 'white'},
                'prefix': 'Time: ',
                'visible': True,
            },
        }],
    )

    fig.update_xaxes(
        title='Time Step',
        color='#aaaaaa',
        gridcolor='#333333',
        row=1, col=2,
    )
    fig.update_yaxes(
        title='Mean Activity',
        color='#aaaaaa',
        gridcolor='#333333',
        range=[0, 1],
        row=1, col=2,
    )

    fig.frames = frames

    return fig

def save_figure(fig, output_path):
    fig.write_html(output_path, include_plotlyjs='cdn', auto_open=True, full_html=True)
    return output_path
