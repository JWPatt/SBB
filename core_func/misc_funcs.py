from plotly import graph_objs as go


def sec_to_hhmm(seconds):
    """
    Convert an interger number of seconds into hours in minutes in hh:mm format.

    :param seconds:
    :return:
    """
    hours = seconds//3600
    minutes = (seconds-3600*hours)//60
    return str(int(hours)) + ":" + str(int(minutes)).zfill(2)


def discrete_colorscale(bvals, colors):
    """
    Choose colors and intervals for colorbar, returns the correctly formatted list for plotly.

    bvals - list of values bounding intervals/ranges of interest
    colors - list of rgb or hex colorcodes for values in [bvals[k], bvals[k+1]],0<=k < len(bvals)-1
    returns the plotly  discrete colorscale
    """
    if len(bvals) != len(colors) + 1:
        raise ValueError('len(boundary values) should be equal to  len(colors)+1')
    bvals = sorted(bvals)
    nvals = [(v - bvals[0]) / (bvals[-1] - bvals[0]) for v in bvals]  # normalized values

    dcolorscale = []  # discrete colorscale
    for k in range(len(colors)):
        dcolorscale.extend([[nvals[k], colors[k]], [nvals[k + 1], colors[k]]])
    return dcolorscale


# Must give plotly a blank figure to generate a loading screen before the real figure is loaded
def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig
