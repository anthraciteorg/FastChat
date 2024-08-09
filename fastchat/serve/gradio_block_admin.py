import gradio as gr
from fastchat.serve.gradio_web_server import api_endpoint_info
import os
    
def load_admin_tab():
    return ()

def build_admin_tab():
    endpoints_state = gr.State([])

    with gr.Group(visible=True) as login_group:
        password_input = gr.Textbox(type="password", label="Enter Password")
        submit_button = gr.Button("Access Protected Content")

    
    @gr.render(inputs=[endpoints_state])
    def endpoint_list(endpoints):
        for i, endpoint in enumerate(endpoints):
            with gr.Accordion(label=endpoint["key"]):
                model_name = gr.Textbox(value=endpoint["model_name"], label="API Model Name", interactive=False)
                base_url = gr.Textbox(value=endpoint["api_base"], label="API Base Url", interactive=False)
                delete = gr.Button("Delete")
                key = gr.State(endpoint["key"])

                @gr.on(delete.click, inputs=[key], outputs=[endpoints_state])
                def delete_endpoint(key):
                    del api_endpoint_info[key]
                    endpoints = [{"key": key, **value} for key, value in api_endpoint_info.items()] 
                    return endpoints
        
    with gr.Group(visible=False) as create_group:
        with gr.Row():
            model_key = gr.Textbox(label="Arena Model Name", interactive=True)
            model_name = gr.Textbox(label="API Model Name", interactive=True)
        with gr.Row():
            base_url = gr.Textbox(label="API Base Url", interactive=True)
            api_key = gr.Textbox(label="API Key", interactive=True)
        create = gr.Button("Create Endpoint")

        @gr.on(create.click, inputs=[model_key, model_name, base_url, api_key, password_input], outputs=[endpoints_state])
        def create_endpoint(model_key, name, url, api_key, password):
            if password == os.environ["ADMIN_TOKEN"]:
                api_endpoint_info[model_key] = {
                    "text-arena": True,
                    "anony_only": False,
                    "model_name": name,
                    "api_base": url,
                    "recommended_config": {
                        "temperature": 1.0,
                        "top_p": 1.0,
                        "min_p": 0.0,
                        "max_new_tokens": 200
                    },
                    "api_type": "aphrodite"
                }
                if api_key != "":
                    api_endpoint_info[model_key] = api_key
                endpoints = [{"key": key, **value} for key, value in api_endpoint_info.items()] 
                return endpoints
            return []

    @gr.on(submit_button.click, inputs=[password_input, endpoints_state], outputs=[login_group, create_group, endpoints_state])
    def hide_group(password, endpoints):
        if password == os.environ["ADMIN_TOKEN"]:
            endpoints = [{"key": key, **value} for key, value in api_endpoint_info.items()]
            return [gr.update(visible=False), gr.update(visible=True), endpoints]
        return [gr.update(visible=True),gr.update(visible=False), []]

    return []