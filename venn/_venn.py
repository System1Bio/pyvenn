from matplotlib.pyplot import subplots
from matplotlib.patches import Ellipse, Polygon
from matplotlib.colors import to_rgba
from matplotlib.cm import ScalarMappable
from ._constants import SHAPE_COORDS, SHAPE_DIMS, SHAPE_ANGLES
from ._constants import PETAL_LABEL_COORDS

def select_colors(n_colors=6, cmap="viridis", alpha=.4):
    """Generate colors from matplotlib colormap; pass list to use exact colors"""
    if not isinstance(n_colors, int) or (n_colors < 2) or (n_colors > 6):
        raise ValueError("n_colors must be an integer between 2 and 6")
    if isinstance(cmap, list):
        colors = [to_rgba(color, alpha=alpha) for color in cmap]
    else:
        scalar_mappable = ScalarMappable(cmap=cmap)
        colors = scalar_mappable.to_rgba(range(n_colors), alpha=alpha)
    return colors[:n_colors]

def less_transparent_color(color, alpha_factor=2):
    """Bump up color's alpha"""
    new_alpha = (1 + to_rgba(color)[3]) / alpha_factor
    return to_rgba(color, alpha=new_alpha)

def draw_ellipse(ax, x, y, w, h, a, color):
    """Wrapper for drawing ellipse; called like `draw_ellipse(ax, *coords, *dims, angle, color)`"""
    ax.add_patch(
        Ellipse(
            xy=(x,y), width=w, height=h, angle=a,
            facecolor=color, edgecolor=less_transparent_color(color)
        )
    )

def draw_triangle(ax, x1, y1, x2, y2, x3, y3, _dim, _angle, color):
    """Wrapper for drawing triangle; called like `draw_triangle(ax, *coords, None, None, color)`"""
    ax.add_patch(
        Polygon(
            xy=[(x1, y1), (x2, y2), (x3, y3)], closed=True,
            facecolor=color, edgecolor=less_transparent_color(color)
        )
    )

def draw_text(ax, x, y, text, fontsize, color="black"):
    """Wrapper for drawing text"""
    ax.text(
        x, y, text, fontsize=fontsize, color=color,
        horizontalalignment="center", verticalalignment="center"
    )

def generate_logics(n_sets):
    """Generate intersection identifiers in binary (0010 etc)"""
    for i in range(1, 2**n_sets):
        yield bin(i)[2:].zfill(n_sets)

def generate_petals(datasets, fmt="{size} ({percentage:.1f}%)"):
    """Generate petal descriptions for venn diagram based on set sizes"""
    datasets = list(datasets)
    n_sets = len(datasets)
    dataset_union = set.union(*datasets)
    universe_size = len(dataset_union)
    petals = {}
    for logic in generate_logics(n_sets):
        included_sets = [
            datasets[i] for i in range(n_sets) if logic[i] == "1"
        ]
        excluded_sets = [
            datasets[i] for i in range(n_sets) if logic[i] == "0"
        ]
        petal_set = (
            (dataset_union & set.intersection(*included_sets)) -
            set.union(set(), *excluded_sets)
        )
        petals[logic] = fmt.format(
            logic=logic, size=len(petal_set),
            percentage=(100*len(petal_set)/universe_size)
        )
    return petals

def init_axes(ax, figsize):
    """Create axes if do not exist, set axes parameters"""
    if ax is None:
        _, ax = subplots(nrows=1, ncols=1, figsize=figsize)
    ax.set(
        aspect="equal", frame_on=False, xticks=[], yticks=[]
    )
    return ax

def venn(*, petals, labels, cmap="viridis", alpha=.4, figsize=(8, 8), fontsize=13, legend_loc="upper right", ax=None):
    """Draw prepared petals with provided labels"""
    n_sets = len(labels)
    for logic in petals.keys():
        if len(logic) != n_sets:
            raise ValueError("Inconsistent petal and dataset labels")
    if 2 <= n_sets < 6:
        draw_shape = draw_ellipse
    elif n_sets == 6:
        draw_shape = draw_triangle
    else:
        raise ValueError("Number of sets must be between 2 and 6")
    colors = select_colors(n_colors=n_sets, cmap=cmap, alpha=alpha)
    ax = init_axes(ax, figsize)
    shape_params = zip(
        SHAPE_COORDS[n_sets], SHAPE_DIMS[n_sets], SHAPE_ANGLES[n_sets], colors
    )
    for coords, dims, angle, color in shape_params:
        draw_shape(ax, *coords, *dims, angle, color)
    for logic, (x, y) in PETAL_LABEL_COORDS[n_sets].items():
        draw_text(ax, x, y, petals[logic], fontsize)
    if legend_loc is not None:
        ax.legend(labels, loc=legend_loc, prop={"size": fontsize})
    return ax.figure, ax
