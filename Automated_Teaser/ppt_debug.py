from pptx import Presentation

prs = Presentation("Layout.pptx")

layout_index = 3

slide_layout = prs.slide_layouts[layout_index]

print(f"Details for layout {layout_index}: {slide_layout.name}")
for placeholder in slide_layout.placeholders:
    print(f"Placeholder index: {placeholder.placeholder_format.idx}, Type: {placeholder.placeholder_format.type}, Name: '{placeholder.name}'")