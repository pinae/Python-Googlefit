from PyQt5.QtWidgets import QWidgetItem


def clear_layout(layout):
    while layout.count() > 0:
        item = layout.itemAt(0)
        if type(item) is QWidgetItem:
            widget = item.widget()
        else:
            widget = None
        layout.removeItem(item)
        del item
        if widget is not None:
            widget.setVisible(False)
            widget.setParent(None)
            del widget
