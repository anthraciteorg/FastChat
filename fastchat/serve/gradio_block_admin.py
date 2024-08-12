import gradio as gr
from fastchat.serve.gradio_web_server import api_endpoint_info, db
import os
    
def load_admin_tab():
    return ()

def build_admin_tab():
    endpoints_state = gr.State([])

    password_input = gr.Textbox(type="password", label="Enter Password")
    submit_button = gr.Button("Access Protected Content")

    
    @gr.render(inputs=[endpoints_state])
    def endpoint_list(endpoints):
        for i, endpoint in enumerate(endpoints):
            with gr.Accordion(label=endpoint["key"]):
                model_name = gr.Textbox(value=endpoint["model_name"], label="API Model Name", interactive=True)
                with gr.Row():
                    base_url = gr.Textbox(value=endpoint["api_base"], label="API Base Url", interactive=True)
                    api_key = gr.Textbox(value=endpoint.get("api_key", ""), label="API Key", type="password", interactive=True)
                    endpoint_type = gr.Dropdown(value=endpoint["api_type"], choices=["openai", "aphrodite"], label="API Type", interactive=True, scale=0)
                with gr.Row():
                    delete = gr.Button("Delete")
                    update = gr.Button("Update")
                key = gr.State(endpoint["key"])

                @gr.on(update.click, inputs=[key, model_name, base_url, api_key, endpoint_type], outputs=[endpoints_state])
                def update_endpoint(key, model_name, base_url, api_key, endpoint_type):
                    db["model_endpoints"].update_one({ "key": key }, {"$set": {
                        "model_name": model_name,
                        "api_base": base_url,
                        "api_key": api_key,
                        "api_type": endpoint_type,
                    }})
                    return db["model_endpoints"].find({})

                @gr.on(delete.click, inputs=[key], outputs=[endpoints_state])
                def delete_endpoint(key):
                    db["model_endpoints"].find_one_and_delete({ "key": key })
                    return db["model_endpoints"].find({})
        
    with gr.Group(visible=False) as create_group:
        with gr.Row():
            model_key = gr.Textbox(label="Arena Model Name", interactive=True)
            model_name = gr.Textbox(label="API Model Name", interactive=True)
        with gr.Row():
            base_url = gr.Textbox(label="API Base Url", interactive=True)
            api_key = gr.Textbox(label="API Key", interactive=True)
            endpoint_type = gr.Dropdown(value=1, choices=["openai", "aphrodite"], label="Endpoint Type", interactive=True, scale=0)
        create = gr.Button("Create Endpoint")

        @gr.on(create.click, inputs=[model_key, model_name, base_url, api_key, password_input, endpoint_type], outputs=[endpoints_state])
        def create_endpoint(model_key, name, url, api_key, password, endpoint_type):
            if password == os.environ["ADMIN_TOKEN"]:
                model = {
                    "text-arena": True,
                    "anony_only": False,
                    "model_name": name,
                    "api_base": url,
                    "api_type": endpoint_type 
                }
                if api_key != "":
                    model["api_key"] = api_key
                db["model_endpoints"].insert_one(
                    {
                        "key": model_key,
                        **model
                    }
                )
                return list(db["model_endpoints"].find({}))
            return []

    @gr.on(submit_button.click, inputs=[password_input, endpoints_state], outputs=[password_input, submit_button, create_group, endpoints_state])
    def hide_group(password, endpoints):
        if password == os.environ["ADMIN_TOKEN"]:
            return [gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), list(db["model_endpoints"].find({}))]
        return [gr.update(visible=True), gr.update(visible=True),gr.update(visible=False), []]

    return []