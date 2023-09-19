import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import *
from PyQt5 import QtGui
import pandas as pd

df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                   'b': [100, 200, 300],
                   'c': [16.12365, -32.5487, 0]})


class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self.data = data

    def rowCount(self, parent=None):
        return self.data.shape[0]

    def columnCount(self, parnet=None):
        return self.data.shape[1]

    def data(self, index, role):
        if index.isValid():
            value = self.data.iloc[index.row(), index.column()]
            if role == Qt.DisplayRole:
                # if isinstance(value, datetime):
                #     # Render time to YYY-MM-DD.
                #     return value.strftime("%Y-%m-%d")

                if isinstance(value, float):
                    return "%.2f" % value

                if isinstance(value, str):
                    return "%s" % value   
                
                # if isinstance(value, int):
                #     return value  

                # Default (anything not captured above: e.g. int)
                # return value     
               
                # if not index.isValid() or role != Qt.DisplayRole:
                #     return QVariant()

                return str(value)

            if role == Qt.TextAlignmentRole:
                if isinstance(value, int) or isinstance(value, float):
                    return Qt.AlignRight|Qt.AlignVCenter
                return Qt.AlignCenter

            if role == Qt.ForegroundRole:
                if (isinstance(value, int) or isinstance(value, float)) and value <= 0:
                    return QtGui.QColor('red')
        return None 

  
#         
#        if role == Qt.DecorationRole: # Qt.BackgroundRole
#           value = self._data[index.row()][index.column()]
#           if (isinstance(value, int) or isinstance(value, float)):
#               value = int(value)

#               # Limit to range -5 ... +5, then convert to 0..10
#               value = max(-5, value)  # values < -5 become -5
#               value = min(5, value)   # valaues > +5 become +5
#               value = value + 5       # -5 becomes 0, +5 becomes + 10

#               return QtGui.QColor(COLORS[value])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return self.data.columns[section]

        elif orientation == Qt.Vertical:
            return str(self.data.index[section])

    # data 함수 기능 구현 문제로 일단 미사용
    """
    def flags(self, index):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def setData(self, index, value, role):
            if not index.isValid():
                return QVariant()
            if role == Qt.DisplayRole or role == Qt.EditRole:
                self.df.iloc[index.row(), index.column()] = value
                self.dataChanged.emit(index, index)
                return True
            return QVariant()
    """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = pandasModel(df)
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())