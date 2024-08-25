from typing import Any, Dict, Iterable, Union

import panel as pn


def css(selector: Union[str, Iterable[str]], declarations: dict[str, str]) -> str:
    return "\n".join(
        [
            f"{selector if isinstance(selector, str) else ', '.join(selector)} {{",
            *[f"    {property}: {value};" for property, value in declarations.items()],
            "}",
        ]
    )


MAIN_COLOR = "#1e81f0"  # rgb 30, 129, 240

CSS_VARS = css(
    ":root",
    {
        "--body-font": "'Roboto', sans-serif !important",
        "--accent-color": f"{MAIN_COLOR} !important",
    },
)

CSS_GLOBAL = css("#header.shadow", {"box-shadow": "unset"})

"""
the structure of css_modifiers is as follows:
{
    "directory name under css/":[list of panel classes that will be modified],
    ...
}

Each CSS modifier file that needs to be loaded, is infered from the panel class name and the directory name.
For example, with value :
{ "foobar":[pn.widgets.TextInput] }
the css file that will be loaded is css/foobar/textinput.css

"""

css_modifiers = {
    "global": [
        pn.widgets.TextInput,
        pn.widgets.Select,
        pn.widgets.Button,
        pn.layout.Divider,
        pn.Column,
    ],
    "filters": [
        pn.widgets.TextInput,
        pn.pane.Markdown,
        pn.widgets.IntRangeSlider,
        pn.Row,
        pn.widgets.Button,
    ],
}


"""
CSS helpers, constants and UI Helpers
"""


def divider():
    return pn.layout.Divider(css_classes=["default_divider"])


def add_modifier(
    modifier_class: pn.viewable.Viewable,
    modifications: Dict[str, Any],
    property: str = "stylesheets",
):
    properties = pn.theme.fast.Fast.modifiers.setdefault(modifier_class, {})
    property_modifications = properties.setdefault(property, [])
    property_modifications.append(modifications)


def apply_design_modifiers():
    css_filepaths = []
    for dir, classes in css_modifiers.items():
        for cls in classes:
            css_filepath = f"css/{dir}/{cls.__name__.lower()}.css"
            add_modifier(cls, css_filepath)
            css_filepaths.append(css_filepath)

    return css_filepaths


def connection_monitor():
    connection_monitor = pn.pane.HTML(
        """

    <script>

        const originalSend = WebSocket.prototype.send;
        window.sockets = [];
        WebSocket.prototype.send = function(...args) {
            if (window.sockets.indexOf(this) === -1)
                window.sockets.push(this);
            return originalSend.call(this, ...args);
        };

        console.log(window.sockets);

        const polling = setInterval(function() {

            if ( window.sockets.length > 0 ){

                if ( window.sockets[0].readyState >= 2 ){

                    let div = document.createElement('div');
                    div.style.color = 'white';
                    div.style.backgroundColor= 'crimson';
                    div.style.padding = '10px 10px 10px 10px';
                    div.style.textAlign= 'center';

                    let text = document.createTextNode('Bokeh session has expired. Please reload.');
                    div.appendChild(text);


                    window.document.body.insertBefore(
                        div,
                        window.document.body.firstChild
                    );

                    clearInterval(polling);
                }
            }

        }, 5000);

    </script>
    """
    )

    return connection_monitor
