import panel as pn


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


def get_template():
    """
    Returns a Panel template with the given title,
    with its menu and other header items.
    """

    template = pn.template.FastListTemplate(
        site="NIH",
        title="OpenSciMetrics",
        favicon="https://www.nih.gov/favicon.ico",
        sidebar=[],
    )

    template.header.append(
        connection_monitor(),
    )

    return template
