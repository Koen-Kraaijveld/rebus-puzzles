import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.font_manager import FontProperties
from matplotlib.patches import ConnectionPatch

from util import get_node_attributes, get_edge_information, get_graph_as_sequence
from .templates.Template import Template


class RebusImageConverter:
    def __init__(self):
        self.BASE_SIZE = (400, 400)

    def generate(self, graph, show=False, save=None):
        edges = nx.get_edge_attributes(graph, "rule").values()
        if "INSIDE" in edges:
            self.generate_inside(graph, show=show, save=save)
        elif "ABOVE" in edges:
            self.generate_above(graph, show=show, save=save)
        elif "OUTSIDE" in edges:
            self.generate_outside(graph, show=show, save=save)
        else:
            fig, ax = plt.subplots(figsize=(self.BASE_SIZE[0] / 100, self.BASE_SIZE[1] / 100))
            node_attrs = get_node_attributes(graph)
            template = self._select_template(graph)

            if len(graph.nodes) > 3:
                plt.close(fig)
                return None

            for element, (node, attrs) in zip(template.elements, node_attrs.items()):
                x, y, _ = element
                size = 36
                points = self._apply_repetition_rule(attrs, x, y, size)
                for point in points:
                    x, y, _ = point
                    text = attrs["text"]
                    text = self._apply_direction_rule(text, attrs)
                    color = self._apply_color_rule(attrs)
                    size_ = self._apply_size_rule(size, attrs)
                    text, font = self._apply_icon_rule(text, attrs)
                    alpha = 0.75 if "icon" in attrs and "cross" in attrs else 1.
                    ax.text(x, y, text, color=color, fontsize=size_, fontweight="bold", fontfamily=font, ha="center",
                            va="center", alpha=alpha)
                    self._apply_highlight_rule(attrs, ax, text, x, y, size)
                    self._apply_cross_rule(attrs, ax, text, x, y, _)

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')

            if show:
                plt.show()
            if save is not None:
                plt.savefig(save)
            plt.close(fig)

    def generate_inside(self, graph, show=False, save=None):
        fig, ax = plt.subplots(figsize=(self.BASE_SIZE[0] / 100, self.BASE_SIZE[1] / 100))
        template = self._select_template(graph)

        graph_sequence = get_graph_as_sequence(graph)
        inside = graph_sequence[:graph_sequence.index("INSIDE")]
        outside = graph_sequence[graph_sequence.index("INSIDE")+1:]

        # print("Inside:", inside)
        # print("Outside:", outside)

        if len(inside) > 1 or len(outside) > 2:
            plt.close(fig)
            return None

        size = 36
        def _apply_rules(attrs):
            text = attrs["text"]
            text = self._apply_direction_rule(text, attrs)
            text = self._apply_repetition_rule_simple(text, attrs)
            color = self._apply_color_rule(attrs)
            size_ = self._apply_size_rule(size, attrs)
            text, font = self._apply_icon_rule(text, attrs)
            return {
                "text": text,
                "color": color,
                "font": font,
                "size": size_
            }

        x, y, _ = template.elements[0]
        inside = _apply_rules(inside[0])
        text = ax.text(x, y, inside["text"], color=inside["color"], ha="center", va="center", weight="bold",
                       fontsize=inside["size"], fontfamily=inside["font"])

        if len(outside) == 1:
            outside = _apply_rules(outside[0])
            if len(outside["text"]) == 1:
                outside_text_left, outside_text_right = outside["text"] * 2
            else:
                outside_text_left = "".join(list(outside["text"])[:int(len(outside["text"])/2)])
                outside_text_right = "".join(list(outside["text"])[int(len(outside["text"])/2):])
            ax.annotate(outside_text_left, xycoords=text, xy=(0, 0.5), va="center", ha="right", color=outside["color"],
                        weight="bold", fontsize=outside["size"], fontfamily=outside["font"])
            ax.annotate(outside_text_right, xycoords=text, xy=(1, 0.5), va="center", color=outside["color"],
                        weight="bold", fontsize=outside["size"], fontfamily=outside["font"])
        elif len(outside) == 2:
            outside_left = _apply_rules(outside[0])
            outside_right = _apply_rules(outside[1])
            ax.annotate(outside_left["text"], xycoords=text, xy=(0, 0.5), va="center", ha="right", fontsize=outside_left["size"],
                        color=outside_left["color"], weight="bold", fontfamily=outside_left["font"])
            ax.annotate(outside_right["text"], xycoords=text, xy=(1, 0.5), va="center", fontsize=outside_right["size"],
                        color=outside_right["color"], weight="bold", fontfamily=outside_right["font"])

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        if show:
            plt.show()
        if save is not None:
            plt.savefig(save)
        plt.close(fig)


    def generate_above(self, graph, show=False, save=None):
        fig, ax = plt.subplots(figsize=(self.BASE_SIZE[0] / 100, self.BASE_SIZE[1] / 100))
        template = self._select_template(graph)

        graph_sequence = get_graph_as_sequence(graph)
        above = graph_sequence[:graph_sequence.index("ABOVE")]
        below = graph_sequence[graph_sequence.index("ABOVE") + 1:]

        if len(above) > 2 or len(below) > 2:
            plt.close(fig)
            return None

        size = 36
        for element, nodes in zip(template.elements, (above, below)):
            x, y, size_multiplier = element
            if len(nodes) == 1:
                x_points = [(x, y, None)]
            else:
                x_gap = 0.025 * sum([len(attrs["text"]) for attrs in nodes])
                x_points = list(zip(list(np.linspace(x - x_gap, x + x_gap, len(nodes))), [y] * len(nodes), [size] * len(nodes)))
            for node_attrs, x_point in zip(nodes, x_points):
                x, y, _ = x_point
                if ("highlight" in node_attrs or ("size" in node_attrs and node_attrs["size"] == "big")) and y == 0.65:
                    y += 0.15
                elif ("highlight" in node_attrs or ("size" in node_attrs and node_attrs["size"] == "big")) and y == 0.35:
                    y -= 0.15
                size_ = size * size_multiplier
                text = node_attrs["text"]
                text = self._apply_direction_rule(text, node_attrs)
                text = self._apply_repetition_rule_simple(text, node_attrs, stack=True)
                color = self._apply_color_rule(node_attrs)
                size_ = self._apply_size_rule(size_, node_attrs)
                text, font = self._apply_icon_rule(text, node_attrs)
                ax.text(x, y, text, color=color, ha="center", va="center", weight="bold",
                        fontsize=size_, fontfamily=font)
                self._apply_highlight_rule(node_attrs, ax, text, x, y, _)
                self._apply_cross_rule(node_attrs, ax, text, x, y, _)
            above_text_len = sum([len(attrs["text"]) for attrs in above])
            below_text_len = sum([len(attrs["text"]) for attrs in below])
            divider_len = min(10, max(above_text_len, below_text_len))
            text = ax.text(0.5, 0.5, "─" * divider_len, color="black", ha="center", va="center", weight="bold",
                           fontsize=size * 1.2, fontfamily="Consolas")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        if show:
            plt.show()
        if save is not None:
            plt.savefig(save)
        plt.close(fig)

    def generate_outside(self, graph, show=True, save=None):
        fig, ax = plt.subplots(figsize=(self.BASE_SIZE[0] / 100, self.BASE_SIZE[1] / 100))

        graph_sequence = get_graph_as_sequence(graph)
        outside = graph_sequence[:graph_sequence.index("OUTSIDE")]
        inside = graph_sequence[graph_sequence.index("OUTSIDE") + 1:]

        # print("Inside:", inside)
        # print("Outside:", outside)

        if len(inside) > 1 or len(outside) > 1:
            plt.close(fig)
            return None

        def _apply_rules(attrs):
            text = attrs["text"]
            text = self._apply_direction_rule(text, attrs)
            text = self._apply_repetition_rule_simple(text, attrs)
            color = self._apply_color_rule(attrs)
            text, font = self._apply_icon_rule(text, attrs)
            padding = 30 - (len(text) * 2)
            x_left = 0.25 - (0.015 * (len(text) / text.count("\n") if text.count("\n") > 0 else len(text)))
            x_right = 0.75
            return {
                "text": text,
                "color": color,
                "font": font,
                "padding": padding,
                "x_left": x_left,
                "x_right": x_right
            }

        inside = _apply_rules(inside[0])
        outside = _apply_rules(outside[0])
        size = 36
        size -= len(inside["text"]) / inside["text"].count("\n") if inside["text"].count("\n") > 0 else len(inside["text"])
        size -= len(outside["text"]) / outside["text"].count("\n") if outside["text"].count("\n") > 0 else len(inside["text"])

        ax.text(outside["x_left"], 0.5, outside["text"], color=outside["color"], ha="center", va="center", weight="bold", fontsize=size,
                fontfamily=outside["font"])
        ax.text(outside["x_right"], 0.5, inside["text"], color=inside["color"], ha="center", va="center", weight="bold", fontsize=size,
                fontfamily=inside["font"], bbox=dict(facecolor="white", edgecolor="black", pad=inside["padding"], linewidth=4))

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        if show:
            plt.show()
        if save is not None:
            plt.savefig(save)
        plt.close(fig)

    def generate_icon(self, icon):
        fig, ax = plt.subplots(figsize=(self.BASE_SIZE[0] / 100, self.BASE_SIZE[1] / 100))

        ax.text(0.5, 0.5, "👩🏻‍⚕", ha="center", va="center", fontsize=40, fontfamily="Segoe UI Emoji")

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        plt.show()
        plt.close(fig)

    def _select_template(self, graph):
        n_nodes = len(graph.nodes)
        edges = nx.get_edge_attributes(graph, "rule").values()
        if "INSIDE" in edges:
            return Template.BASE
        if "ABOVE" in edges:
            return Template.ABOVE
        if n_nodes == 1:
            return Template.BASE
        if n_nodes == 2:
            return Template.BASE_TWO
        if n_nodes == 3:
            return Template.BASE_THREE
        if n_nodes == 4:
            return Template.BASE_FOUR
        if n_nodes == 5:
            return Template.BASE_FIVE

    def _apply_color_rule(self, attrs):
        # if "icon" in attrs and "cross" in attrs:
        #     return "gray"
        return "black" if "color" not in attrs else attrs["color"]

    def _apply_icon_rule(self, text, attrs):
        if "icon" in attrs:
            return list(attrs["icon"].values())[0], "Segoe UI Emoji"
        return text, "Consolas"

    def _apply_repetition_rule(self, attrs, x, y, size):
        n_repeats = 1 if "repeat" not in attrs else attrs["repeat"]
        if n_repeats == 1:
            return [(x, y, size)]
        sizes = [40 * (1 / n_repeats)] * n_repeats

        # ACROSS X-DIMENSION
        if "direction" in attrs and (attrs["direction"] == "down" or attrs["direction"] == "up"):
            return list(zip(list(np.linspace(x - 0.15, x + 0.15, n_repeats)), [y] * n_repeats, sizes))

        y_gap = n_repeats * 0.075
        if "highlight" in attrs or ("size" in attrs and attrs["size"] == "big"):
            y_gap *= 2
        # ACROSS Y-DIMENSION
        return list(zip([x] * n_repeats, list(np.linspace(y - y_gap, y + y_gap, n_repeats)), sizes))

    def _apply_repetition_rule_simple(self, text, attrs, stack=False):
        n_repeats = 1 if "repeat" not in attrs else attrs["repeat"]
        if n_repeats == 4 and stack:
            return f"{text} {text}\n{text} {text}"
        # if len(text) == 1 and n_repeats > 1:
        #     return f"{text} {text}\n{text} {text}"
        if len(text) == 1:
            return "".join([text] * n_repeats)
        return "\n".join([text] * n_repeats)

    def _apply_direction_rule(self, text, attrs):
        if "direction" in attrs:
            if attrs["direction"] == "reverse":
                return text[::-1]
            if attrs["direction"] == "down":
                return "\n".join(text)
            if attrs["direction"] == "up":
                return "\n".join(text)[::-1]
        return text

    def _apply_cross_rule(self, attrs, ax, text, x, y, size):
        size_multiplier = 1.
        if "icon" in attrs:
            size_multiplier = 2.5
        if "cross" in attrs:
            # line_x1, line_x2 = x - (0.0025 * size * (len(text) / 2)), x + (0.0025 * size * (len(text) / 2))
            line_x1, line_x2 = x - (0.1 * (len(text) / 2) * size_multiplier), x + (0.1 * (len(text) / 2) * size_multiplier)
            y_offset = 0.01
            line = ConnectionPatch((line_x1, y + y_offset), (line_x2, y + y_offset), "axes fraction", "axes fraction",
                                   color="black", lw=2 * size_multiplier, zorder=10)
            ax.add_artist(line)

    def _apply_size_rule(self, size, attrs):
        if "size" in attrs:
            if attrs["size"] == "big":
                return size * 2
            if attrs["size"] == "small":
                return size * 0.5
        return size

    def _apply_highlight_rule(self, attrs, ax, text, x, y, size):
        x_offset_multiplier = 2. if len(text) == 1 else 1.
        if "highlight" in attrs:
            if attrs["highlight"] == "after":
                x += (0.11 * (len(text) / 2) * x_offset_multiplier)
                arrow_top = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 3)
                imagebox = OffsetImage(arrow_top, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y + 0.15), frameon=False)
                ax.add_artist(ab)
                arrow_bottom = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 1)
                imagebox = OffsetImage(arrow_bottom, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y - 0.12), frameon=False)
                ax.add_artist(ab)
            if attrs["highlight"] == "before":
                x -= (0.11 * (len(text) / 2) * x_offset_multiplier)
                arrow_top = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 3)
                imagebox = OffsetImage(arrow_top, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y + 0.15), frameon=False)
                ax.add_artist(ab)
                arrow_bottom = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 1)
                imagebox = OffsetImage(arrow_bottom, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y - 0.12), frameon=False)
                ax.add_artist(ab)
            if attrs["highlight"] == "middle":
                arrow_top = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 3)
                imagebox = OffsetImage(arrow_top, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y + 0.15), frameon=False)
                ax.add_artist(ab)
                arrow_bottom = np.rot90(plt.imread(f"{os.path.dirname(__file__)}../../saved/resources/arrow_right.png"), 1)
                imagebox = OffsetImage(arrow_bottom, zoom=0.025)
                ab = AnnotationBbox(imagebox, (x, y - 0.12), frameon=False)
                ax.add_artist(ab)
