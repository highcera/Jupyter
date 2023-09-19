import sys, os

import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
# import openpyxl
import xlwings as xw

import numpy as np
import matplotlib as mpl
# import matplotlib.pyplot as plt
# from scipy.interpolate import make_interp_spline
# from scipy import interpolate

font_name = mpl.font_manager.FontProperties(fname='C:/Windows/Fonts/malgun.ttf').get_name()
mpl.rc('font', family=font_name)
mpl.rc('axes', unicode_minus = False)

MAIN_FILE_NAME = 'main_wnd2'

os.system('python -m PyQt5.uic.pyuic -x ' + MAIN_FILE_NAME + '.ui -o ' + MAIN_FILE_NAME + '.py')

from main_wnd2 import Ui_MainWindow
from mypandasModel import *

class Form(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.actionOpen_2.triggered.connect(self.open_file)
        self.cboPowsize.activated[str].connect(self.filter_fir)
        self.cboPowder.activated[str].connect(self.filter_sec)
        self.cboCompo.activated[str].connect(self.filter_thr)
        self.cboSheetT.activated[str].connect(self.filter_four)
        self.cboLot.activated[str].connect(self.filter_last) 
        
        self.btnApply.clicked.connect(self.apply_lib)
        #        self.btnGraph.clicked.connect(self.draw_graph)
        #        self.btnExcel.clicked.connect(self.make_excel)

        self.chip_name.setHidden(True)
        self.material.setHidden(True)
        self.sheet_T.setHidden(True)
        self.lot_no.setHidden(True)

        self.df = pd.DataFrame()
        self.lib = pd.DataFrame()
        self.test = pd.DataFrame()

    def open_file(self):
        os.chdir("P:\개인자료")
        show_filter = "모든 파일(*.*);;엑셀파일(*.xls);; 엑셀파일(*.xlsx)"
        init_filter = "엑셀파일(*.xlsx)"
        opt = QFileDialog.Option()
        file_name, filter_type = QFileDialog.getOpenFileName(filter=show_filter, initialFilter=init_filter, options=opt)

        if file_name:
            self.setWindowTitle(file_name.split('/')[-1])

            # self.df = pd.read_excel(file_name, header = 1, usecols = "C:W", engine = 'openpyxl')

            book = xw.Book(file_name)
            df = book.sheets(1).used_range.options(pd.DataFrame).value
            self.df = pd.DataFrame(df.iloc[1:, :50].dropna(axis = 0, how = 'all').values, columns = df.iloc[0, :50].values)

            self.df['파우더 사이즈']= self.df['파우더 사이즈'].astype(int)
            self.df[['시험전계', '유전체두께']] = self.df[['시험전계', '유전체두께']].astype(float)
            self.df[['시험전계', '유전체두께']] = self.df[['시험전계', '유전체두께']].round(1)

            pSize = list(set(self.df["파우더 사이즈"]))
            pSize = [x for x in pSize if pd.isnull(x) == False]
            print(pSize)
            pSize.sort()
            pSize = [str(x) for x in pSize if pd.isnull(x) == False]
            print(pSize)
         
            self.cboPowsize.addItems(pSize)

            self.lib = pd.DataFrame(self.df, columns = ['재료','파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO', '시험온도', '시험전압', '시험전계', 'm', 'η', 'MTTF', 'B0.1', '변환온도', '변환전압\n(10V/um)', '온도가속\n(10V/um)', '전압가속\n(10V/um)', 'η\n(10V/um)', 'MTTF\n(10V/um)', 'B0.1\n(10V/um)'])
            self.lib["파우더 사이즈"] = [x if x != '사이즈 없음' else x for x in self.lib['파우더 사이즈']]
            show = self.lib.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
            # (['m', 'η', 'MTTF', 'B0.1', '변환온도', '변환전압\n(10V/um)', '온도가속\n(10V/um)', '전압가속\n(10V/um)', 'η\n(10V/um)', 'MTTF\n(10V/um)', 'B0.1\n(10V/um)'], axis=1)
            print(self.lib)
            self.make_tableLib(show)

    def make_tableLib(self, df):
        model = pandasModel(df)
        self.tableLib.setModel(model)
        self.tableLib.resizeColumnsToContents()
        self.tableLib.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableLib.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        print('make_tableLib 완료')

    def make_tableConst(self, df):
        self.tableConst.setHidden(False)
        model = pandasModel(df)
        self.tableConst.setModel(model)
        self.tableConst.resizeColumnsToContents()
        self.tableConst.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableConst.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        print('make_tableConst 완료')

    def filter_fir(self, txt):
        # Combo boxc 초기화
        self.cboPowder.clear()

        # 콤보박스로 원하는 파우더 사이즈 선택
        self.filtered = self.lib[self.lib["파우더 사이즈"] == int(txt)]
        print(self.filtered)
        print(txt)

        powder = list(set(self.filtered["파우더"]))
        print(powder)
        powder = [x for x in powder if pd.isnull(x) == False]
        powder.sort()
        print(powder)
        
        self.cboPowder.addItems(powder)
        
        filtered_show = self.filtered.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
        print(self.filtered)
        self.make_tableLib(filtered_show)

    def filter_sec(self, txt):
        # Combo boxc 초기화
        self.cboCompo.clear()

        # 콤보박스로 원하는 모재 파우더 선택
        self.filtered_sec = self.filtered[self.filtered["파우더"] == txt]
        print(self.filtered_sec)
        print(txt)

        compo = list(set(self.filtered_sec["조성"]))
        print(compo)
        compo = [x for x in compo if pd.isnull(x) == False]
        # compo = [ str(x) for x in compo ]
        compo.sort()
        print(compo)
        
        self.cboCompo.addItems(compo)
        filtered_show = self.filtered_sec.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
        self.make_tableLib(filtered_show)

    def filter_thr(self, txt):
        # Combo boxc 초기화
        self.cboSheetT.clear()

        # 콤보박스로 원하는 조성 선택
        self.filtered_thr = self.filtered_sec[self.filtered_sec["조성"] == txt ]
        print(self.filtered_thr)
        print(txt)

        sheetT = list(set(self.filtered_thr["Sheet T"]))
        sheetT = [float(x) for x in sheetT if pd.isnull(x) == False]
        sheetT.sort()
        sheetT = [str(x) for x in sheetT if pd.isnull(x) == False]
        print(sheetT)

        self.cboSheetT.addItems(sheetT)
        filtered_show = self.filtered_thr.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
        self.make_tableLib(filtered_show)

    def filter_four(self, txt):
        # Combo boxc 초기화
        self.cboLot.clear()
        
        # 콤보박스로 원하는 Sheet T 선택
        self.filtered_four = self.filtered_thr[self.filtered_thr["Sheet T"] == float(txt)]
        print(self.filtered_four)
        print(txt)

        lot = list(set(self.filtered_four["LOT NO"]))
        print(lot)
        lot = [x for x in lot if pd.isnull(x) == False]
        lot.sort()
        print(lot)

        self.cboLot.addItems(lot)
        filtered_show = self.filtered_four.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
        self.make_tableLib(filtered_show)

    def filter_last(self, txt):     
        # 출력 라벨 초기화
        self.chip_name.setHidden(False)
        self.material.setHidden(False)
        self.sheet_T.setHidden(False)
        self.lot_no.setHidden(False)   
    
        # 콤보박스로 원하는 Lot NO 선택
        self.filtered_last = self.filtered_four[self.filtered_four["LOT NO"] == txt ]
        print(self.filtered_last)
        print(txt)

        # 필터링된 기종 인덱스 따오기
        self.idx = self.filtered_last.index
        print(self.idx)

        # 선택한 SPL에 해당되는 측정조건 디스플레이
        self.chip_name.setText(self.filtered_last['기종'].iloc[0])
        print(self.filtered_last['기종'].iloc[0])
        self.material.setText(self.filtered_last['재료'].iloc[0])
        print(self.filtered_last['재료'].iloc[0])
        self.sheet_T.setNum(self.filtered_last['Sheet T'].iloc[0])
        print(self.filtered_last['Sheet T'].iloc[0])
        self.lot_no.setText(self.filtered_last['LOT NO'].iloc[0])
        print(self.filtered_thr['LOT NO'].iloc[0])

        # 시험온도, 시험전압 테이블 추출
        test_temp = list(set(self.filtered_last["시험온도"]))
        test_temp = [int(x) for x in test_temp if pd.isnull(x) == False]
        test_temp.sort()
        test_temp = [str(x) for x in test_temp if pd.isnull(x) == False]
        print(test_temp)
        test_volt = list(set(self.filtered_last["시험전압"]))
        test_volt = [float(x) for x in test_volt if pd.isnull(x) == False]
        test_volt.sort()
        test_volt = [str(x) for x in test_volt if pd.isnull(x) == False]
        print(test_volt)

        self.testcond = pd.DataFrame(columns = test_volt, index = test_temp)
        self.testcond = self.testcond.fillna('V')
        print(self.testcond)
        
        self.make_tableConst(self.testcond)

        # 인덱스 리셋
        self.filtered_last.reset_index(drop = True, inplace =True)
        filtered_show = self.filtered_last.drop(['재료', '파우더 사이즈', '파우더', '조성', 'Sheet T', '기종', 'LOT NO'], axis = 1)
        self.make_tableLib(filtered_show)
        print(self.filtered_last)

    def apply_lib(self):
        self.accels = pd.DataFrame(self.df.iloc[self.idx], columns = ['온도하한', '온도평균', '온도상한', '전압하한', '전압평균', '전압상한'])
        self.params = pd.DataFrame(self.df.iloc[self.idx], columns = ['유전체두께', '시험온도', '시험전압', '변환온도', 'm', 'η', '변환전압\n(10V/um)', '온도가속\n(10V/um)', '전압가속\n(10V/um)', 'η\n(10V/um)'])
        print(self.accels)
        print(self.params)
        
        
#         p = list(np.arange(0, 10.1, 0.1))
#         o = list(np.arange(0, 16.1, 0.1))
#         a = list(np.arange(0, 25.1, 0.1))
#         l = list(np.arange(0, 35.1, 0.1))
#         bce = list(np.arange(0, 40.1, 0.1))

#         self.test = pd.DataFrame()
        
#         # 전압 scale만큼 기존 칼럼 복사해서 추가 (빈 데이터프레임에다가 생성)
#         for i in range(len(self.filtered_thr["vol_lev"])):
#             if self.filtered_thr['vol_lev'][i] == 'S':
#                 df1 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
#                 self.test = pd.concat([self.test, df1], axis = 1)
#             elif self.filtered_thr['vol_lev'][i] == 'R':
#                 df2 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
#                 self.test = pd.concat([self.test, df2], axis = 1)
#             elif self.filtered_thr['vol_lev'][i] == 'Q':
#                 df3 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
#                 self.test = pd.concat([self.test, df3], axis = 1)
#             elif self.filtered_thr['vol_lev'][i] == 'P':
#                 df4 = pd.concat([self.filtered_thr.iloc[i]]*len(p), axis = 1)
#                 self.test = pd.concat([self.test, df4], axis = 1)
#             elif self.filtered_thr['vol_lev'][i] == 'O':
#                 df5 = pd.concat([self.filtered_thr.iloc[i]]*len(o), axis = 1)
#                 self.test = pd.concat([self.test, df5], axis = 1)
#             elif self.filtered_thr['vol_lev'][i] == 'A':
#                 df6 = pd.concat([self.filtered_thr.iloc[i]] * len(a), axis=1)
#                 self.test = pd.concat([self.test, df6], axis=1)
#             elif self.filtered_thr['vol_lev'][i] == 'L':
#                 df7 = pd.concat([self.filtered_thr.iloc[i]] * len(l), axis=1)
#                 self.test = pd.concat([self.test, df7], axis=1)
#             elif self.filtered_thr['vol_lev'][i] == 'B' or 'C' or 'E':
#                 df8 = pd.concat([self.filtered_thr.iloc[i]] * len(bce), axis=1)
#                 self.test = pd.concat([self.test, df8], axis=1)

#         self.fin = self.test.T.reset_index(drop = True)
        
#         # 전압 칼럼에 전압 정보 추가
#         for i in range(len(self.fin["vol_lev"])):

#             if self.fin['vol_lev'][i] == 'S' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(p)):
#                     self.fin['전압 (Vdc)'][i + j] = p[j]
#             elif self.fin['vol_lev'][i] == 'R' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(p)):
#                     self.fin['전압 (Vdc)'][i + j] = p[j]
#             elif self.fin['vol_lev'][i] == 'Q' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(p)):
#                     self.fin['전압 (Vdc)'][i + j] = p[j]
#             elif self.fin['vol_lev'][i] == 'P' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(p)):
#                     self.fin['전압 (Vdc)'][i + j] = p[j]
#             elif self.fin['vol_lev'][i] == 'O' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(o)):
#                     self.fin['전압 (Vdc)'][i + j] = o[j]
#             elif self.fin['vol_lev'][i] == 'A' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(a)):
#                     self.fin['전압 (Vdc)'][i + j] = a[j]
#             elif self.fin['vol_lev'][i] == 'L' and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(l)):
#                     self.fin['전압 (Vdc)'][i + j] = l[j]
#             elif (self.fin['vol_lev'][i] == 'B'or 'C'or'E') and self.fin['전압 (Vdc)'][i] == 0:
#                 for j in range(len(bce)):
#                     self.fin['전압 (Vdc)'][i + j] = bce[j]
#         '''
#         # sheet 두께 입력 받은 후 전계 칼럼 추가
#         self.st = self.STlineEdit.text()
#         ef = self.fin['전압 (Vdc)']/float(self.st)
#         for i in range(len(ef)):
#             ef[i] = np.round(ef[i], 2)
#         self.fin.insert(len(self.fin.columns), '전계 (V/um)', ef)



#         self.fin.drop(columns = ['vol_lev', 'DC-Bias 측정','DF','주파수(kHz)', 'AC(V)', '전압유지시간', 'Aging 시간'], inplace = True)

#         # 선택한 기종에 따른 상수값 테이블 추출
#         self.cst = pd.DataFrame(self.df.iloc[self.idx], columns = ['a', 'b', 'c', 'd', 'f'])
#         self.cst.columns = ['a (증가율)', 'b (변곡점)', 'c (점근선 1)', 'd (점근선 2)', 'f (검정력)']
#         self.const = [float(x) for x in self.cst.iloc[0].values]


#         # 로지스틱 모델링식을 이용하여 용량변화율 계산 및 해당 칼럼 추가
#         cap_pct = []
#         for i in range(len(self.fin['전계 (V/um)'])):
#             cap_pct.append( 10 ** (self.const[2] + (self.const[3] - self.const[2])/(1 + np.exp(-self.const[0] * (np.log( 1 + self.fin['전계 (V/um)'][i]) - self.const[1]))) ** self.const[4]) )

#         self.fin.insert(len(self.fin.columns), '용량변화율 %', cap_pct)


#         p_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10]
#         o_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16]
#         a_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25]
#         l_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25, 35]
#         bce_show = [0, 0.5, 1, 2, 3.15, 4, 5, 6.3, 8, 10, 16, 25, 35, 40]

        
#         # 필요용량 입력 값 이용하여 유효용량 계산 및 해당 칼럼 추가 (주파수 영역 구분)
#         cap = self.CaplineEdit.text()

#         if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
#             self.lblvdc.setHidden(True)
#             self.lblratio.setHidden(True)
#             self.lblvdc_name.setHidden(True)
#             self.lblratio_name.setHidden(True)
#             self.low = self.fin.copy()
#             low_cap = float(cap) * self.fin['용량변화율 %'] * 0.01
#             self.low.insert(len(self.low.columns), '저주파 유효 용량', low_cap)
#             self.low.drop(['sheet 두께'], axis=1, inplace=True)

#             self.low_show = self.low.copy()
#             self.low_show['용량변화율 %'] = np.round(self.low_show['용량변화율 %'], 2)
#             self.low_show['저주파 유효 용량'] = np.round(self.low_show['저주파 유효 용량'], 2)

#             # 보이는 테이블 전압 필터링
#             if self.low_show['전압 (Vdc)'].iloc[-1] == 10:
#                 self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(p_show)]
#             elif self.low_show['전압 (Vdc)'].iloc[-1] == 16:
#                 self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(o_show)]
#             elif self.low_show['전압 (Vdc)'].iloc[-1] == 25:
#                 self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(a_show)]
#             elif self.low_show['전압 (Vdc)'].iloc[-1] == 35:
#                 self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(l_show)]
#             elif self.low_show['전압 (Vdc)'].iloc[-1] == 40:
#                 self.low_show = self.low_show[self.low_show['전압 (Vdc)'].isin(bce_show)]

#             self.make_tableLib(self.low_show)


#         elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
#             self.high = self.fin.copy()
#             high_ratio = self.df['변화율'][self.idx].values[0]
#             high_vdc = self.df['0Vdc 용량'][self.idx].values[0]
#             self.lblvdc.setHidden(False)
#             self.lblratio.setHidden(False)
#             self.lblvdc_name.setHidden(False)
#             self.lblratio_name.setHidden(False)
#             self.lblratio.setText(str(np.round(high_ratio * 100, 2)))
#             self.lblvdc.setText(str(np.round(high_vdc, 2)))
#             high_cap = (high_ratio * self.fin['용량변화율 %']) * 0.01 * float(cap)
#             self.high.insert(len(self.high.columns), '고주파 유효 용량', high_cap, 2)
#             self.high.drop(['sheet 두께'], axis=1, inplace=True)

#             self.high_show = self.high.copy()
#             self.high_show['용량변화율 %'] = np.round(self.high_show['용량변화율 %'], 2)
#             self.high_show['고주파 유효 용량'] = np.round(self.high_show['고주파 유효 용량'], 2)

#             # 보이는 테이블 전압 필터링
#             if self.high_show['전압 (Vdc)'].iloc[-1] == 10:
#                 self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(p_show)]
#             elif self.high_show['전압 (Vdc)'].iloc[-1] == 16:
#                 self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(o_show)]
#             elif self.high_show['전압 (Vdc)'].iloc[-1] == 25:
#                 self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(a_show)]
#             elif self.high_show['전압 (Vdc)'].iloc[-1] == 35:
#                 self.high_show = self.high_show[self.high_show['전압 (Vdc)'].isin(l_show)]
#             elif self.high_show['전압 (Vdc)'].iloc[-1] == 40:
#                 self.highw_show = self.high_show[self.high_show['전압 (Vdc)'].isin(bce_show)]

#             self.make_tableLib(self.high_show)


#         self.make_tableConst(self.cst)
    
#     def draw_graph(self):

#         x = [float(a) for a in self.fin['전압 (Vdc)'].values]
#         y = self.fin['용량변화율 %'].values


#         xs = np.linspace(x[0], x[-1], 1000)
#         f = interpolate.interp1d(x, y, kind = 'linear')

#         ys = f(xs)

#         if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
#             xp = [float(a) for a in self.low_show['전압 (Vdc)'].values]
#             yp = self.low_show['용량변화율 %'].values
#         elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
#             xp = [float(a) for a in self.high_show['전압 (Vdc)'].values]
#             yp = self.high_show['용량변화율 %'].values

#         plt.scatter(xp,yp, color = 'red')
#         plt.plot(xs, ys)


#         plt.xlabel('전압 (V)')
#         plt.ylabel('용량변화율 %')

#         plt.grid(True)


#         plt.show()

#     def make_excel(self):
#         new_file = self.fileLineEdit.text()
#         if not new_file:
#             QMessageBox.warning(self, 'warning', '파일 이름을 입력해주세요.')
#         else:
#             newfile = 'P:.\\..\\{}.xlsx'.format(new_file)
#             # newfile = './{}.xlsx'.format(new_file)
#             writer = pd.ExcelWriter(newfile)
#             if self.filtered_thr['DC-Bias 측정'][0] == '저주파':
#                 self.low.to_excel(writer, index=False, engine = 'openpyxl')
#             elif self.filtered_thr['DC-Bias 측정'][0] == '고주파':
#                 self.high.to_excel(writer, index=False, engine = 'openpyxl')
#             writer.save()
#             QMessageBox.information(self, '저장완료', '성공적으로 저장되었습니다.')
#      '''

#     def my_exception_hook(exctype, value, traceback, self=None):
#         # Print the error and traceback
#         print(exctype, value, traceback)

#         # Call the normal Exception hook after
#         sys._excepthook(exctype, value, traceback)
#         QMessageBox.warning(self, '오류', '올바르지 않은 접근입니다.')
#         # sys.exit(1)

#     # Back up the reference to the exceptionhook
#     sys._excepthook = sys.excepthook

#     # Set the exception hook to our wrapping function
#     sys.excepthook = my_exception_hook

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Form()
    w.show()
    sys.exit(app.exec_())