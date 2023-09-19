import sys, os

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import openpyxl
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

        self.actionOpen_2.triggered.connect(self.open_file)
        #  activated[str]은 QComboBox의 옵션의 문자열을 받아 전달한다.  
        self.cboPow.activated[str].connect(self.filter_fir)
        self.cboDiel.textActivated.connect(self.filter_sec)
        self.cboFreq.textActivated.connect(self.filter_thr)
        self.btnApply.clicked.connect(self.apply_lib)       
        self.btnGraph.clicked.connect(self.draw_graph)
        self.btnExcel.clicked.connect(self.make_excel)
        self.lblvdc.setHidden(True)
        self.lblratio.setHidden(True)
        self.lblvdc_name.setHidden(True)
        self.lblratio_name.setHidden(True)

        self.df = pd.DataFrame()
        self.lib = pd.DataFrame()
        self.test = pd.DataFrame()

        # 모델식 UI 출력
        pixmap = QPixmap("equation.png")
        self.lbleqn.setPixmap(QPixmap(pixmap))

    def open_file(self):
        show_filter = "모든 파일(*.*);;엑셀파일(*.xls);; 엑셀파일(*.xlsx)"
        init_filter = "엑셀파일(*.xlsx)"
        opt = QFileDialog.Option()
        file_name, filter_type = QFileDialog.getOpenFileName(filter=show_filter, initialFilter=init_filter, options=opt)

        if file_name:
            self.setWindowTitle(file_name.split('/')[-1])

            # self.df = pd.read_excel(file_name, header = 1, usecols = "C:W", engine = 'openpyxl')

            book = xw.Book(file_name)
            df = book.sheets(1).used_range.options(pd.DataFrame).value
            self.df = pd.DataFrame(df.iloc[1:, :21].dropna(axis = 0, how = 'all').values, columns = df.iloc[0, :21].values)

            vol_lev = [x[7] for x in self.df["기종"]]
            self.df.insert(len(self.df.columns), 'vol_lev', vol_lev)
            self.df.insert(len(self.df.columns), '전압 (Vdc)', 0)

            mat = list(set(self.df["조성"]))
            mat = [x for x in mat if pd.isnull(x) == False]
            mat.sort()
            self.cboPow.addItems(mat)

            self.lib = pd.DataFrame(self.df, columns = ["조성","유전율", "vol_lev", "DC-Bias 측정", '전압 (Vdc)', 'sheet 두께', 'DF', '주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'])
            self.lib["유전율"] = [int(x) if x != '사이즈 없음' else x for x in self.lib['유전율']]
            show = self.lib.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis=1)

            self.make_tableLib(show)

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

    def filter_fir(self, txt):
        #다른 항목 초기화
        self.lblvdc.setHidden(True)
        self.lblratio.setHidden(True)
        self.lblvdc_name.setHidden(True)
        self.lblratio_name.setHidden(True)

        self.lblfreq.clear()
        self.lblac.clear()
        self.lblaging.clear()
        self.lbltime.clear()
        self.lbldf.clear()
        self.CaplineEdit.clear()
        self.STlineEdit.clear()

        self.cboDiel.clear()
        self.cboFreq.clear()

        # 콤보박스로 원하는 조성 선택
        self.filtered = self.lib[ self.lib["조성"] == txt ]

        diel = list(set(self.filtered["유전율"]))
        diel = [x for x in diel if pd.isnull(x) == False]
        diel = [ str(x) for x in diel ]
        diel.sort()
        self.cboDiel.addItems(diel)
        filtered_show = self.filtered.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis = 1)
        self.make_tableLib(filtered_show)

    def filter_sec(self, txt):
        # 다른 항목 초기화
        self.lblvdc.setHidden(True)
        self.lblratio.setHidden(True)
        self.lblvdc_name.setHidden(True)
        self.lblratio_name.setHidden(True)

        # 콤보박스로 원하는 유전율 선택
        self.filtered_sec = self.filtered[ self.filtered["유전율"] == int(txt) ]

        # 선택한 유전율에 해당되는 DF 값 디스플레이
        self.lbldf.setNum(np.round(self.filtered_sec['DF'].iloc[0], 4))

        self.cboFreq.clear()
        freq = list(set(self.filtered_sec["DC-Bias 측정"]))
        freq = [x for x in freq if pd.isnull(x) == False]
        freq.sort()
        self.cboFreq.addItems(freq)
        filtered_show = self.filtered_sec.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis=1)
        self.make_tableLib(filtered_show)

    def filter_thr(self, txt):
        # 다른 항목 초기화
        self.lblvdc.setHidden(True)
        self.lblratio.setHidden(True)
        self.lblvdc_name.setHidden(True)
        self.lblratio_name.setHidden(True)

        # 콤보박스로 원하는 주파수 영역 선택
        self.filtered_thr = self.filtered_sec[ self.filtered_sec["DC-Bias 측정"] == txt ]

        #필터링된 기종 인덱스 따오기
        self.idx = self.filtered_thr.index

        # 선택한 SPL에 해당되는 측정조건 디스플레이
        self.lblac.setNum(self.filtered_thr['AC(V)'].iloc[0])
        self.lblfreq.setNum(self.filtered_thr['주파수(kHz)'].iloc[0])
        self.lbltime.setText(self.filtered_thr['전압유지시간'].iloc[0])
        self.lblaging.setText(self.filtered_thr['Aging 시간'].iloc[0])

        #인덱스 리셋
        self.filtered_thr.reset_index(drop = True, inplace =True)
        filtered_show = self.filtered_thr.drop(['vol_lev', '전압 (Vdc)', 'DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], axis=1)
        self.make_tableLib(filtered_show)

    def apply_lib(self):
        p = list(np.arange(0, 10.1, 0.1))
        o = list(np.arange(0, 16.1, 0.1))
        a = list(np.arange(0, 25.1, 0.1))
        l = list(np.arange(0, 35.1, 0.1))
        bce = list(np.arange(0, 40.1, 0.1))

        self.test = pd.DataFrame()

        # 전압 scale만큼 기존 칼럼 복사해서 추가 (빈 데이터프레임에다가 생성)
        for i in range(len(self.filtered_thr["vol_lev"])):
            if self.filtered_thr['vol_lev'][i] == 'S':
                df1 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
                self.test = pd.concat([self.test, df1], axis = 1)
            elif self.filtered_thr['vol_lev'][i] == 'R':
                df2 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
                self.test = pd.concat([self.test, df2], axis = 1)
            elif self.filtered_thr['vol_lev'][i] == 'Q':
                df3 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
                self.test = pd.concat([self.test, df3], axis = 1)
            elif self.filtered_thr['vol_lev'][i] == 'P':
                df4 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
                self.test = pd.concat([self.test, df4], axis = 1)
            elif self.filtered_thr['vol_lev'][i] == 'O':
                df5 = pd.concat([self.filtered_thr.iloc[i]]*len(o), axis = 1)
                self.test = pd.concat([self.test, df5], axis = 1)
            elif self.filtered_thr['vol_lev'][i] == 'A':
                df6 = pd.concat([self.filtered_thr.iloc[i]] * len(a), axis=1)
                self.test = pd.concat([self.test, df6], axis=1)
            elif self.filtered_thr['vol_lev'][i] == 'L':
                df7 = pd.concat([self.filtered_thr.iloc[i]] * len(l), axis=1)
                self.test = pd.concat([self.test, df7], axis=1)
            elif self.filtered_thr['vol_lev'][i] == 'B' or 'C' or 'E':
                df8 = pd.concat([self.filtered_thr.iloc[i]] * len(bce), axis=1)
                self.test = pd.concat([self.test, df8], axis=1)
        self.fin = self.test.T.reset_index(drop = True)

        # 전압 칼럼에 전압 정보 추가
        for i in range(len(self.fin["vol_lev"])):
            if self.fin['vol_lev'][i] == 'S' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(p)):
                    self.fin['전압 (Vdc)'][i + j] = p[j]
            elif self.fin['vol_lev'][i] == 'R' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(p)):
                    self.fin['전압 (Vdc)'][i + j] = p[j]
            elif self.fin['vol_lev'][i] == 'Q' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(p)):
                    self.fin['전압 (Vdc)'][i + j] = p[j]
            elif self.fin['vol_lev'][i] == 'P' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(p)):
                    self.fin['전압 (Vdc)'][i + j] = p[j]
            elif self.fin['vol_lev'][i] == 'O' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(o)):
                    self.fin['전압 (Vdc)'][i + j] = o[j]
            elif self.fin['vol_lev'][i] == 'A' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(a)):
                    self.fin['전압 (Vdc)'][i + j] = a[j]
            elif self.fin['vol_lev'][i] == 'L' and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(l)):
                    self.fin['전압 (Vdc)'][i + j] = l[j]
            elif (self.fin['vol_lev'][i] == 'B'or 'C'or'E') and self.fin['전압 (Vdc)'][i] == 0:
                for j in range(len(bce)):
                    self.fin['전압 (Vdc)'][i + j] = bce[j]

        # sheet 두께 입력 받은 후 전계 칼럼 추가
        self.st = self.STlineEdit.text()
        ef = self.fin['전압 (Vdc)']/float(self.st)
        for i in range(len(ef)):
            ef[i] = np.round(ef[i], 2)
        self.fin.insert(len(self.fin.columns), '전계 (V/um)', ef)

        self.fin.drop(columns = ['vol_lev', 'DC-Bias 측정','DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], inplace = True)

        # 선택한 기종에 따른 상수값 테이블 추출
        self.cst = pd.DataFrame(self.df.iloc[self.idx], columns = ['a', 'b', 'c', 'd', 'f'])
        self.cst.columns = ['a (증가율)', 'b (변곡점)', 'c (점근선 1)', 'd (점근선 2)', 'f (검정력)']
        self.const = [float(x) for x in self.cst.iloc[0].values]

        # 로지스틱 모델링식을 이용하여 용량변화율 계산 및 해당 칼럼 추가
        cap_pct = []
        for i in range(len(self.fin['전계 (V/um)'])):
            cap_pct.append( 10 ** (self.const[2] + (self.const[3] - self.const[2])/(1 + np.exp(-self.const[0] * (np.log( 1 + self.fin['전계 (V/um)'][i]) - self.const[1]))) ** self.const[4]) )

        self.fin.insert(len(self.fin.columns), '용량변화율 %', cap_pct)

        p_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10]
        o_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16]
        a_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25]
        l_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25, 35]
        bce_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25, 35, 40]
        
        # 필요용량 입력 값 이용하여 유효용량 계산 및 해당 칼럼 추가 (주파수 영역 구분)
        cap = self.CaplineEdit.text()

        if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
            self.lblvdc.setHidden(True)
            self.lblratio.setHidden(True)
            self.lblvdc_name.setHidden(True)
            self.lblratio_name.setHidden(True)
            self.low = self.fin.copy()
            low_cap = float(cap) * self.fin['용량변화율 %'] * 0.01
            self.low.insert(len(self.low.columns), '저주파 유효 용량', low_cap)
            self.low.drop(['sheet 두께'], axis=1, inplace=True)

            self.low_show = self.low.copy()
            self.low_show['용량변화율 %'] = np.round(self.low_show['용량변화율 %'], 2)
            self.low_show['저주파 유효 용량'] = np.round(self.low_show['저주파 유효 용량'], 2)

            # 보이는 테이블 전압 필터링
            if self.low_show['전압 (Vdc)'].iloc[-1] == 10:
                self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(p_show)]
            elif self.low_show['전압 (Vdc)'].iloc[-1] == 16:
                self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(o_show)]
            elif self.low_show['전압 (Vdc)'].iloc[-1] == 25:
                self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(a_show)]
            elif self.low_show['전압 (Vdc)'].iloc[-1] == 35:
                self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(l_show)]
            elif self.low_show['전압 (Vdc)'].iloc[-1] == 40:
                self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(bce_show)]

            self.make_tableLib(self.low_show)

        elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
            self.high = self.fin.copy()
            high_ratio = self.df['변화율'][self.idx].values[0]
            high_vdc = self.df['0Vdc 용량'][self.idx].values[0]
            self.lblvdc.setHidden(False)
            self.lblratio.setHidden(False)
            self.lblvdc_name.setHidden(False)
            self.lblratio_name.setHidden(False)
            self.lblratio.setText(str(np.round(high_ratio * 100, 2)))
            self.lblvdc.setText(str(np.round(high_vdc, 2)))
            high_cap = (high_ratio * self.fin['용량변화율 %']) * 0.01 * float(cap)
            self.high.insert(len(self.high.columns), '고주파 유효 용량', high_cap, 2)
            self.high.drop(['sheet 두께'], axis=1, inplace=True)

            self.high_show = self.high.copy()
            self.high_show['용량변화율 %'] = np.round(self.high_show['용량변화율 %'], 2)
            self.high_show['고주파 유효 용량'] = np.round(self.high_show['고주파 유효 용량'], 2)

            # 보이는 테이블 전압 필터링
            if self.high_show['전압 (Vdc)'].iloc[-1] == 10:
                self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(p_show)]
            elif self.high_show['전압 (Vdc)'].iloc[-1] == 16:
                self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(o_show)]
            elif self.high_show['전압 (Vdc)'].iloc[-1] == 25:
                self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(a_show)]
            elif self.high_show['전압 (Vdc)'].iloc[-1] == 35:
                self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(l_show)]
            elif self.high_show['전압 (Vdc)'].iloc[-1] == 40:
                self.highw_show = self.high_show[self.high_show['전압 (Vdc)'].isin(bce_show)]

            self.make_tableLib(self.high_show)
        self.make_tableConst(self.cst)

    def draw_graph(self):
        x = [float(a) for a in self.fin['전압 (Vdc)'].values]
        y = self.fin['용량변화율 %'].values

        xs = np.linspace(x[0], x[-1], 1000)
        f = interpolate.interp1d(x, y, kind = 'linear')

        ys = f(xs)

        if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
            xp = [float(a) for a in self.low_show['전압 (Vdc)'].values]
            yp = self.low_show['용량변화율 %'].values
        elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
            xp = [float(a) for a in self.high_show['전압 (Vdc)'].values]
            yp = self.high_show['용량변화율 %'].values

        plt.scatter(xp,yp, color = 'red')
        plt.plot(xs, ys)

        plt.xlabel('전압 (V)')
        plt.ylabel('용량변화율 %')

        plt.grid(True)
        plt.show()

    def make_excel(self):
        new_file = self.fileLineEdit.text()
        if not new_file:
            QMessageBox.warning(self, 'warning', '파일 이름을 입력해주세요.')
        else:
            newfile = 'P:.\\..\\{}.xlsx'.format(new_file)
            # newfile = './{}.xlsx'.format(new_file)
            writer = pd.ExcelWriter(newfile)
            if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
                self.low.to_excel(writer, index=False, engine = 'openpyxl')
            elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
                self.high.to_excel(writer, index=False, engine = 'openpyxl')
            writer.save()
            QMessageBox.information(self, '저장완료', '성공적으로 저장되었습니다.')

    def my_exception_hook(exctype, value, traceback, self=None):
        # Print the error and traceback
        print(exctype, value, traceback)

        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        QMessageBox.warning(self, '오류', '올바르지 않은 접근입니다.')
        # sys.exit(1)

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())