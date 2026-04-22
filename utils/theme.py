import streamlit as st
from __future__ import annotations
from typing import Any, Dict, Optional, Literal
from math import isnan
from dataclasses import dataclass

@dataclass
class KpiCardProps:
    label: str
    value: Optional[float]
    format: Optional[Literal['percent', 'time', 'integer', 'decimal']] = None
    goal: Optional[float] = None
    suffix: Optional[str] = None
    accent: Optional[str] = None

NEON: Dict[str, Dict[str, str]] = {
    "cyan": {
        "color": '#00f5ff',
        'glow': 'rgba(0,245,255,0.55)',
        'shadow': "0 0 10px rgba(0,245,255,0.5), 0 0 24px rgba(0,245,255,0.2)",
    },
    "green": {
        "color": "#00ff9f",
        'glow': 'rgba(0,255,159,0.55)',
        'shadow': "0 0 10px rgba(0,255,159,0.5), 0 0 24px rgba(0,255,159,0.2)",
    },
    "pink": {
        'color': '#ff2d78',
        'glow': 'rgba(255,45,120,0.55)',
        'shadow': "0 0 10px rgba(255,45,120,0.5), 0 0 24px rgba(255,45,120,0.2)",
    },
    "purple": {
        "color": "#bf5fff",
        'glow': "rgba(191,95,255,0.55)",
        "shadow": "0 0 10px rgba(191,95,255,0.5), 0 0 24px rgba(191,95,255,0.2)",
    },
    "amber": {
        'color': "#ffcc00",
        "glow": "rgba(255,204,0,0.55)",
        "shadow": "0 0 10px rgba(255,204,0,0.5), 0 0 24px rgba(255,204,0,0.2)",
    },
}

def resolve_neon(accent: Optional[str] = None) -> Dict[str, str]:
    if accent is not None and "pink" in accent:
        return NEON['pink']
    if accent is not None and "purple" in accent:
        return NEON["purple"]
    if accent is not None and 'green' in accent:
        return NEON["green"]
    if accent is not None and "amber" in accent:
        return NEON["amber"]
    return NEON["cyan"]

def minutes_to_display(minutes: Optional[float]) -> str:
    if minutes is None or (isinstance(minutes, float) and math.isnan(minutes)):
        return "-"
    total_seconds = round(minutes * 60)
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m:02d}:{s:02d}"
def format_value(
    value: Optional[float],
    format: Optional[Literal['percent', 'time', 'integer', 'decimal']],
    suffix: Optional[str] = None,
) -> str:
    if value is None or (isinstance(value, float) and isnan(value)):
        return "-"
    match format:
        case 'percent':
            return f"{round(value)}%"
        case "time":
            return minutes_to_display(value)
        case 'integer':
            return f"{round(value):,}"
        case "decimal":
            return f"{value:.2f}"
        case _:
            return f"{value}{suffix or ''}"
        
def goal_status(
    value: Optional[float],
    goal: Optional[float],
) -> Literal['above', 'below', 'none']:
    if value is None or goal is None:
        return 'none'
    return 'above' if value <= goal else "below"

def metric_card(
    *,
    label: Any,
    value: Any,
    goal: Any = None,
    suffix: Any = None,
    accent: Optional[str] = None,
) -> Dict[str, Any]:
    status = goal_status(value, goal)
    neon_accent = resolve_neon(accent)
    status_neon = NEON['green'] if status == 'above' else NEON['pink'] if status == 'below' else neon_accent
    bar_neon = status_neon if goal is not None else neon_accent
    goal_label = "▲ ON TARGET" if status == "above" else "▼ OFF TARGET" if status == "below" else ""
    goal_suffix = (
        f" / goal "
        f"{f'{goal}%' if format == 'percent' else minutes_to_display(goal) if format == 'time' else goal}" if goal is not None else ""
    )
    children: list[Dict[str, Any]] = []
    
    children.append(
        {
            "type": "div",
            "props": {
                "style": {
                'position': 'absolute',
                'top': 0,
                'left': 0,
                'right': 0,
                'height': 2,
                'background': (
                    'linear-gradient(90deg, transparent 0%,'
                    f"{bar_neon['color']} 40%, {bar_neon['color']} 60%, transparent 100%)"
                ),
                "boxShadow": bar_neon['shadow'],
            }
        }, "children": [],
    }
)
    children.append(
        {
            "type": "div",
            "props": {
                "style": {
                    "position": "absolute",
                    "top": 0,
                    "left": 0,
                    "width": 6,
                    "height": 6,
                    "background": bar_neon["color"],
                    "boxShadow": bar_neon["shadow"],
                    "clipPath": "polygon(0 0, 100% 0, 0 100%)",
                }
            },
            "children": [],
        }
    )
    children.append(
        {
            "type": "div",
            "props": {
                "className": "label",
                "style": {"marginBottom": 10, "color": bar_neon["color"], "opacity": 0.7},
            },
            "children": [label],
        }
    )

    children.append(
        {
            "type": "div",
            "props": {
                "className": "value-xl",
                "style": {
                    "color": bar_neon["color"],
                    "textShadow": bar_neon["shadow"].split(",")[0],
                    "letterSpacing": "-0.01em",
                },
            },
            "children": [format_value(value, format, suffix)],
        }
    )
    if goal is not None and status != "none":
        children.append(
            {
                "type": "div",
                "props": {
                    "style": {
                        "display": "inline-flex",
                        "alignItems": "center",
                        "gap": 4,
                        "marginTop": 10,
                        "padding": "3px 8px",
                        "border": f"1px solid {status_neon['color']}44",
                        "background": f"{status_neon['color']}0a",
                        "fontSize": 9,
                        "fontWeight": 700,
                        "letterSpacing": "0.1em",
                        "color": status_neon["color"],
                        "textShadow": f"0 0 6px {status_neon['color']}",
                        "clipPath": (
                            "polygon(0 0, calc(100% - 5px) 0, 100% 5px, "
                            "100% 100%, 5px 100%, 0 calc(100% - 5px))"
                        ),
                    }
                },
                "children": [
                    goal_label,
                    {
                        "type": "span",
                        "props": {"style": {"fontWeight": 400, "opacity": 0.6}},
                        "children": [goal_suffix],
                    },
                ],
            }
        )

    return {
        "type": "div",
        "props": {
            "className": "card fade-in",
            "style": {
                "position": "relative",
                "overflow": "hidden",
                "minWidth": 150,
                "paddingTop": 18,
                "borderColor": f"{bar_neon['color']}22",
                "boxShadow": f"inset 0 0 20px {bar_neon['glow'].replace('0.55', '0.04')}",
            },
        },
        "children": children,
    }

class Colors :
    CYAN = "#00f5ff"
    PINK = "#ff2d78"
    PURPLE = "#bf5fff"
    GREEN = "#00ff9f"
    AMBER = "#ffcc00"
    BLUE = "#4d8aff"
    RED = "#FF2D78"
    WHITE = "#E2E8FF"

class Components:
    @staticmethod
    def metric_card(title: str, value: str, delta: str = "", delta_positive: bool = True, card_type: str = "primary") -> str:
        colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.AMBER,
        "error": Colors.RED
        }
        border_color = colors.get(card_type, Colors.BLUE)
        delta_color = Colors.GREEN if delta_positive else Colors.RED
        delta_html = (
            f"<p class='metric-delta' style='color:{delta_color};'>{delta}</p>"
            if delta else ""
        )
        return f"""
        <div class='metric-card' style='--bordercolor:{border_color};'>
            <div style='display:flex; align-items:center; margin-bottom:0.5rem;'>
                <p class='metric-title'>{title}</p>
            </div>
            <p class='metric-value'>{value}</p>
            {delta_html}
        </div>
        """
    @staticmethod
    def insight_box(title: str, content: str, box_type: str = "info", min_height: str = "auto") -> str:
        """Create a styled insight/info box with optional min-height"""
        config = {
            "info": {"color": Colors.BLUE, "bg": "rgba(58, 141, 255, 0.15)"},
            "success": {"color": Colors.GREEN, "bg": "rgba(76, 201, 166, 0.15)"},
            "warning": {"color": Colors.AMBER, "bg": "rgba(255, 184, 77, 0.15)"},
            "error": {"color": Colors.RED, "bg": "rgba(255, 107, 107, 0.15)"}
        }
        style = config.get(box_type, config["info"])
        flex_style = "display: flex; flex-direction: column;" if min_height != "auto" else ""
        height_style = f"min-height: {min_height};" if min_height != "auto" else ""
        return f"""
        <div style='background-color: {style["bg"]};
                    padding: 1rem; border-radius: 8px; margin: 1rem 0;
                    border-left: 6px solid {style["color"]};
                    {height_style} {flex_style}'>
            <h4 style='color: {style["color"]}; margin: 0 0 0.5rem 0;'>{title}</h4>
            <div style='flex-grow: 1; color: {Colors.WHITE};'>{content}</div>
        </div>
        """
    @staticmethod
    def page_header(title:str) -> str:
        """Create a styled page header"""
        return f"""
        <h1 style='color: #40E0D0; text-shadow: 2px 2px 4px #00F5FF, 0 0 25px #bf5fff, 0 0 5px #ff2d78; 
        margin: 0; text-align: center; text-transform: uppercase; font-size: 3rem;'>{title}</h1>
        </div>
        """
