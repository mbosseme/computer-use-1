from pptx import Presentation
try:
    prs = Presentation("runs/2026-01-06__accelerating_technology_delivery_presentation/assets/Premier_Components.pptx")
    prs.save("runs/2026-01-06__accelerating_technology_delivery_presentation/tmp/test_save.pptx")
    print("Success")
except Exception as e:
    print(e)
