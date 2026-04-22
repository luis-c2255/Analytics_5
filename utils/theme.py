import streamlit as st

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
        <h1 style='font-family: Syne; color: #40E0D0; text-shadow: 2px 2px 4px #00F5FF, 0 0 25px #bf5fff, 0 0 5px #ff2d78; 
        margin: 0; text-align: center; text-transform: uppercase; font-size: 3rem;'>{title}</h1>
        </div>
        """
