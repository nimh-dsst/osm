import param
from panel.reactive import ReactiveHTML
from panel.widgets import Widget


class SelectPicker(ReactiveHTML, Widget):
    title = param.String(default="")

    options = param.List(doc="List of possible values to be selected", default=[])
    filtered_options = param.List(
        doc="List of possible values to be selected", default=[]
    )
    value = param.List(doc="The actual list of selected values", default=[])

    filter_str = param.String(default="")

    update_title_callback = None

    _child_config = {"options": "model"}

    def __init__(self, **params):
        super().__init__(**params)

    @classmethod
    def from_param(cls, parameter: param.Parameter, update_title_callback, **params):
        result = super().from_param(parameter, **params)
        result.update_title_callback = update_title_callback
        result.value_did_change()
        return result

    def update_filtereted_options(self):
        self.filtered_options = [
            opt
            for opt in self.options
            if isinstance(opt, str) and self.filter_str.lower() in opt.lower()
        ]

    @param.depends("options", watch=True, on_init=True)
    def options_did_change(self):
        # print("options_did_change", self.options)
        self.value = [v for v in self.value if v in self.options]
        self.update_filtereted_options()

    @param.depends("value", watch=True, on_init=True)
    def value_did_change(self):
        # print("value_did_change", self.value)
        if self.update_title_callback is not None:
            self.title = self.update_title_callback(self, self.value, self.options)

    @param.depends("filter_str", watch=True, on_init=True)
    def filter_str_did_change(self):
        # print("filter_str_did_change", self.filter_str)
        self.update_filtereted_options()

    @param.depends("filtered_options", watch=True, on_init=True)
    def filtered_options_did_change(self):
        # print("filtered_options_did_change", self.filtered_options)
        pass

    _checkbox_group_css = """
                <style>
                input[type="checkbox"]{
                    -webkit-appearance: initial;
                    appearance: initial;
                    width: 20px;
                    height: 20px;
                    border: 2px solid black;
                    position: relative;
                    margin-left: 10px;
                    margin-right: 10px;
                    background-color: var(--accent-fill-active);

                }

                /*:host label {
                    background-color: gold;
                }*/

                input[type="checkbox"]:checked {
                    background-color: var(--accent-fill-active);
                }

                input[type="checkbox"]:checked::after {
                    content:"✓";

                    -webkit-transform: translate(-50%,-50%);
                    -moz-transform: translate(-50%,-50%);
                    -ms-transform: translate(-50%,-50%);
                    transform: translate(-50%,-50%);
                }

                input[type="checkbox"]::after {
                    color: #fff;
                    position: absolute;
                    left: 50%;
                    top: 50%;
                }

                input[type="checkbox"].intermediary::after {
                    content: "-";

                    -webkit-transform: translate(-50%,-60%) scale(200%);
                    -moz-transform: translate(-50%,-60%) scale(200%);
                    -ms-transform: translate(-50%,-60%) scale(200%);
                    transform: translate(-50%,-60%) scale(200%);
                }
            </style>
        """

    _style = """
        <style>


        div.sp_header {
            background-color: var(--bs-form-control-bg);
            border: 1px solid var(--accent-fill-rest);
            border-radius: calc(var(--corner-radius) * 1px);
            color: var(--neutral-foreground-rest);
            font-family: var(--body-font);
            font-size: var(--type-ramp-base-font-size);
            padding-left: 12px;
            width:auto;
            height:33px
        }


        div.sp_header p {
            margin-top: 6px;
            margin-right:18px;
        }

        div.sp_container {
            background-color: var(--bs-form-control-bg);
            margin-left: 10px;
            margin-right: 10px;
            margin-top: 5px;
            margin-bottom: 5px;
        }




        div.checkboxes_container {
            max-height:400px;
            overflow:scroll;
        }



        .scroll-shadows {

            background:
                /* Shadow Cover TOP */
                linear-gradient(
                var(--bs-form-control-bg) 30%,
                rgba(255, 255, 255, 0)
                ) center top,

                /* Shadow Cover BOTTOM */
                linear-gradient(
                rgba(255, 255, 255, 0),
                var(--bs-form-control-bg) 70%
                ) center bottom,

                /* Shadow TOP */
                radial-gradient(
                farthest-side at 50% 0,
                rgba(0, 0, 0, 0.2),
                rgba(0, 0, 0, 0)
                ) center top,

                /* Shadow BOTTOM */
                radial-gradient(
                farthest-side at 50% 100%,
                rgba(0, 0, 0, 0.2),
                rgba(0, 0, 0, 0)
                ) center bottom;

            background-repeat: no-repeat;
            background-size: 100% 10px, 100% 10px, 100% 7px, 100% 7px;
            background-attachment: local, local, scroll, scroll;
        }


        div.sp_options_list_container {
            background-color: lightgray;
            box-shadow: rgba(0, 0, 0, 0.2) 0px 5px 5px -3px,
                        rgba(0, 0, 0, 0.14) 0px 8px 10px 1px,
                        rgba(0, 0, 0, 0.12) 0px 3px 14px 2px;
            position: absolute;
            z-index: 1001;
            width: 300px;
            top: 30%;
            left: 15%;
        }

        .sp_filter {
            display:inline-flex;
            flex-direction:row;
            width: 100%;
            border-bottom: var(--bs-gray-500) solid 1px;

            background-color: var(--panel-secondary-color);
        }

        .sp_filter svg[data-icon-name="filterIcon"] {
            -webkit-transform: translate(-8px, 0px) scale(1.2, 1.2);
            -moz-transform: translate(-8px, 0px) scale(1.2, 1.2);
            -ms-transform: translate(-8px, 0px) scale(1.2, 1.2);
            transform: translate(-8px, 0px) scale(1.2, 1.2);

            fill: var(--bs-body-color);
            margin: 8px 20px;
            margin-right: 2px;
        }

        .sp_select_all {
            margin-top: 12px;
            border-bottom: var(--bs-gray-500) solid 1px;
        }

        .sp_filter_text_input_container {
            margin-left:10px;
        }

        .sp_filter_text_input_container .bk-input-group {
            display:flex;
            flex-direction:row;
            width:100%;
            height:100%;
        }

        .sp_filter_text_input_container label {
            padding: 5px 0;
            margin-top: 2px;
            font-size:13px;
            height:100%;
        }

        .sp_filter_text_input_container input, .sp_filter_text_input_container input:focus-visible {
            padding-left: 10px;
            background-color:rgba(0,0,0,0);
            border: none;
            height:100%;
            outline:none;
        }

        .sp_options_list_container label {
            display:flex;
            margin-top:3px;
        }

        .sp_options_list_container label span {
            display:block;
            height:100%;
        }

        .sp_filter_clear_btn {
            padding-top: 4px;
            padding-right: 4px;
        }

        .sp_filter_clear_btn .bk-btn {
            border: lightgray solid 2px;
            fill: lightgray;
        }
        .sp_filter_clear_btn .bk-btn :hover{
            border: black solid 2px;
            fill: black;
        }
        /*
        .sp_options_list_container input[type="checkbox"].intermediary::after {
            content: "-";

            -webkit-transform: translate(-50%,-60%) scale(200%);
            -moz-transform: translate(-50%,-60%) scale(200%);
            -ms-transform: translate(-50%,-60%) scale(200%);
            transform: translate(-50%,-60%) scale(200%);
        }*/

        </style>

    """

    _template = (
        _style
        + _checkbox_group_css
        + """

    <div id="sp_container" class="sp_container">

        <div id="sp_header"  onclick="${script('toggle_list')}" class="sp_header" tabindex="100">
            <p>${title}</p>
        </div>

        <div id="sp_options_list_container" class="sp_options_list_container" style="display:none;">

                <div id="sp_filter" class="sp_filter">
                    <svg data-icon-name="filterIcon" viewBox="0 0 18 18" width="18" height="18" aria-hidden="true" sandboxuid="0">
                        <path fill-rule="evenodd" d="M2 4h14v2H2V4zm2 4h10v2H4V8zm2 4h6v2H6v-2z" sandboxuid="0"></path>
                    </svg>
                    <div id="sp_filter_text_input_container" class="sp_filter_text_input_container">

                        <div class="bk-input-group">
                            <label>Filter</label>
                            <div class="bk-input-container">
                                <input id="filter_text_input" onkeyup="${script('filter_text_input_did_change')}" type="text" class="bk-input" placeholder="Type to filter..." />
                            </div>
                        </div>

                    </div>


                    <div id="sp_filter_clear_btn" class="sp_filter_clear_btn">
                        <div class="bk-btn-group"><button id="clear_filter_button" onclick="${script('clear_filter')}" type="button" class="bk-btn bk-btn-light">X</button></div>
                    </div>
                </div>


                <div id="sp_select_all" class="sp_select_all bk-input-group">
                    <label id="select_all_label" for="select_all">
                        <input type="checkbox" id="select_all_cb" name="select_all_cb" value="select_all" onclick="${script('did_click_select_all')}" checked />
                        <span>Select All</span>
                    </label>
                </div>


                <div id="checkboxes_container" class="checkboxes_container scroll-shadows bk-input-group">


                </div>


        </div>
    </div>
    """
    )

    _scripts = {
        "after_layout": """
        /*console.log("after_layout");*/

           """,
        "input_change": """

            /*console.log("input_change", data, model, state, view);
            console.log(model.checkboxes_list);*/

            let new_value = [];
            model.checkboxes_list.forEach((cb, idx) => {
                if (cb.checked) {
                    new_value.push(cb.value);
                }
            });
            data.value = new_value;

            setTimeout(function() {
                self.update_select_all_checkbox()
            }, 100);

        """,
        "update_select_all_checkbox": """

            /* console.log("update_select_all_checkbox", data.value.length , data.options.length); */

           if ( data.value.length == data.options.length) {
                select_all_cb.checked = true;
                select_all_cb.classList.remove("intermediary");
            } else if ( data.value.length == 0 ) {
                select_all_cb.checked = false;
                select_all_cb.classList.remove("intermediary");
           } else {
                select_all_cb.classList.add("intermediary");
           }


        """,
        "filter_text_input_did_change": """

            /* console.log("filter_text_input_did_change", filter_text_input.value); */
            data.filter_str = filter_text_input.value;

        """,
        "clear_filter": """
            /* console.log("clear filter"); */
            filter_text_input.value = "";
            self.filter_text_input_did_change();
        """,
        "did_click_select_all": """

            /* console.log(select_all_cb, select_all_cb.checked);     */
            model.checkboxes_list.forEach((cb, idx) => {
                cb.checked = select_all_cb.checked;
            });
            self.input_change();

        """,
        "filtered_options": """
            self.rebuild_checkboxes();
        """,
        "rebuild_checkboxes": """

            if ( typeof data.filtered_options === "undefined") {
                /* console.log("rebuild_checkboxes but undefined", data.filtered_options, model.checkboxes_list) */
                return
            }


           /* console.log("rebuild_checkboxes", data.filtered_options, data.value);*/
            new_checkboxes_list = [];

            checkboxes_container.innerHTML = "";

            data.filtered_options.forEach((opt, idx) => {
                let cb = document.createElement("input");
                cb.type = "checkbox";
                cb.id = `cb${idx}`;
                cb.name = `cb${idx}`;
                cb.value = opt;
                cb.checked = true ? data.value.includes(opt) : false;
                cb.onchange = self.input_change;

                let lbl = document.createElement("label");
                lbl.htmlFor = `cb${idx}`;

                let lblspan = document.createElement("span");
                lblspan.innerHTML = opt;

                lbl.appendChild(cb);
                lbl.appendChild(lblspan);

                checkboxes_container.appendChild(lbl);
                /* checkboxes_container.appendChild(document.createElement("br"));
                */


                new_checkboxes_list.push(cb);
            });

            model.checkboxes_list = new_checkboxes_list;

        """,
        "render": """
            console.log("render");
            /*
            console.log("data", data);
            console.log("model", model);
            console.log("state", state);
            console.log("view", view);
            console.log("checkboxes_container", checkboxes_container);
            console.log("sp_options_list_container", sp_options_list_container);
            */
            self.rebuild_checkboxes();
            self.update_select_all_checkbox()

            var isPointerEventInsideElement = function (event, element) {
                var pos = {
                    x: event.targetTouches ? event.targetTouches[0].pageX : event.pageX,
                    y: event.targetTouches ? event.targetTouches[0].pageY : event.pageY
                };
                var rect = element.getBoundingClientRect();
                return  pos.x < rect.right && pos.x > rect.left && pos.y < rect.bottom && pos.y > rect.top;
            };


            function hideOnClickOutside() {

                const outsideClickListener = event => {

                   if ( ! isPointerEventInsideElement(event, sp_options_list_container)
                       && ! isPointerEventInsideElement(event, sp_container)
                       && ! isPointerEventInsideElement(event, sp_header)
                       && sp_options_list_container.style.display != 'none') {

                        sp_options_list_container.style.display = 'none';
                    }
                }

                document.addEventListener('click', outsideClickListener);
            }

            hideOnClickOutside();

        """,
        "toggle_list": """
            if (sp_options_list_container.style.display == '') {
                sp_options_list_container.style.display = 'none';
            } else {
                sp_options_list_container.style.display = '';
            }
        """,
        "remove": """  console.log("remove", state, view); """,
    }
