import sys, os

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import *
import xlwings as xw

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy import interpolate

font_name = mpl.font_manager.FontProperties(fname='C:/Windows/Fonts/malgun.ttf').get_name()
mpl.rc('font', family=font_name)
mpl.rc('axes', unicode_minus = False)

MAIN_FILE_NAME = 'main_wnd'

os.system('python -m PyQt5.uic.pyuic -x ' + MAIN_FILE_NAME + '.ui -o ' + MAIN_FILE_NAME + '.py')

from main_wnd import Ui_MainWindow
from pandasModel import *

class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.open_filter()
        self.apply_lib()
        self.btnGraph.clicked.connect(self.draw_graph)
        self.btnExcel.clicked.connect(self.make_excel)
                
        self.df = pd.DataFrame()
        self.lib = pd.DataFrame()
        self.test = pd.DataFrame()

    def open_filter(self):
        os.chdir("P:\개인자료")
        book = xw.Book('Dc-bias_library_V2.xlsx')

        df = book.sheets(1).used_range.options(pd.DataFrame).value
        self.df = pd.DataFrame(df.iloc[1:, :21].dropna(axis = 0, how = 'all').values, columns = df.iloc[0, :21].values)

        vol_lev = [x[7] for x in self.df["기종"]]
        self.df.insert(len(self.df.columns), 'vol_lev', vol_lev)
        self.df.insert(len(self.df.columns), '전압 (Vdc)', 0)

        self.lib = pd.DataFrame(self.df, columns = ["조성","유전율", "vol_lev", "DC-Bias 측정", '전압 (Vdc)', 'sheet 두께', 'DF', '주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'])
        self.lib["유전율"] = [int(x) if x != '사이즈 없음' else x for x in self.lib['유전율']]

        show = self.lib.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis=1)

        txt = "SHBT70(NA272PUG1)"
        filtered = self.lib[self.lib["조성"] == txt]

        diel = list(set(filtered["유전율"]))
        diel = [x for x in diel if pd.isnull(x) == False]
        diel = [ str(x) for x in diel ]

        txt = "4031"
        filtered_sec = filtered[filtered["유전율"] == int(txt) ]

        txt = "저주파"
        self.filtered_thr = filtered_sec[ filtered_sec["DC-Bias 측정"] == txt ]
        self.idx = self.filtered_thr.index
        print(self.filtered_thr, self.idx)

        self.filtered_thr.reset_index(drop = True, inplace =True)
        filtered_show = self.filtered_thr.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis=1)
        self.make_tableLib(filtered_show)
        self.CaplineEdit.clear()

    def apply_lib(self):
        p = list(np.arange(0, 10.1, 0.1))
        self.test = pd.DataFrame()

        vol_lev = 'Q'
        for i in range(len(self.filtered_thr["vol_lev"])):
            df3 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
            self.test = pd.concat([self.test, df3], axis = 1)

        self.fin = self.test.T.reset_index(drop = True)

        for i in range(len(self.fin["vol_lev"])):
            if self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(p)):
                    self.fin['전압 (Vdc)'][i + j] = p[j]

        # sheet 두께 입력 받은 후 전계 칼럼 추가
        # self.st = self.STlineEdit.text()
        st = 0.8 
        ef = self.fin['전압 (Vdc)']/st

        for i in range(len(ef)):
            ef[i] = np.round(ef[i], 2)

        self.fin.insert(len(self.fin.columns), '전계 (V/um)', ef)

        self.fin.drop(columns = ['vol_lev', 'DC-Bias 측정','DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], inplace = True)
        print(self.fin)
        
        # const = [[-5.902346, 0.5393833, 0.5186153, 2.0273025, 0.447222]]
        self.cst = pd.DataFrame(self.df.iloc[self.idx], columns = ['a', 'b', 'c', 'd', 'f'])
        self.cst.columms = ["a (증가율)", "b (변곡점)", "c (점근선 1)", "d (점근선 2)", "f (검정력)"]

        self.const = [float(x) for x in self.cst.iloc[0].values]

        cap_pct = []
        for i in range(len(self.fin['전계 (V/um)'])):
            cap_pct.append( 10 ** (self.const[2] + (self.const[3] - self.const[2])/(1 + np.exp(-self.const[0] * (np.log( 1 + self.fin['전계 (V/um)'][i]) - self.const[1]))) ** self.const[4]) )
          
        self.fin.insert(len(self.fin.columns), '용량변화율 %', cap_pct)

        p_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10]
        # cap = self.CaplineEdit.text()
        cap = 1 
             
        self.low = self.fin.copy()
        low_cap = float(cap) * self.fin['용량변화율 %'] * 0.01
        self.low.insert(len(self.low.columns), '저주파 유효 용량', low_cap)
        self.low.drop(['sheet 두께'], axis=1, inplace=True)

        self.low_show = self.low.copy()
        self.low_show['용량변화율 %'] = np.round(self.low_show['용량변화율 %'], 2)
        self.low_show['저주파 유효 용량'] = np.round(self.low_show['저주파 유효 용량'], 2)

        # 보이는 테이블 전압 필터링
        self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(p_show)]
        self.make_tableLib(self.low_show)
        self.make_tableConst(self.cst)
       
    def make_tableLib(self, df):
        model = pandasModel(df)
        self.tableLib.setModel(model)
        self.tableLib.resizeColumnsToContents()
        self.tableLib.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableLib.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)       

    def make_tableConst(self, df):
        self.tableConst.setHidden(False)
        model = pandasModel(df)
        self.tableConst.setModel(model)
        self.tableConst.resizeColumnsToContents()
        self.tableConst.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableConst.verticalHeader().setSectionResizeMode(QHeaderView.Stretch) 

    def draw_graph(self):
        x = [float(a) for a in self.fin['전압 (Vdc)'].values]
        y = self.fin['용량변화율 %'].values

        xs = np.linspace(x[0], x[-1], 1000)
        f = interpolate.interp1d(x, y, kind = 'linear')

        ys = f(xs)
        
        xp = [float(a) for a in self.low_show['전압 (Vdc)'].values]
        yp = self.low_show['용량변화율 %'].values
        
        plt.scatter(xp,yp, color = 'red')
        plt.plot(xs, ys)

        plt.xlabel('전압 (V)')
        plt.ylabel('용량변화율 %')

        plt.grid(True)
        plt.show()

    def make_excel(self):
        new_file = 'DC-bias library 분석'
        
        newfile = 'P:.\\..\\{}.xlsx'.format(new_file)
        # newfile = './{}.xlsx'.format(new_file)
        writer = pd.ExcelWriter(newfile)
        self.low.to_excel(writer, index=False, engine = 'openpyxl')
        writer.save()
        QMessageBox.information(self, '저장완료', '성공적으로 저장되었습니다.')
  
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    app.exec_()

# import sys
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import QDoubleValidator
# from PyQt5 import uic
 
# # UI = 'calculator_200429.ui'
# class Dialog(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setupUi()
#         self.calculator()
   
#     def setupUi(self):
#         self.setWindowTitle('LineEdit')
#         self.resize(300, 300)

#         self.line_edit = QLineEdit(self)
#         self.line_edit.setValidator(QDoubleValidator(1,100,3,self))
#         self.line_edit.move(75,75)

#         self.button = QPushButton(self)
#         self.button.move(75, 175)
#         self.button.setText('Get Text')
#         self.button.clicked.connect(self.calculator)

#     def calculator(self):
#         # self.st = self.STlineEdit.text()

#         text = self.line_edit.text() # line_edit text 값 가져오기
#         print(type(text), text)
#         st = float(text)
#         print(type(st), st)
#         ef = 10/0.8
#         print(ef)


# app = QApplication(sys.argv)
# ex = Dialog()
# ex.show()
# sys.exit(app.exec_())