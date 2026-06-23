import ipywidgets as widgets
import math
import os
from IPython.display import display
from AI_description import make_description

# Constants
THUMBNAIL_WIDTH = '120px'
ITEMS_PER_PAGE = 10

def create_ui_interface(results_map, images_lookup, class_names, cm):
    """
    Creates the UI interface
    """
    # 1. Setup Internal Containers
    out = widgets.Output(layout=widgets.Layout(display='block'))
    detail_view = widgets.VBox(layout=widgets.Layout(display='none'))
    
    # 2. Internal Handler Logic
    def handle_matrix_click(i, j):
        def handler(b):
            print("Entered the handler")
            out.clear_output(wait=True)
            with out:
                
                paths = results_map.get((i, j), [])
                
                if not paths:
                    display(widgets.HTML(f"<h3>No images found for {class_names[i]} as {class_names[j]}</h3>"))
                    return

                print("displaying the title")
                display(widgets.HTML(f"<h3>Viewing: {class_names[i]} as {class_names[j]} ({len(paths)} images)</h3>"))
                
                print("displaying the gallery")
                # Call the gallery builder (also in this file)
                gallery = create_gallery(paths, images_lookup, out, detail_view)
                display(gallery)
        return handler

    # 3. Build the Matrix UI using the internal handler
    matrix_ui = create_confusion_matrix(cm, class_names, handle_matrix_click)

    # 4. Return everything as a single layout
    return widgets.VBox([matrix_ui, out, detail_view])

def create_confusion_matrix(cm, class_names, handler_factory):
    """
    Creates the Confusion Matrix UI component.
    handler_factory: a function that returns a click handler for (i, j)
    """
    buttons_grid = []
    
    # Header Row
    header_labels = [widgets.Label(layout=widgets.Layout(width='100px'))]
    for name in class_names:
        label = widgets.Label(value=f"Pred {name}", layout=widgets.Layout(width='100px'))
        label.add_class("cm-header-label")
        header_labels.append(label)

    buttons_grid.append(widgets.HBox(header_labels))
    
    # Data Rows
    for i in range(len(class_names)):
        col_label = widgets.Label(value=f"Actual {class_names[i]}", layout=widgets.Layout(width='100px'))
        col_label.add_class("cm-col-label")
        row = [col_label]
        for j in range(len(class_names)):
            color = '#c8e6c9' if i == j else '#ffcdd2'
            btn = widgets.Button(description=str(cm[i, j]))
            btn.add_class("cm-button")
            btn.style.button_color = color
            # Use the factory to get the handler for this specific cell
            btn.on_click(handler_factory(i, j))
            row.append(btn)
        buttons_grid.append(widgets.HBox(row))

    container = widgets.VBox([
        widgets.HTML("<h2>Confusion Matrix</h2>"), 
        widgets.VBox(buttons_grid)
    ])
    container.add_class("cm-container")
    return container

def create_ai_column(path, title):
    with open(path, "rb") as f:
        img_data = f.read()
    
    img_widget = widgets.Image(value=img_data, width="250px")
    desc_label = widgets.HTML("<i>Click button to analyze...</i>")
    analyze_btn = widgets.Button(description=f"Analyze {title}", button_style='info')
    
    def on_analyze_clicked(b):
        analyze_btn.disabled = True
        desc_label.value = "<b>AI is thinking...</b>"
        try:
            response = make_description(path)
            data = response.json()
            if "error" in data:
                desc_label.value = f"<b style='color:red;'>API Error: {data['error'].get('message', data['error'])}</b>"
            else:
                content = data["choices"][0]["message"]["content"]
                desc_label.value = f"<div style='width:250px;'>{content}</div>"
        except Exception as e:
            desc_label.value = f"<b style='color:red;'>Exception: {e}</b>"
        analyze_btn.disabled = False
        #     content = response.json()["choices"][0]["message"]["content"]
        #     desc_label.value = f"<div style='width:250px;'>{content}</div>"
        # except Exception:
        #     print(content)
        #     desc_label.value = "<b style='color:red;'>Error: Wait 10s (API free tier limit)</b>"
        # analyze_btn.disabled = False

    analyze_btn.on_click(on_analyze_clicked)
    return widgets.VBox([widgets.HTML(f"<b>{title}</b>"), img_widget, analyze_btn, desc_label])

def create_detail_view(img_path, images_lookup, out_widget, detail_widget):    
    back_btn = widgets.Button(description="<- Back to Gallery", button_style='warning')
    
    def go_back(b):
        detail_widget.layout.display = 'none'
        out_widget.layout.display = 'block'
    back_btn.on_click(go_back)

    original_col = create_ai_column(img_path, "Original")
    heatmap_col = create_ai_column(images_lookup[img_path]["heatMap"], "Heatmap")
    outline_col = create_ai_column(images_lookup[img_path]["outlined"], "Outline")

    detail_widget.children = [
        back_btn, 
        widgets.HTML(f"<h4>Detail View</h4>"),
        widgets.HBox([original_col, heatmap_col, outline_col])
    ]
    
    out_widget.layout.display = 'none'
    detail_widget.layout.display = 'flex'

def create_gallery(paths, images_lookup, out_widget, detail_widget):
    total_pages = math.ceil(len(paths) / ITEMS_PER_PAGE)
    pages = []
    
    for page_num in range(total_pages):
        start_idx = page_num * ITEMS_PER_PAGE
        page_paths = paths[start_idx : start_idx + ITEMS_PER_PAGE]
        
        items = []
        for p in page_paths:
            with open(p, "rb") as f:
                img_widget = widgets.Image(value=f.read(), width=THUMBNAIL_WIDTH, height=THUMBNAIL_WIDTH)
            btn = widgets.Button(description="View Details", layout=widgets.Layout(width=THUMBNAIL_WIDTH))
            # Pass everything the detail view needs
            btn.on_click(lambda b, p=p: create_detail_view(p, images_lookup, out_widget, detail_widget))
            items.append(widgets.VBox([img_widget, btn], layout=widgets.Layout(align_items='center')))
            
        grid = widgets.GridBox(items, layout=widgets.Layout(grid_template_columns="repeat(5, 1fr)", grid_gap='15px'))
        pages.append(grid)
    
    tabs = widgets.Tab(children=pages)
    for i in range(total_pages): tabs.set_title(i, f"Page {i+1}")
    return tabs