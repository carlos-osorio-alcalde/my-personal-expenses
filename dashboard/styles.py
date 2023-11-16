class Styles:
    """Class to store the styles of the dashboard"""

    _THEME_COLOR = "#29A7A0"

    # Style for the H1 headers
    H1 = {
        "font-size": "2.5em",
        "color": "white",
        "font-weight": "bold",
        "text-align": "center",
        "margin-bottom": "20px",
        "background-color": _THEME_COLOR,
        "padding": "15px",
        "border-radius": "10px",
    }

    # Style for the H3 headers of the cards
    H3 = {
        "color": "white",
        "background-color": _THEME_COLOR,
        "padding": "10px",
        "border-radius": "5px",
    }

    # Style for the H4 headers of the cards
    H4 = {
        "color": _THEME_COLOR,
        "font-weight": "bold",
        "text-align": "center",
        "font-size": "1.3em",
    }

    # Style for the values of the cards
    VALUE_CARD = {
        "font-size": "2.5em",
        "color": _THEME_COLOR,
        "font-weight": "bold",
        "text-align": "center",
        "margin-bottom": "20px",
    }

    # Set the style for the table
    TABLE = {
        "backgroundColor": "white",
        "color": "#333",
        "width": "100%",
        "height": "100%",
        "margin": "auto",
        "maxHeight": "350px",
    }

    # Set the style of the Div that contains the table
    DIV_CARD = {
        "box-shadow": "2px 2px 2px 2px #D8D8D8",
        "padding": "20px",
        "height": "450px",
        "width": "100%",
        "border-radius": "5px",
        "overflow": "hidden",
    }

    # Set the style of the Div that contains the time series
    DIV_TIME_SERIES = {
        "box-shadow": "2px 2px 2px 2px #D8D8D8",
        "padding": "20px",
        "height": "650px",
        "width": "100%",
        "border-radius": "5px",
        "overflow": "hidden",
    }

    # Set the style of the Div that contains the left value on top
    DIV_LEFT_VALUE = {
        "box-shadow": "2px 2px 2px 2px #D8D8D8",
        "padding": "20px",
        "height": "180px",
        "margin": "auto",
        "align": "center",
        "left": "50%",
        "transform": "translate(52%, 0%)",
    }

    # Set the style of the Div that contains the right value on top
    DIV_RIGHT_VALUE = {
        "box-shadow": "2px 2px 2px 2px #D8D8D8",
        "padding": "20px",
        "height": "180px",
        "margin": "auto",
        "align": "center",
        "left": "50%",
        "transform": "translate(56%, 0%)",
    }
