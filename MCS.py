import sys
import os
import json
import threading
import time
import random
from datetime import datetime, timedelta
import websocket
import requests

from urllib.parse import quote
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFrame, QGridLayout,
    QGroupBox, QSizePolicy, QListWidget, QListWidgetItem,
    QDialog, QTabWidget, QCheckBox, QScrollArea, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QUrl, Signal, QObject, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QFont, QIcon, QTextCursor, QPixmap, QGuiApplication, QColor
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

APP_ICON_PATH = resource_path("app.ico")

OHT_DOWN_EQUIPMENTS = {
    "HNMOHV01-1", "HNMOHV01-2", "HNMOHV01-3", "HNMOHV01-4", "HNMOHV01-5",
    "HNMOHV02-1", "HNMOHV02-2", "HNMOHV02-3", "HNMOHV02-4", "HNMOHV02-5", "HNMOHV02-6", "HNMOHV02-7", "HNMOHV02-8", "HNMOHV02-9",
    "HNMOHV03-1", "HNMOHV03-2", "HNMOHV03-3", "HNMOHV03-4", "HNMOHV03-5",
    "HNMOHV04-1", "HNMOHV04-2", "HNMOHV04-3", "HNMOHV04-4", "HNMOHV04-5", "HNMOHV04-6", "HNMOHV04-7", "HNMOHV04-8",
    "HNMOHV05-1",
}

AGV_DOWN_EQUIPMENTS = {
    "HNMAGE01-1", "HNMAGE01-2", "HNMAGE01-3", "HNMAGE01-4", "HNMAGE01-5",
    "HNMAGE02-2", "HNMAGE02-3",
    "HNMAGE03-1", "HNMAGE03-2", "HNMAGE03-3", "HNMAGE03-4", "HNMAGE03-5",
    "HNMAGE05-1", "HNMAGE05-2", "HNMAGE05-3", "HNMAGE05-4", "HNMAGE05-5", "HNMAGE05-6",
    "HNMAGE06-1", "HNMAGE06-2",
    "HNMAGE07-1", "HNMAGE07-2", "HNMAGE07-3", "HNMAGE07-4", "HNMAGE07-5", "HNMAGE07-6", "HNMAGE07-7", "HNMAGE07-8",
    "HNMAGE08-1", "HNMAGE08-2",
    "D5PAGV01-1", "D5PAGV01-2",
}

STK_DOWN_EQUIPMENTS = {
    "D5PSTK010105", "D5PSTK010106", "D5PSTK020105", "D5PSTK020106", "D5PSTK030105", "D5PSTK030106", "D5PSTK040105", "D5PSTK040106", "D5PSTK050105", "D5PSTK060105", "D5PSTK060106", "D5PSTK070105", "D5PSTK070106", "D5PSTK080105", "D5PSTK080106",
    "HNMSTC010105", "HNMSTC010106", "HNMSTC020105", "HNMSTC020106", "HNMSTC030105", "HNMSTC030106", "HNMSTC040105", "HNMSTC040106", "HNMSTC050105", "HNMSTC050106", "HNMSTC060105", "HNMSTC060106", "HNMSTC070105", "HNMSTC070106", "HNMSTC080105", "HNMSTC080106", "HNMSTC090105", "HNMSTC090106", "HNMSTC100105", "HNMSTC100106", "HNMSTC110105", "HNMSTC110106",
    "HNASTC010105", "HNASTC010106", "HNASTC020105", "HNASTC020106", "HNASTC030105", "HNASTC030106", "HNASTC040105", "HNASTC040106", "HNASTC050105", "HNASTC050106", "HNASTC060105", "HNASTC060106",
}

PORT_DOWN_EQUIPMENTS = {
    "NMS01IO-A01", "NMS01IO-A02", "NMS01IO-O01", "NMS01IO-O02",
    "NMS02IO-A01", "NMS02IO-A02", "NMS02IO-A03", "NMS02IO-A04",
    "NMS02IO-O01", "NMS02IO-O02", "NMS02IO-O03", "NMS02IO-O04",
    "NMS03IO-A01", "NMS03IO-A02", "NMS03IO-O01", "NMS03IO-O02",
    "NMS04IO-O01", "NMS04IO-O02", "NMS04IO-O03", "NMS04IO-O04",
    "NMS05IO-A01", "NMS05IO-A02", "NMS05IO-O01", "NMS05IO-O02",
    "NMS06IO-A01", "NMS06IO-A02", "NMS06IO-A03", "NMS06IO-A04",
    "NMS06IO-O01", "NMS06IO-O02", "NMS06IO-O03", "NMS06IO-O04",
    "NMS07IO-A01", "NMS07IO-A02", "NMS07IO-O01", "NMS07IO-O02",
    "NMS08IO-O01", "NMS08IO-O02", "NMS08IO-O03", "NMS08IO-O04",
    "NMS09IO-A01", "NMS09IO-A02",
    "NMS10IO-A01", "NMS10IO-A02", "NMS10IO-A03", "NMS10IO-A04",
    "NMS11IO-A04", "NMS11IO-A05", "NMS11IO-O01", "NMS11IO-O02", "NMS11IO-O03", "NMS11IO-O04",
    "5PS02IO-C07", "5PS01IO-C02", "5PS01IO-C03", "5PS03IO-C01", "5PS03IO-C03", "5PS02IO-C04",
    "5PS02IO-C03", "5PS03IO-C05", "5PS04IO-C01", "5PS05IO-C01", "5PS01IO-C05", "5PS06IO-C06",
    "5PS05IO-C04", "5PS06IO-C01", "5PS03IO-C08", "5PS04IO-C02", "5PS05IO-C05", "5PS07IO-C01",
    "5PS07IO-C03", "5PS07IO-C04", "5PS08IO-C01", "5PS07IO-C06", "5PS04IO-C07", "5PS08IO-C03",
    "NMS08IO-C01", "NMS10IO-C01", "NAS02IO-C03", "NAS04IO-C03", "NAS06IO-C03",
}

BUFFER_UNKNOWN_EXCLUDE_unit = {
    "D5PBUF01-1", "D5PBUF03-1", "HNMBRM0101-1", "HNMBRM0201-1", "HNMBRM0501-1", "HNMBRM0601-1", "HNMBRM0701-1", "HNMBRM0901-1", "HNMBRM1101-1",
}

SPECIAL_WAIT_ONLY_OHT = {
    "HNMBRM0101-1",
    "HNMBRM0201-1",
    "HNMBRM0501-1",
    "HNMBRM0601-1",
    "HNMBRM0701-1",
    "HNMBRM0901-1",
    "HNMBRM1101-1",
}

BUFFER_DOWN_EQUIPMENTS = {
    "HNMBFF5101-1", "HNMBFF5101-2", "HNMBFF5101-3", "HNMBFF5101-4",
    "HNMBFF5102-1", "HNMBFF5102-2", "HNMBFF5102-3", "HNMBFF5102-4",
    "HNMBFF5103-1", "HNMBFF5103-2", "HNMBFF5103-3", "HNMBFF5103-4",
    "HNMBFF5104-1", "HNMBFF5104-2", "HNMBFF5104-3", "HNMBFF5104-4",
    "HNMBFF5110-1", "HNMBFF5110-2", "HNMBFF5110-3", "HNMBFF5110-4",
    "HNMBFF5111-1", "HNMBFF5111-2", "HNMBFF5111-3", "HNMBFF5111-4",
    "HNMBFF5105-1", "HNMBFF5105-2", "HNMBFF5105-3", "HNMBFF5105-4",
    "HNMBFF5106-1", "HNMBFF5106-2", "HNMBFF5106-3", "HNMBFF5106-4",
    "HNMBFF5107-1", "HNMBFF5107-2", "HNMBFF5107-3", "HNMBFF5107-4",
    "HNMBFF5108-1", "HNMBFF5108-2", "HNMBFF5108-3", "HNMBFF5108-4",
    "HNMBFF5113-1", "HNMBFF5113-2", "HNMBFF5113-3", "HNMBFF5113-4",
    "HNMBFF5112-1", "HNMBFF5112-2", "HNMBFF5112-3", "HNMBFF5112-4",
    "HNMBFF5109-1", "HNMBFF5109-2", "HNMBFF5109-3", "HNMBFF5109-4",
    "HNMBFF510A-1", "HNMBFF510A-2", "HNMBFF510A-3", "HNMBFF510A-4",
    "HNMBFF510B-1", "HNMBFF510B-2", "HNMBFF510B-3", "HNMBFF510B-4",
    "HNMBFF510C-1", "HNMBFF510C-2", "HNMBFF510C-3", "HNMBFF510C-4",
    "HNMBFF5114-1", "HNMBFF5114-2", "HNMBFF5114-3", "HNMBFF5114-4",
    "HNMBFF5115-1", "HNMBFF5115-2", "HNMBFF5115-3", "HNMBFF5115-4",
    "HNMBFF510D-1", "HNMBFF510D-2", "HNMBFF510D-3", "HNMBFF510D-4",
    "HNMBFF510E-1", "HNMBFF510E-2", "HNMBFF510E-3", "HNMBFF510E-4",
    "HNMBFF510F-1", "HNMBFF510F-2", "HNMBFF510F-3", "HNMBFF510F-4",
    "HNMBFF510G-1", "HNMBFF510G-2", "HNMBFF510G-3", "HNMBFF510G-4",
    "D5PBUF01-1", "D5PBUF03-1", "HNMBRM0101-1", "HNMBRM0201-1", "HNMBRM0501-1", "HNMBRM0601-1", "HNMBRM0701-1", "HNMBRM0901-1", "HNMBRM1101-1",
}

OHT_STATUS_EQUIPMENTS = {
    "HNMOHV01", "HNMOHV02", "HNMOHV03", "HNMOHV04", "HNMOHV05",
}

AGV_STATUS_EQUIPMENTS = {
    "HNMAGE01", "HNMAGE02", "HNMAGE03", "HNMAGE05", "HNMAGE06", "HNMAGE07", "HNMAGE08", "D5PAGV01",
}

STK_STATUS_EQUIPMENTS = {
    "D5PSTK01", "D5PSTK02", "D5PSTK03", "D5PSTK04", "D5PSTK05", "D5PSTK06", "D5PSTK07", "D5PSTK08",
    "HNMSTC01", "HNMSTC02", "HNMSTC03", "HNMSTC04", "HNMSTC05", "HNMSTC06", "HNMSTC07", "HNMSTC08", "HNMSTC09", "HNMSTC10", "HNMSTC11",
    "HNASTC01", "HNASTC02", "HNASTC03", "HNASTC04", "HNASTC05", "HNASTC06",
}

PORT_DELAY_EQUIPMENTS = {
    "NMS01IO-A02", "NMS01IO-O02",
    "NMS02IO-A04", "NMS02IO-O02", "NMS02IO-A01", "NMS02IO-O04",
    "NMS03IO-A01", "NMS03IO-O02",
    "NMS04IO-O02", "NMS04IO-O04",
    "NMS05IO-A01", "NMS05IO-O02",
    "NMS06IO-A03", "NMS06IO-A04", "NMS06IO-O01", "NMS06IO-O02",
    "NMS07IO-A02", "NMS07IO-O01",
    "NMS08IO-O02", "NMS08IO-O04",
    "NMS09IO-A01",
    "NMS10IO-A02", "NMS10IO-A03",
    "NMS11IO-A05", "NMS11IO-O03", "NMS11IO-O04",
}

OHT_ALARM_NAMES = {
    '9903': 'Loading Fail',
    '9904': 'Unloading Fail',
    '10001': 'ERR_EMO_SWITCH',
    '10003': 'ERR_BUMPER_PRESS',
    '10006': 'ERR_TP_CONNTECTED',
    '10100': 'ERR_NOT_EtherCAT_OP',
    '10101': 'ERR_NOT_INITIAL',
    '10203': 'ERR_TAG_NOT_FIND',
    '10901': 'ERR_EtherCAT_HOIST_TOQUE',
    '14100': 'ERR_AXIS1_Amp_OFF',
    '14101': 'ERR_AXIS2_Amp_OFF',
    '14102': 'ERR_AXIS3_Amp_OFF',
    '15000': 'ERR_POS_DRIVE_TARGET',
    '16004': 'ERR_CHECK_HOIST_UP',
    '16005': 'ERR_CHECK_HOIST_SWING',
    '16010': 'ERR_CHECK_ANTIDROP_UNLOCK',
    '16013': 'ERR_CHECK_GRIPPER_UNKNOWN',
    '16014': 'ERR_CHECK_GRIPPER_ALARM',
    '16015': 'ERR_CHECK_STEER_DIRECTION',
    '16101': 'ERR_CHECK_MATERIAL_EXIST',
    '16102': 'ERR_CHECK_MATERIAL_EMPTY',
    '16106': 'ERR_CHECK_DETECT_FLANGE',
    '17000': 'ERR_PIO_READY_ON',
    '17003': 'ERR_PIO_ES_ON',
    '18105': 'ERR_TMOUT_STEER_LEFT',
    '18106': 'ERR_TMOUT_STEER_RIGHT',
    '18501': 'ERR_TMOUT_FNODE_DECTAG',
    '18502': 'ERR_TMOUT_FNODE_STOPTAG',
    '18902': 'ERR_TMOUT_PIO_TA3',
    '19001': 'ERROR_ESTOP_BARCODE_NOT_DETACT',
    '19002': 'ERROR_ESTOP_CLICK_UI',
    '19003': 'ERROR_ESTOP_CLICK_OCS',
    '19004': 'ERROR_ESTOP_NOT_DETACT_TAG_IN_PATH',
    '19062': 'ERROR_ESTOP_TIMEOUT_GOMORE_COMMAND',
    '19102': 'ERROR_ESTOP_DONOT_GO_BECAUSE_PAUSE',
    '20280': 'ERR_PCICMD_INVALID_AL_STATE',
    '21054': 'ERR_STOP_BY_ALM',
    '21055': 'ERR_STOP_BY_COMM_ERROR',
    '30002': 'ERR_AXIS1_AL_010_2',
    '30117': 'ERR_AXIS1_AL_050_5',
    '30120': 'ERR_AXIS1_AL_051_2',
    '31058': 'ERR_AXIS2_AL_021_1',
    '31060': 'ERR_AXIS2_AL_021_3',
    '32002': 'ERR_AXIS3_AL_010_2',
    '32122': 'ERR_AXIS3_AL_052_3',
}

AGV_ALARM_NAMES = {
    '0': 'Không xác định',
    '10102': 'NAV350 Error',
    '10103': 'TIM320 Error',
    '10107': 'Error of Front Motor',
    '10108': 'Error of Rear Motor',
    '10115': 'Poor Communication with Motor',
    '10123': 'PC Not Send Bit Complete',
    '10210': 'EMS Button Pressed',
    '10209': 'Dont Have Acquire (Have a Tray in AGV)',
    '10301': 'Error Stopper Right',
    '140':   'Error Roller Right',
    '10317': 'TimeOut Conveyor',
    '10319': 'Sensor Check Tray Right Error',
    '10402': '(EQP PIO TA3) READY OFF Timeout',
    '158':   '(EQP PIO TA1) LR or UR ENB ON Timeout',
    '162':   'LC Signal ON When Transfering',
    '204':   'AGV Manual Mode',
    '10111': 'Steering Motor Does Not Change Steering Direction',
    '10112': 'Move Base Spin Failed',
    '10113': 'Disconnect AGVC',
    '10114': 'Poor Communication with Battery',
    '10117': 'Deviation of Driving Path(50mm)',
    '10118': 'Cant Receive Any Node',
    '10119': 'Cim Sent The Wrong Type',
    '10120': 'Unable to Plan Route',
    '10202': 'Timeout PBS Sensor',
    '10203': 'Bumper Collision',
    '10204': 'Right Side Lightcurtain Detect',
    '10205': 'Left Side Lightcurtain Detect',
    '10208': 'Not Have Tray, Not Going to Deposit',
    '10211': 'AGV Cover or Door Opening',
    '236':   'Error Stopper Right',
    '10302': 'Error Stopper Left',
    '10304': 'Error Roller Left',
    '10305': 'Error Roller Right',
    '10306': 'Error Pushbar Front',
    '10307': 'Error Pushbar Back',
    '10313': 'Diff To Dock Failed',
    '10314': 'Crab To Dock Failed',
    '10318': 'Sensor Check Tray Left error',
    '10403': '(EQP PIO TA1) LR or UR ENB ON Timeout',
    '10407': '(EQP PIO) LC Signal ON When Transfering',
    '10501': 'Bad Battery Charging',
    '201':   'AGV_STATUS_TIMEOUT',
    '202':   'AGV_MAP_VER_DIF',
    '203':   'UNABLE_TURN_NODE',
    '10324': 'UNKNOWN ALARM 10324',
    '1110324': 'UNKNOWN ALARM 10324',
    '10332': 'UNKNOWN ALARM 10332',
    '10327': 'UNKNOWN ALARM 10327',
}

STK_ALARM_GROUP1_EQUIPMENTS = {
    "D5PSTK010105", "D5PSTK010106", "D5PSTK020105", "D5PSTK020106",
    "D5PSTK030105", "D5PSTK030106", "D5PSTK040105", "D5PSTK040106",
    "D5PSTK050105", "D5PSTK060105", "D5PSTK060106",  
    "HNMSTC010105", "HNMSTC010106", "HNMSTC020105", "HNMSTC020106",
    "HNMSTC030105", "HNMSTC030106", "HNMSTC040105", "HNMSTC040106",
    "HNMSTC050105", "HNMSTC050106", "HNMSTC060105", "HNMSTC060106",
    "HNMSTC070105", "HNMSTC070106", "HNMSTC080105", "HNMSTC080106",
    "HNMSTC090105", "HNMSTC090106",
    "HNASTC010105", "HNASTC010106", "HNASTC020105", "HNASTC020106",
    "HNASTC030105", "HNASTC030106", "HNASTC040105", "HNASTC040106", "HNASTC050105", "HNASTC050106",
}

STK_ALARM_GROUP2_EQUIPMENTS = {
    "D5PSTK070105", "D5PSTK070106", "D5PSTK080105", "D5PSTK080106",
    "HNMSTC100105", "HNMSTC100106", "HNMSTC110105", "HNMSTC110106",
    "HNASTC060105", "HNASTC060106",
}

STK_ALARM_NAMES_GROUP1 = {
    '1': 'Empty Event [Warning Error]',
    '1001': 'Empty Event [Warning Error]',
    '6': 'HP Side TP E-Stop Error [Power Off]',
    '10': 'HP Side Laser Sensor Detect(Manual) [Power Off]',
    '11': 'OP Side Laser Sensor Detect(Manual) [Power Off]',
    '47': 'Sefty PLC Power On Enable Off Error [Power Off]',
    '82': 'X Axis POT Error(Servo) [Normal]',
    '91': 'T Axis NOT Error(Servo) [Normal]',
    '107': 'A Axis Over Load Error(Servo) [Normal]',
    '128': ' X Axis Servo Pack Error [Normal]',
    '131': 'A Axis Servo Pack Error [Normal]',
    '136': 'A Axis Absolute Origin Loss [Normal]',
    '148': 'A Axis Auto Positon Fail [Normal]',
    '154': 'Tray Position Fail Error [Normal]',
    '156': 'Tray Type Miss Match Error [Normal]',
    '158': 'Z Axis Unblance Sensor Detect [Normal]',
    '165': 'CMD ID Wrong Error [Normal]',
    '167': 'Left HP Double Sensor Error [Normal]',
    '170': 'Right OP Double Sensor Error [Normal]',
    '173': 'Inplace#1 Sensor Detect [Normal]',
    '174': 'Inplace#2 Sensor Detect [Normal]',
    '176': 'Inplace#1 Sensor Not Detect [Normal]',
    '177': 'Inplace#2 Sensor Not Detect [Normal]',
    '178': 'Tray Detect Sensor Not Detect [Normal]',
    '180': 'T-Axis Dest Position Error (Sensor)',
    '182': 'OP Key Stop Error [Normal]',
    '185': 'X Axis Dest Position Sensor Error [Normal]',
    '186': 'Z Axis Dest Position Sensor Error [Normal]',
    '188': 'G Axis Dest Position Sensor Error [Normal]',
    '189': 'T Axis Dest Position Sensor Error [Normal]',
    '190': 'TP Connection Error [Normal]',
    '197': 'OP High Chain Cut Error [Normal]',
    '203': 'Collision Sensor Setting Error [Normal]',
    '204': 'HP Side Laser Sensor Warning Detect(Manual) [Normal]',
    '205': 'OP Side Laser Sensor Warning Detect(Manual) [Normal]',
    '213': 'HP Side Laser Sensor Warning Detect(Auto) [Normal]',
    '420': 'OP Out Of Service Belt Sensor Detect [Normal]',
    '422': 'HP Out Of Service Bumper Stopper Down Fail [Normal]',
    '423': 'OP Out Of Service Bumper Stopper Down Fail [Normal]',
    '435': 'Master  Communication Error [Slow Stop]',
    '437': 'HP Touch Select Manual [Slow Stop]',
    '438': 'OP Touch Select Manual [Slow Stop]',
    '441': 'CIM Stop [Slow Stop]',
    '446': 'OP Side Door Open [Slow Stop]',
    '447': 'Other RM Communication Error [Slow Stop]',
    '448': 'Light Curtain Detect Error [Slow Stop]',
    '450': 'CIM Logical Stop [Slow Stop]',
    '451': 'Other RM Out Of Service Cancel [Slow Stop]',
    '497': 'Empty Event [Warning Error]',
    '498': 'Double Event [Warning Error]',
    '499': 'From EQP I_F Error Event [Warning Error]',
    '500': 'To EQP I_F Error  Event [Warning Error]',
    '1007': 'OP Side TP E-Stop Error [Power Off]',
    '1010': 'HP Side Laser Sensor Detect(Manual) [Power Off]',
    '1011': 'OP Side Laser Sensor Detect(Manual) [Power Off]',
    '1012': 'Ankle Detect  [Power Off]',
    '1047': 'Sefty PLC Power On Enable Off Error [Power Off]',
    '1066': 'Z1-Z2 Deviation Error [Quick Stop]',
    '1084': 'Z Axis POT Error(Servo) [Normal]',
    '1085': 'Z Axis NOT Error(Servo) [Normal]',
    '1086': 'A Axis POT Error(Servo) [Normal]',
    '1087': 'A Axis NOT Error(Servo) [Normal]',
    '1090': 'T Axis POT Error(Servo) [Normal]',
    '1091': 'T Axis NOT Error(Servo) [Normal]',
    '1101': 'G Axis Soft Limit - Error(Servo) [Normal]',
    '1128': 'X Axis Servo Pack Error [Normal]',
    '1131': 'A Axis Servo Pack Error [Normal]',
    '1135': 'Z Axis Absolute Origin Loss [Normal]',
    '1136': 'A Axis Absolute Origin Loss [Normal]',
    '1148': 'A Axis Auto Positon Fail [Normal]',
    '1154': 'Tray Position Fail Error [Normal]',
    '1156': 'Tray Type Miss Match Error [Normal]',
    '1158': 'Z Axis Unblance Sensor Detect [Normal]',
    '1165': 'CMD ID Wrong Error [Normal]',
    '1167': 'Left HP Double Sensor Error [Normal]',
    '1168': 'Left OP Double Sensor Error [Normal]',
    '1169': 'Right HP Double Sensor Error [Normal]',
    '1170': 'Right OP Double Sensor Error [Normal]',
    '1172': 'G Axis No Ready Move A Axis [Normal]',
    '1173': 'Inplace#1 Sensor Detect [Normal]',
    '1174': 'Inplace#2 Sensor Detect [Normal]',
    '1176': 'Inplace#1 Sensor Not Detect [Normal]',
    '1177': 'Inplace#2 Sensor Not Detect [Normal]',
    '1178': 'Tray Detect Sensor Not Detect [Normal]',
    '1185': 'X Axis Dest Position Sensor Error [Normal]',
    '1186': 'Z Axis Dest Position Sensor Error [Normal]',
    '1203': 'Collision Sensor Setting Error [Normal]',
    '1205': 'OP Side Laser Sensor Warning Detect(Manual) [Normal]',
    '1213': 'HP Side Laser Sensor Warning Detect(Auto) [Normal]',
    '1323': 'Master Communication Error [Slow Stop]',
    '1393': 'Infterface Port E Stop [Power Off]',
    '1420': 'OP Out Of Service Belt Sensor Detect [Normal]',
    '1422': 'HP Out Of Service Bumper Stopper Down Fail [Normal]',
    '1423': 'OP Out Of Service Bumper Stopper Down Fail [Normal]',
    '1435': 'Master  Communication Error [Slow Stop]',
    '1437': 'HP Touch Select Manual [Slow Stop]',
    '1438': 'OP Touch Select Manual [Slow Stop]',
    '1441': 'CIM Stop [Slow Stop]',
    '1442': 'Main Touch Stop [Slow Stop]',
    '1445': 'HP Side Door Open [Slow Stop]',
    '1448': 'Light Curtain Detect Error [Slow Stop]',
    '1450': 'CIM Logical Stop [Slow Stop]',
    '1451': 'Other RM Out Of Service Cancel [Slow Stop]',
    '1497': 'Empty Event [Warning Error]',
    '1498': 'Double Event [Warning Error]',
    '1499': 'From EQP I_F Error Event [Warning Error]',
    '1500': 'To EQP I_F Error  Event [Warning Error]',
}

STK_ALARM_NAMES_GROUP2 = {
    '12': 'HP Side Laser Sensor Detect',
    '15': 'HP Bumper Detect',
    '21': 'X-Axis Deviation Error(PID)',
    '28': 'Real X-Axis No Command Move',
    '29': 'X-Axis Virtual Speed & Next Scan Time Error',
    '38': 'Safety PLC Power On Enable Off Error',
    '82': 'X11-Axis Servo Pack Error',
    '84': 'X21-Axis Servo Pack Error',
    '86': 'Z11-Axis Servo Pack Error',
    '88': 'Z21-Axis Servo Pack Error',
    '90': 'A11-Axis Servo Pack Error',
    '92': 'T11-Axis Servo Pack Error',
    '93': 'G11-Axis Servo Pack Error',
    '99': 'Cross Trasfer Move Command Error',
    '177': 'X-Axis Dest Position Error(Sensor)',
    '178': 'Z-Axis Dest Position Error(Sensor)',
    '211': 'Teaching Range Error',
    '215': 'CST Type Miss Match Error(Dest)',
    '217': 'CST Position Fail Error',
    '218': 'Inplace#1 Sensor Detect',
    '219': 'Inplace#2 Sensor Detect',
    '220': 'CST Detect Sensor Detect',
    '221': 'Inplace#1 Sensor Not Detect',
    '222': 'Inplace#2 Sensor Not Detect',
    '249': 'A Axis Auto Positon Fail',
    '250': 'Type Sensor#1 Detect',
    '251': 'Type Sensor#2 Detect',
    '252': 'Type Sensor#3 Detect',
    '281': 'Master Auto Stop Error',
    '337': 'Empty Event',
    '338': 'Double Event',
    '339': 'From Port I/F Error Event',
    '340': 'To Port I/F Error  Event',
    '341': 'From ObStrution Event',
    '342': 'To ObStrution Event',
    '343': 'From EQP I/F Error Event',
    '344': 'To EQP I/F Error  Event',
    '436': 'HP Out Of Service Belt Sensor Detect',
    '479': 'Light Curtain Detect Error',
    '481': 'CIM Logical Stop',
    '499': 'Obstrution Event',
    '1014': 'Ankle Detect',
    '1028': 'Real X-Axis No Command Move',
    '1029': 'X-Axis Virtual Speed & Next Scan Time Error',
    '1038': 'Safety PLC Power On Enable Off Error',
    '1082': 'X11-Axis Servo Pack Error',
    '1084': 'X21-Axis Servo Pack Error',
    '1086': 'Z11-Axis Servo Pack Error',
    '1088': 'Z21-Axis Servo Pack Error',
    '1090': 'A11-Axis Servo Pack Error',
    '1092': 'T11-Axis Servo Pack Error',
    '1093': 'G11-Axis Servo Pack Error',
    '1099': 'Cross Trasfer Move Command Error',
    '1171': 'X-Axis Dest Position Error(Sensor)',
    '1178': 'Z-Axis Dest Position Error(Sensor)',
    '1180': 'T-Axis Dest Position Error(Sensor)',
    '1215': 'CST Type Miss Match Error(Dest)',
    '1217': 'CST Position Fail Error',
    '1218': 'Inplace#1 Sensor Detect',
    '1219': 'Inplace#2 Sensor Detect',
    '1220': 'CST Detect Sensor Detect',
    '1221': 'Inplace#1 Sensor Not Detect',
    '1222': 'Inplace#2 Sensor Not Detect',
    '1223': 'CST Detect Sensor Not Detect',
    '1249': 'A Axis Auto Positon Fail',
    '1250': 'Type Sensor#1 Detect',
    '1251': 'Type Sensor#2 Detect',
    '1252': 'Type Sensor#3 Detect',
    '1254': 'Type Sensor Not Detect',
    '1281': 'Master Auto Stop Error',
    '1337': 'Empty Event',
    '1338': 'Double Event',
    '1339': 'From Port I/F Error Event',
    '1340': 'To Port I/F Error  Event',
    '1341': 'From ObStrution Event',
    '1342': 'To ObStrution Event',
    '1343': 'From EQP I/F Error Event',
    '1344': 'To EQP I/F Error  Event',
    '1479': 'Light Curtain Detect Error',
    '1481': 'CIM Logical Stop',
    '1499': 'Obstrution Event',
}

BUFFER_UNKNOWN_EQUIPMENTS = BUFFER_DOWN_EQUIPMENTS

OMS_HUB_PATH = "/oms" 

OMS_SITES = [
    {
        "name": "HNMOHV01",
        "base_url": "http://10.121.52.69",
        "unit": ["HNMOHV01-1", "HNMOHV01-2", "HNMOHV01-3", "HNMOHV01-4", "HNMOHV01-5"],
    },
    {
        "name": "HNMOHV02",
        "base_url": "http://10.121.51.252",
        "unit": [
            "HNMOHV02-1", "HNMOHV02-2", "HNMOHV02-3", "HNMOHV02-4", "HNMOHV02-5",
            "HNMOHV02-6", "HNMOHV02-7", "HNMOHV02-8", "HNMOHV02-9",
        ],
    },
    {
        "name": "HNMOHV03",
        "base_url": "http://10.121.2.175",
        "unit": ["HNMOHV03-1", "HNMOHV03-2", "HNMOHV03-3", "HNMOHV03-4", "HNMOHV03-5"],
    },
    {
        "name": "HNMOHV04",
        "base_url": "http://10.121.52.70",
        "unit": [
            "HNMOHV04-1", "HNMOHV04-2", "HNMOHV04-3", "HNMOHV04-4",
            "HNMOHV04-5", "HNMOHV04-6", "HNMOHV04-7", "HNMOHV04-8",
        ],
    },
    {
        "name": "HNMOHV05",
        "base_url": "http://10.121.56.123",
        "unit": ["HNMOHV05-1"],
    },
]


def map_oms_id_to_unit_id(site_name: str, vc_id: int) -> str | None:
    for site in OMS_SITES:
        if site["name"] == site_name:
            unit = site["unit"]
            idx = vc_id - 1 
            if 0 <= idx < len(unit):
                return unit[idx]
            return None
    return None

class WebSocketWorker(QObject):
    message_received = Signal(dict)
    status_changed = Signal(bool, str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self._stop_event = threading.Event()
        self._attempt = 0
        self.ws = None

    def start(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        self._stop_event.set()
        try:
            if self.ws is not None:
                self.ws.close()
        except Exception:
            pass

    def _on_message(self, ws, message: str):
        try:
            data = json.loads(message)
        except Exception:
            return
        self.message_received.emit(data)

    def _on_open(self, ws):
        self.status_changed.emit(True, "🟢 ĐÃ KẾT NỐI")

    def _on_close(self, ws, close_status_code, close_msg):
        self.status_changed.emit(False, "🔴 MẤT KẾT NỐI")

    def _on_error(self, ws, error):
        self.status_changed.emit(False, f"🔴 LỖI KẾT NỐI: {error}")

    def _run(self):
        self._attempt = 0
        while not self._stop_event.is_set():
            if self._attempt == 0:
                self.status_changed.emit(False, "🟡 ĐANG KẾT NỐI")
            else:
                self.status_changed.emit(False, "🟡 ĐANG KẾT NỐI LẠI")

            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_close=self._on_close,
                    on_error=self._on_error,
                )
                self.ws.run_forever()
            except Exception as e:
                self.status_changed.emit(False, f"🔴 LỖI KẾT NỐI: {e}")
            finally:
                self.ws = None
            if self._stop_event.is_set():
                break
            self._attempt += 1

            if not self._stop_event.is_set():
                time.sleep(3)

class OmsSiteWorker(QObject):
    rvc_received = Signal(str, list)

    def __init__(self, site_config: dict):
        super().__init__()
        self.site = site_config
        self._stop_event = threading.Event()
        self.thread = None
        self.ws = None
        self.handshake_done = False

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        try:
            if self.ws is not None:
                self.ws.close()
        except Exception:
            pass

    def _run(self):
        site_name = self.site["name"]
        base_url = self.site["base_url"]
        home_url = base_url + self.site["home_path"]

        try:
            session, conn_token, cookie_str, has_ws, has_sse = self._build_signalr_connection(base_url, home_url)
        except Exception as e:
            print(f"[OMS {site_name}] LỖI build connection: {e}")
            return

        headers = {
            "Origin": base_url,
            "User-Agent": "PythonWebSocketClient/1.0",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        if cookie_str:
            headers["Cookie"] = cookie_str

        self.handshake_done = False

        host_part = base_url.replace("http://", "").replace("https://", "")
        if has_ws:
            ws_url = f"ws://{host_part}{OMS_HUB_PATH}?id={quote(conn_token)}"
            header_list = [f"{k}: {v}" for k, v in headers.items()]

            ws = websocket.WebSocketApp(
                ws_url,
                header=header_list,
                on_open=self._on_ws_open,
                on_message=self._on_ws_message,
                on_error=self._on_ws_error,
                on_close=self._on_ws_close,
            )
            self.ws = ws
            try:
                ws.run_forever()
            finally:
                self.ws = None
            return

        if has_sse:
            sse_url = f"{base_url}{OMS_HUB_PATH}?id={quote(conn_token)}"
            self._run_sse(session, sse_url, headers, site_name)
            return

        print(f"[OMS {site_name}] KHÔNG hỗ trợ WebSockets hoặc ServerSentEvents trong availableTransports.")

    def _build_signalr_connection(self, base_url: str, home_url: str):
        session = requests.Session()

        r_home = session.get(home_url, timeout=5)
        r_home.raise_for_status()

        negotiate_url_1 = base_url + OMS_HUB_PATH + "/negotiate?negotiateVersion=1"
        negotiate_url_2 = base_url + OMS_HUB_PATH + "/negotiate"

        r_neg = session.post(negotiate_url_1, timeout=5)
        if r_neg.status_code == 404:
            r_neg = session.post(negotiate_url_2, timeout=5)
        r_neg.raise_for_status()
        data = r_neg.json()

        conn_token = data.get("connectionToken") or data.get("connectionId")
        if not conn_token:
            raise RuntimeError(f"Không thấy connectionToken/Id trong negotiate: {data}")

        transports = data.get("availableTransports") or []
        has_websocket = any(
            (t.get("transport") or "").lower() == "websockets"
            for t in transports if isinstance(t, dict)
        )
        has_sse = any(
            (t.get("transport") or "").lower() == "serversentevents"
            for t in transports if isinstance(t, dict)
        )

        cookies = session.cookies.get_dict()
        cookie_list = [f"{k}={v}" for k, v in cookies.items()]
        cookie_str = "; ".join(cookie_list) if cookie_list else ""

        return session, conn_token, cookie_str, has_websocket, has_sse

    def _on_ws_open(self, ws):

        handshake = '{"protocol":"json","version":1}\x1e'
        try:
            ws.send(handshake)
        except Exception as e:
            print(f"[OMS {self.site['name']}] HANDSHAKE ERROR: {e}")

    def _on_ws_message(self, ws, message: str):
        frames = message.split("\x1e")
        for frame in frames:
            frame = frame.strip()
            if not frame:
                continue

            self._handle_signalr_frame(frame, ws)        

    def _on_ws_error(self, ws, error):
        print(f"[OMS {self.site['name']}] ERROR: {error}")

    def _on_ws_close(self, ws, code, reason):
        print(f"[OMS {self.site['name']}] CLOSE: code={code}, reason={reason}")

    def _send_invocation(self, ws, target: str, arguments: list):
        msg_obj = {
            "type": 1,
            "target": target,
            "arguments": arguments or [],
        }
        frame = json.dumps(msg_obj, ensure_ascii=False) + "\x1e"
        try:
            ws.send(frame)
        except Exception as e:
            print(f"[OMS {self.site['name']}] INVOKE ERROR {target}: {e}")

    def _run_sse(self, session: requests.Session, sse_url: str, headers: dict, site_name: str):
        print(f"[OMS {site_name}] DÙNG SSE (EventStream) tại {sse_url}")

        try:
            hs_headers = headers.copy()
            hs_headers.update({
                "Content-Type": "text/plain;charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
            })

            handshake_payload = json.dumps({"protocol": "json", "version": 1}) + "\x1e"

            resp_hs = session.post(
                sse_url,
                headers=hs_headers,
                data=handshake_payload,
                timeout=5,
            )
            resp_hs.raise_for_status()
            print(f"[OMS {site_name}] SSE HANDSHAKE OK, status={resp_hs.status_code}")
        except Exception as e:
            print(f"[OMS {site_name}] SSE HANDSHAKE ERROR: {e}")
            return

        try:
            inv_headers = headers.copy()
            inv_headers.update({
                "Content-Type": "text/plain;charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "*/*",
            })
            invoke_obj = {
                "type": 1,
                "target": "JoinRealtimeGroup",
                "arguments": [],
            }
            invoke_payload = json.dumps(invoke_obj, ensure_ascii=False) + "\x1e"

            resp_inv = session.post(
                sse_url,
                headers=inv_headers,
                data=invoke_payload,
                timeout=5,
            )
            resp_inv.raise_for_status()
            print(f"[OMS {site_name}] SSE INVOKE JoinRealtimeGroup OK, status={resp_inv.status_code}")
        except Exception as e:
            print(f"[OMS {site_name}] SSE INVOKE ERROR JoinRealtimeGroup: {e}")
            pass

        try:
            ev_headers = headers.copy()
            ev_headers.update({
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            })

            with session.get(sse_url, headers=ev_headers, stream=True, timeout=None) as resp:
                resp.raise_for_status()
                print(f"[OMS {site_name}] SSE STREAM OPENED, status={resp.status_code}")

                current_data_lines: list[str] = []

                for raw_line in resp.iter_lines(decode_unicode=True):
                    if self._stop_event.is_set():
                        break
                    if raw_line is None:
                        continue

                    line = raw_line.rstrip("\r")

                    if line == "":
                        if not current_data_lines:
                            continue

                        data_block = "\n".join(current_data_lines)
                        current_data_lines.clear()

                        parts = data_block.split("\x1e")
                        for frame in parts:
                            frame = frame.strip()
                            if not frame:
                                continue
                            self._handle_signalr_frame(frame)
                        continue

                    if line.startswith("data:"):
                        current_data_lines.append(line[5:].lstrip())
                    else:
                        continue

        except Exception as e:
            print(f"[OMS {site_name}] SSE ERROR: {e}")

    def _handle_signalr_frame(self, frame: str, ws=None):
        site_name = self.site["name"]

        if not self.handshake_done:
            self.handshake_done = True
            if ws is not None:
                try:
                    self._send_invocation(ws, "JoinRealtimeGroup", [])
                except Exception as e:
                    print(f"[OMS {site_name}] INVOKE ERROR JoinRealtimeGroup: {e}")

        try:
            obj = json.loads(frame)
        except Exception:
            return

        if isinstance(obj, dict) and obj.get("target") == "R_VC":
            args = obj.get("arguments") or []
            if args and isinstance(args[0], str):
                raw = args[0]
                try:
                    rvc_list = json.loads(raw)
                    self.rvc_received.emit(site_name, rvc_list)
                except Exception:
                    pass

class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class StatisticsWidget(QWidget):
    error_card_clicked = Signal()
    stk_near_full_card_clicked = Signal()
    lost_tray_card_clicked = Signal()

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.total_widget = self._create_stat_card("📊 TỔNG THIẾT BỊ FA", "0", "Đang giám sát 0 thiết bị", "#3498db")
        self.error_widget = self._create_stat_card("🚨 THIẾT BỊ ĐANG LỖI", "0", "Đang hoạt động tốt", "#e74c3c")
        self.near_full_widget = self._create_stat_card("📈 STOCKER GẦN ĐẦY", "0", "Dung lượng an toàn", "#f39c12")
        self.lost_info_widget = self._create_stat_card("📡 TRAY MẤT LỆNH DI CHUYỂN", "0", "Kết nối ổn định", "#95a5a6")

        stat_cards = [
            self.total_widget,
            self.error_widget,
            self.near_full_widget,
            self.lost_info_widget,
        ]

        for i, card in enumerate(stat_cards):
            layout.addWidget(card, 0, i)

        if isinstance(self.error_widget, ClickableFrame):
            self.error_widget.clicked.connect(self.error_card_clicked.emit)

        if isinstance(self.near_full_widget, ClickableFrame):
            self.near_full_widget.clicked.connect(self.stk_near_full_card_clicked.emit)

        if isinstance(self.lost_info_widget, ClickableFrame):
            self.lost_info_widget.clicked.connect(self.lost_tray_card_clicked.emit)

    def _create_stat_card(self, title: str, value: str, status: str, color: str) -> QWidget:
        card = ClickableFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self._darken_color(color, 0.15)});
                border-radius: 12px;
            }}
            QLabel {{
                color: white;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold;")

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size: 26px; font-weight: bold;")

        status_label = QLabel(status)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setWordWrap(True)
        status_label.setStyleSheet("font-size: 11px;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(status_label)

        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setMinimumHeight(150)
        card.value_label = value_label
        card.status_label = status_label

        return card

    def _darken_color(self, color: str, factor: float) -> str:
        from PySide6.QtGui import QColor

        color_obj = QColor(color)
        return color_obj.darker(100 + int(100 * factor)).name()

    def set_total_devices(self, count: int):
        card = self.total_widget
        card.value_label.setText(str(count))

        if count <= 0:
            status = "Chưa chọn thiết bị nào"
        elif count == 1:
            status = "Đang giám sát 1 thiết bị"
        else:
            status = f"Đang giám sát {count} thiết bị"

        card.status_label.setText(status)

    def set_lost_tray_count(self, count: int):
        card = self.lost_info_widget
        card.value_label.setText(str(count))

        if count <= 0:
            status = "Kết nối ổn định"
        elif count == 1:
            status = "Có 1 tray mất lệnh"
        else:
            status = f"Có {count} tray mất lệnh"

        card.status_label.setText(status)

    def set_stk_near_full_count(self, count: int):
        card = self.near_full_widget
        card.value_label.setText(str(count))

        if count <= 0:
            status = "Dung lượng an toàn"
        elif count == 1:
            status = "Có 1 Stocker gần đầy"
        else:
            status = f"Có {count} Stocker gần đầy"

        card.status_label.setText(status)

    def set_error_devices_count(self, count: int):
        card = self.error_widget
        card.value_label.setText(str(count))

        if count <= 0:
            status = "Đang hoạt động tốt"
        elif count == 1:
            status = "Có 1 thiết bị đang lỗi"
        else:
            status = f"Có {count} thiết bị đang lỗi"

        card.status_label.setText(status)

class DeviceStatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        header_title = QLabel("💾 LỊCH SỬ LỖI THIẾT BỊ")
        header_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                font-size: 18px;
                text-align: center;
            }
        """)
        layout.addWidget(header_title)

        header_widget = QWidget()
        header_widget.setFixedHeight(30)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 6px;
            }
            QLabel {
                color: white;
                background: transparent;
                font-weight: bold;
                font-size: 11px;
                padding: 2px;
            }
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 4, 15, 4)
        header_layout.setSpacing(0)

        columns = [
            "THỜI GIAN",
            "THIẾT BỊ",
            "LOẠI",
            "TRẠNG THÁI",
            "THỜI GIAN LỖI",
            "HÀNH ĐỘNG",
        ]

        for text in columns:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    background: transparent;
                    padding: 2px 2px;
                }
            """)
            header_layout.addWidget(label, 1)

        layout.addWidget(header_widget)

        self.device_list = QListWidget()
        self.device_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: #f8f9fa;
                padding: 0px;
                font-size: 11px;
                outline: none;
            }
            QListWidget::item {
                border-bottom: 1px solid #e9ecef;
                padding: 0px;
                background-color: white;
                border-radius: 0px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        self.device_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.device_list.setAlternatingRowColors(True)

        layout.addWidget(self.device_list)

        self._setup_overlay_scrollbar()

    def _setup_overlay_scrollbar(self):
        vsb = self.device_list.verticalScrollBar()
        vsb.rangeChanged.connect(lambda *_: self._update_overlay_viewport())
        vsb.valueChanged.connect(lambda *_: self._update_overlay_viewport())

        self._update_overlay_viewport()

    def _update_overlay_viewport(self):
        vsb = self.device_list.verticalScrollBar()

        if vsb.maximum() > 0:
            sb_width = vsb.sizeHint().width()
            self.device_list.setViewportMargins(0, 0, -sb_width, 0)
        else:
            self.device_list.setViewportMargins(0, 0, 0, 0)

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                border-radius: 10px;
                padding: 10px 8px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("🕹 ĐIỀU KHIỂN HỆ THỐNG")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            padding: 5px;
        """)

        header_layout.addWidget(title_label)
        layout.addWidget(header_widget)

        button_group = QGroupBox("⚙️ CHỨC NĂNG HỆ THỐNG")
        button_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 5px 8px 0 8px;
                color: #2c3e50;
            }
        """)

        button_layout = QVBoxLayout(button_group)
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(15, 0, 15, 10)

        self.device_list_btn = QPushButton("📋 DANH SÁCH THIẾT BỊ")
        self.user_guide_btn = QPushButton("📖 HƯỚNG DẪN SỬ DỤNG")
        self.sound_test_btn = QPushButton("🔊 KIỂM TRA ÂM THANH")

        control_buttons = [self.device_list_btn, self.user_guide_btn, self.sound_test_btn]

        for button in control_buttons:
            button.setFixedHeight(45)
            button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #21618c);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #21618c, stop:1 #1b4f72);
                }
            """)
            button_layout.addWidget(button)

        layout.addWidget(button_group)

        info_group = QGroupBox("ℹ️ THÔNG TIN HỆ THỐNG")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)

        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(15, 0, 15, 10)

        info_text = QLabel(
            "• Phiên bản: 2.0.0\n"
            "• Cập nhật: 01/08/2026\n"
            "• Hệ thống được phát triển bởi: Ngô Tôn Quyền"
        )
        info_text.setStyleSheet("color: #7f8c8d; font-size: 12px; line-height: 1.4;")
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)
        layout.addStretch()

class DeviceSelectionDialog(QDialog):
    def __init__(self, parent=None, feature_configs=None):
        super().__init__(parent)
        self.setWindowTitle("CẤU HÌNH DANH SÁCH THIẾT BỊ CẢNH BÁO")
        self.resize(800, 520)
        self.setModal(True)
        self.setWindowIcon(QIcon(APP_ICON_PATH))

        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background: #ffffff;
            }
            QTabBar::tab {
                background: #dfe6e9;
                border: 1px solid #bdc3c7;
                padding: 6px 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                color: #2c3e50;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #2980b9;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #f8f9fa;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21618c, stop:1 #1b4f72);
            }
            QCheckBox {
                font-size: 11px;
                color: #2c3e50;
            }
            QScrollArea {
                border: 1px solid #dcdde1;
                background: #ffffff;
                border-radius: 4px;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)

        self._tab_checkboxes: dict[str, dict[str, QCheckBox]] = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        header = QLabel("📋 CẤU HÌNH THIẾT BỊ CẢNH BÁO")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(header)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        for feature in (feature_configs or []):
            key = feature["key"]
            title = feature["title"]
            devices = sorted(feature["devices"])
            selected = set(feature.get("selected", []))

            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(8, 8, 8, 8)
            tab_layout.setSpacing(8)

            btn_row = QHBoxLayout()
            select_all_btn = QPushButton("Chọn tất cả")
            clear_all_btn = QPushButton("Bỏ chọn tất cả")
            btn_row.addWidget(select_all_btn)
            btn_row.addWidget(clear_all_btn)
            btn_row.addStretch()
            tab_layout.addLayout(btn_row)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            inner = QWidget()
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(6, 6, 6, 6)
            inner_layout.setSpacing(4)

            checkboxes: dict[str, QCheckBox] = {}
            for dev in devices:
                cb = QCheckBox(dev)
                cb.setChecked(dev in selected)
                inner_layout.addWidget(cb)
                checkboxes[dev] = cb

            inner_layout.addStretch()
            scroll.setWidget(inner)
            tab_layout.addWidget(scroll)

            def make_select_all(cbs):
                def _fn():
                    for cb in cbs.values():
                        cb.setChecked(True)
                return _fn

            def make_clear_all(cbs):
                def _fn():
                    for cb in cbs.values():
                        cb.setChecked(False)
                return _fn

            select_all_btn.clicked.connect(make_select_all(checkboxes))
            clear_all_btn.clicked.connect(make_clear_all(checkboxes))

            self._tab_checkboxes[key] = checkboxes
            tab_widget.addTab(tab, title)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def get_selected(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        for key, cbs in self._tab_checkboxes.items():
            result[key] = {dev for dev, cb in cbs.items() if cb.isChecked()}
        return result

class UserGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HƯỚNG DẪN SỬ DỤNG")
        self.resize(820, 540)
        self.setModal(True)
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                background: #ffffff;
            }
            QTabBar::tab {
                background: #dfe6e9;
                border: 1px solid #bdc3c7;
                padding: 6px 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                color: #2c3e50;
                font-size: 11px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #2980b9;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #f8f9fa;
            }
            QLabel {
                font-size: 12px;
                color: #2c3e50;
            }
            QScrollArea {
                border: 1px solid #dcdde1;
                background: #ffffff;
                border-radius: 4px;
            }
            QDialogButtonBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
                min-width: 90px;
            }
            QDialogButtonBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QDialogButtonBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #21618c, stop:1 #1b4f72);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        header = QLabel("📖 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG CẢNH BÁO LỖI MCS")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(header)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        overview_tab = self._create_scroll_tab("""
        <h2>🎯 MỤC ĐÍCH HỆ THỐNG</h2>
        <p>
            Hệ thống <b>CẢNH BÁO LỖI MCS</b> được phát triển để hỗ trợ tối ưu hóa quy trình giám sát MCS:
        </p>
        <ul>
            <li>📊 <b>Giám sát real-time</b> trạng thái hoạt động của các thiết bị 
                <b>OHT, AGV, STK, Buffer, Port</b></li>
            <li>🔊 <b>Phát cảnh báo âm thanh</b> rõ ràng khi phát sinh sự cố 
                hoặc trạng thái bất thường</li>
            <li>📝 <b>Ghi nhận lịch sử lỗi</b> để thuận tiện theo dõi, phân tích 
                và truy vết sự cố</li>
        </ul>

        <h2>🖥️ GIAO DIỆN CHÍNH</h2>

        <h3>🔘 Nút BẬT/TẮT CẢNH BÁO</h3>
        <ul>
            <li>🟢 <b>🔔 BẬT CẢNH BÁO</b>: 
                <ul>
                    <li>Khởi tạo kết nối tới server MCS và OMS</li>
                    <li>Kích hoạt toàn bộ chức năng giám sát</li>
                    <li>Bắt đầu phát cảnh báo âm thanh</li>
                </ul>
            </li>
            <li>🔴 <b>🔕 TẮT CẢNH BÁO</b>: 
                <ul>
                    <li>Ngắt kết nối với server</li>
                    <li>Dừng phát cảnh báo âm thanh</li>
                    <li>Reset các bộ đếm nội bộ</li>
                </ul>
            </li>
        </ul>

        <h3>📶 Trạng Thái Kết Nối</h3>
        <ul>
            <li>🔴 <b>CHƯA KẾT NỐI</b>: 
                Chưa thiết lập kết nối với server MCS và OMS</li>
            <li>🟡 <b>ĐANG KẾT NỐI / ĐANG KẾT NỐI LẠI</b>: 
                Hệ thống đang cố gắng kết nối hoặc tự động reconnect</li>
            <li>🟢 <b>ĐÃ KẾT NỐI</b>: 
                Kết nối với server MCS và OMS đang ổn định và sẵn sàng giám sát</li>
        </ul>

        <h2>📊 CÁC THẺ THỐNG KÊ</h2>

        <h3>📈 TỔNG THIẾT BỊ FA</h3>
        <ul>
            <li>Hiển thị tổng số thiết bị đang được chọn để giám sát</li>
            <li>Giá trị được cập nhật tự động khi người dùng thay đổi 
                cấu hình trong <b>DANH SÁCH THIẾT BỊ</b></li>
        </ul>

        <h3>🚨 THIẾT BỊ ĐANG LỖI</h3>
        <ul>
            <li>Đếm số thiết bị đang ở trạng thái <b>Down</b> và chưa được khắc phục</li>
            <li>Tự động tăng khi phát hiện lỗi mới, giảm khi thiết bị hồi phục</li>
        </ul>

        <h3>📦 STOCKER GẦN ĐẦY</h3>
        <ul>
            <li>Đếm số Stocker đang trong trạng thái gần đầy 
                (dựa trên event <b>ZoneCapacityChange</b>)</li>
            <li>Chỉ tính cho các thiết bị được kích hoạt trong tab <b>STK Gần đầy</b></li>
        </ul>

        <h3>📡 TRAY MẤT LỆNH DI CHUYỂN</h3>
        <ul>
            <li>Đếm số location (Buffer/Port) đang bị mất lệnh di chuyển</li>
            <li>Tự động cập nhật khi hệ thống phát hiện hoặc khắc phục trạng thái mất lệnh</li>
        </ul>
        """)
        tab_widget.addTab(overview_tab, "Tổng quan")

        quick_tab = self._create_scroll_tab("""
        <h2>🚀 QUY TRÌNH VẬN HÀNH CƠ BẢN</h2>

        <ol>
            <li><b>Khởi động ứng dụng</b> 
                <b>HỆ THỐNG CẢNH BÁO LỖI MCS</b> trên máy vận hành</li>
            <li><b>Kiểm tra âm thanh</b> - đảm bảo loa/âm lượng đã được bật 
                và ở mức phù hợp</li>
            <li><b>Kích hoạt giám sát</b> - nhấn nút <b>🔔 BẬT CẢNH BÁO</b> 
                để bắt đầu kết nối</li>
            <li><b>Xác nhận kết nối</b> - kiểm tra trạng thái chuyển sang 
                <b>🟢 ĐÃ KẾT NỐI</b> trước khi giám sát chính thức</li>
        </ol>

        <h2>⚙️ CẤU HÌNH DANH SÁCH THIẾT BỊ</h2>

        <ol>
            <li>Nhấn nút <b>📋 DANH SÁCH THIẾT BỊ</b> ở panel bên trái</li>
            <li>Cấu hình từng nhóm chức năng trong các tab tương ứng:
                <ul>
                    <li><b>OHT Down, AGV Down, STK Down, Port Down, Buffer Down</b>: 
                        Cảnh báo thiết bị Down</li>
                    <li><b>Delay 5 Phút, Delay 10 Phút</b>: 
                        Cảnh báo PORT bị treo lệnh (AlarmReport)</li>
                    <li><b>Buffer, Port mất lệnh</b>: 
                        Cảnh báo CARRIERTYPE = UnKnown hoặc 
                        TRANSFER_STATE = not_trasnferring</li>
                    <li><b>STK Gần đầy</b>: 
                        Cảnh báo Stocker vượt ngưỡng dung lượng ≥90%</li>
                    <li><b>Trạng thái OHT / AGV / STK</b>: 
                        Cảnh báo Auto / Paused / Offline cho controller</li>
                    <li><b>OHT Tắc đường</b>: 
                        Phát hiện OHT không di chuyển qua dữ liệu OMS</li>
                    <li><b>OHT mất kết nối</b>: 
                        Phát hiện OHT mất kết nối với VCS</li>
                </ul>
            </li>
            <li>Sử dụng nút <b>Chọn tất cả / Bỏ chọn tất cả</b> 
                để bật/tắt nhanh cho từng tab</li>
            <li>Nhấn <b>OK</b> để lưu cấu hình - thẻ <b>📊 TỔNG THIẾT BỊ FA</b> 
                sẽ được cập nhật ngay lập tức</li>
        </ol>

        <h2>📖 THEO DÕI LỊCH SỬ LỖI</h2>

        <h3>Hiển Thị</h3>
        <ul>
            <li>Khu vực <b>📖 LỊCH SỬ LỖI THIẾT BỊ</b> hiển thị các lỗi <b>Down</b> 
                theo thời gian thực</li>
            <li>Mỗi cảnh báo Down hợp lệ sẽ tạo <b>một dòng mới</b> với đầy đủ thông tin:
                <ul>
                    <li>⏰ Thời gian xảy ra lỗi</li>
                    <li>🏷️ Tên thiết bị (EQUIPMENTUNITID)</li>
                    <li>🔧 Loại thiết bị (OHT/AGV/Stocker/Process)</li>
                    <li>📊 Trạng thái (Down)</li>
                    <li>⏱️ Thời gian lỗi (phút) - tự động tăng dần</li>
                    <li>🛠️ Hành động (mặc định: <b>Chưa sửa</b>)</li>
                </ul>
            </li>
        </ul>

        <h3>Xử Lý Phục Hồi</h3>
        <ul>
            <li>Khi thiết bị chuyển sang trạng thái tốt 
                (Idle / Run / LoadRequest / UnLoadRequest):
                <ul>
                    <li>Hệ thống đánh dấu <b>✅ Đã sửa</b> cho dòng lỗi mới nhất</li>
                    <li>Ngừng tính thời gian lỗi cho dòng tương ứng</li>
                </ul>
            </li>
        </ul>

        <h3>Quản Lý Dữ Liệu</h3>
        <ul>
            <li>Giới hạn tối đa <b>100 dòng</b> - dòng cũ nhất tự động xoá khi vượt quá</li>
            <li>Tự động cuộn xuống dòng mới nhất để dễ quan sát</li>
        </ul>

        <h2>📝 NHẬT KÝ HỆ THỐNG</h2>

        <ul>
            <li>Nhóm <b>📝 NHẬT KÝ HỆ THỐNG</b> ghi lại toàn bộ hoạt động:
                <ul>
                    <li>🔌 Sự kiện kết nối / mất kết nối / lỗi kết nối server</li>
                    <li>⚡ Hành động xử lý chính (phát cảnh báo, bỏ qua cảnh báo trùng, 
                        reset trạng thái)</li>
                    <li>📊 Phân tích dữ liệu nhận được (OHT tắc đường, STK gần đầy, 
                        Port delay...)</li>
                </ul>
            </li>
            <li>Dựa vào log, người vận hành có thể nhanh chóng xác định nguyên nhân 
                phần mềm phát cảnh báo</li>
        </ul>

        <h2>🔊 KIỂM TRA ÂM THANH</h2>

        <ol>
            <li>Nhấn nút <b>🔊 KIỂM TRA ÂM THANH</b> ở panel bên trái</li>
            <li>Hệ thống phát thử file âm thanh mẫu (ví dụ: OHT Down) 
                qua cơ chế hàng đợi</li>
            <li>Sử dụng chức năng này để kiểm tra:
                <ul>
                    <li>🎵 Hoạt động của loa/tai nghe</li>
                    <li>🔉 Mức âm lượng phù hợp</li>
                </ul>
            </li>
        </ol>
        """)
        tab_widget.addTab(quick_tab, "Cách sử dụng nhanh")

        detail_tab = self._create_scroll_tab("""
        <h2>🚨 CẢNH BÁO THIẾT BỊ DOWN</h2>

        <h3>Phạm Vi Áp Dụng</h3>
        <ul>
            <li>Áp dụng cho các nhóm thiết bị:
                <ul>
                    <li><b>OHT Down</b> - Overhead Hoist Transfer</li>
                    <li><b>AGV Down</b> - Automated Guided Vehicle</li>
                    <li><b>STK Down</b> - Stocker hệ thống</li>
                    <li><b>PORT Down</b> - Cổng xử lý</li>
                    <li><b>BUFFER Down</b> - Vùng đệm</li>
                </ul>
            </li>
        </ul>

        <h3>Điều Kiện Kích Hoạt</h3>
        <ul>
            <li>Khi trạng thái <b>STATE = Down</b> và thiết bị được kích hoạt 
                trong cấu hình:
                <ul>
                    <li>🔊 Phát âm thanh cảnh báo tương ứng loại thiết bị</li>
                    <li>📝 Tạo dòng mới trong <b>LỊCH SỬ LỖI THIẾT BỊ</b></li>
                    <li>⏱️ Bắt đầu đếm thời gian lỗi</li>
                    <li>📊 Đưa vào danh sách <b>THIẾT BỊ ĐANG LỖI</b></li>
                </ul>
            </li>
        </ul>

        <h3>Xử Lý Phục Hồi</h3>
        <ul>
            <li>Khi thiết bị chuyển sang trạng thái tốt:
                <ul>
                    <li>🔄 Tự động loại khỏi danh sách đang lỗi</li>
                    <li>✅ Đánh dấu <b>Đã sửa</b> cho dòng lỗi mới nhất</li>
                    <li>⏹️ Dừng tính thời gian lỗi</li>
                </ul>
            </li>
        </ul>

        <h3>Tối Ưu Hiệu Năng</h3>
        <ul>
            <li>Bỏ qua các bản tin Down trùng lặp trong thời gian ngắn</li>
            <li>Tránh spam cảnh báo khi thiết bị đã được đánh dấu đang lỗi</li>
        </ul>

        <h2>📈 CẢNH BÁO STK GẦN ĐẦY</h2>

        <h3>Nguồn Dữ Liệu</h3>
        <ul>
            <li>Sử dụng event <b>ZoneCapacityChange</b> với các trường:
                <ul>
                    <li><b>MAX_CAPACITY</b> - Dung lượng tối đa</li>
                    <li><b>USED_CAPACITY</b> - Dung lượng đã sử dụng</li>
                </ul>
            </li>
        </ul>

        <h3>Ngưỡng Xử Lý</h3>
        <ul>
            <li>🚨 <b>Đánh dấu FULL</b> khi tỉ lệ sử dụng ≥ <b>90%</b></li>
            <li>🟢 <b>Reset trạng thái</b> khi tỉ lệ giảm xuống ≤ <b>86%</b></li>
        </ul>

        <h3>Điều Kiện Cảnh Báo</h3>
        <ul>
            <li>Chỉ phát âm thanh khi Stocker:
                <ul>
                    <li>Đạt ngưỡng FULL (≥90%)</li>
                    <li>Được kích hoạt trong tab <b>STK Gần đầy</b></li>
                </ul>
            </li>
        </ul>

        <h3>Thống Kê</h3>
        <ul>
            <li>Thẻ <b>📈 STOCKER GẦN ĐẦY</b> hiển thị số lượng STK:
                <ul>
                    <li>Đang trong trạng thái FULL</li>
                    <li>Đang được giám sát tích cực</li>
                </ul>
            </li>
        </ul>

        <h2>📡 CẢNH BÁO MẤT LỆNH DI CHUYỂN</h2>

        <h3>Buffer Mất Lệnh</h3>
        <ul>
            <li><b>Điều kiện phát hiện</b>:
                <ul>
                    <li><b>CARRIERTYPE = UnKnown</b></li>
                    <li>Location thuộc danh sách kích hoạt <b>Buffer mất lệnh</b></li>
                </ul>
            </li>
            <li><b>Xử lý</b>:
                <ul>
                    <li>Phát cảnh báo âm thanh khi phát hiện lần đầu</li>
                    <li>Thêm location vào danh sách TRAY MẤT LỆNH</li>
                    <li>Bỏ qua các cảnh báo lặp lại</li>
                </ul>
            </li>
            <li><b>Khắc phục</b>:
                <ul>
                    <li>Khi Buffer chuyển sang <b>LoadRequest</b> hoặc <b>UnLoadRequest</b></li>
                    <li>Xóa location khỏi danh sách mất lệnh</li>
                    <li>Giảm bộ đếm thống kê</li>
                </ul>
            </li>
        </ul>

        <h3>Port Mất Lệnh</h3>
        <ul>
            <li><b>Điều kiện phát hiện</b>:
                <ul>
                    <li><b>TRANSFER_STATE = not_trasnferring</b></li>
                    <li>Location thuộc danh sách kích hoạt <b>Port mất lệnh</b></li>
                </ul>
            </li>
            <li><b>Xử lý</b>:
                <ul>
                    <li>Logic tương tự Buffer - chỉ cảnh báo lần đầu</li>
                    <li>Bỏ qua các bản tin lặp lại</li>
                </ul>
            </li>
            <li><b>Khắc phục</b>:
                <ul>
                    <li>Khi Port chuyển sang <b>Idle</b> hoặc <b>Run</b></li>
                    <li>Xóa location khỏi danh sách TRAY MẤT LỆNH</li>
                </ul>
            </li>
        </ul>

        <h2>🚧 CẢNH BÁO OHT TẮC ĐƯỜNG</h2>

        <h3>Phạm Vi Giám Sát</h3>
        <ul>
            <li>Áp dụng cho các unit OHT được kích hoạt trong tab <b>OHT Tắc đường</b></li>
            <li>Sử dụng dữ liệu real-time từ OMS (<b>R_VC</b>)</li>
        </ul>

        <h3>Tham Số Giám Sát</h3>
        <ul>
            <li><b>CurNode</b> - Node hiện tại của OHT</li>
            <li><b>TargetNode</b> - Node mục tiêu cần đến</li>
            <li><b>SensorStopped</b> - Trạng thái sensor dừng</li>
            <li><b>DriveSpeed</b> - Tốc độ di chuyển hiện tại</li>
            <li><b>Connected</b> - Trạng thái kết nối VCS</li>
        </ul>

        <h3>Điều Kiện Phát Hiện Tắc Đường</h3>
        <ul>
            <li>OHT được coi là <b>ứng cử viên tắc đường</b> khi đáp ứng đủ:
                <ul>
                    <li>✅ <b>Connected = True</b> - Đang kết nối VCS</li>
                    <li>🎯 <b>TargetNode ≠ 0</b> - Có lệnh di chuyển mục tiêu</li>
                    <li>📍 <b>CurNode ≠ TargetNode</b> - Chưa đến node đích</li>
                    <li>🛑 <b>SensorStopped = True</b> - Sensor báo dừng</li>
                    <li>📉 <b>DriveSpeed = 0</b> - Tốc độ di chuyển bằng 0</li>
                </ul>
            </li>
        </ul>

        <h3>Xác Nhận Tắc Đường</h3>
        <ul>
            <li>Khi OHT duy trì trạng thái ứng cử viên liên tục trong 
                <b>35 giây</b> mà không thay đổi:
                <ul>
                    <li>CurNode và TargetNode không đổi</li>
                    <li>Các điều kiện SensorStopped và DriveSpeed vẫn thỏa mãn</li>
                </ul>
            </li>
            <li>Hệ thống xác nhận <b>OHT TẮC ĐƯỜNG</b> và:
                <ul>
                    <li>🔊 Phát âm thanh cảnh báo OHT-Stopped</li>
                    <li>📝 Ghi log chi tiết vị trí node đang bị đứng</li>
                    <li>🏷️ Đánh dấu đã kích hoạt cảnh báo</li>
                </ul>
            </li>
        </ul>

        <h3>Reset Trạng Thái</h3>
        <ul>
            <li>Tự động reset khi phát hiện thay đổi:
                <ul>
                    <li>🔄 OHT thay đổi CurNode hoặc TargetNode</li>
                    <li>🚗 OHT bắt đầu di chuyển (DriveSpeed > 0)</li>
                    <li>🔧 SensorStopped chuyển sang False</li>
                </ul>
            </li>
        </ul>

        <h3>Quản Lý Controller</h3>
        <ul>
            <li>Controller bị <b>chặn đếm tắc đường</b> khi:
                <ul>
                    <li>Trạng thái controller = <b>Offline</b> hoặc <b>Paused</b></li>
                </ul>
            </li>
            <li>Tự động <b>bỏ chặn</b> khi controller chuyển sang <b>Auto</b></li>
        </ul>

        <h2>💡 MỘT SỐ LƯU Ý VẬN HÀNH</h2>

        <h3>Xử Lý Sự Cố Âm Thanh</h3>
        <ul>
            <li>Nếu cảnh báo không phát tiếng, kiểm tra:
                <ul>
                    <li>📝 Tên file mp3 đúng định dạng (EQUIPMENTUNITID + hậu tố)</li>
                    <li>⚙️ Thiết bị đã được kích hoạt trong <b>DANH SÁCH THIẾT BỊ</b></li>
                    <li>🔊 Loa/âm lượng hệ thống hoạt động bình thường</li>
                </ul>
            </li>
        </ul>

        <h3>Tạm Dừng Hệ Thống</h3>
        <ul>
            <li>Khi cần tạm dừng toàn bộ cảnh báo:
                <ul>
                    <li>Nhấn <b>🔕 TẮT CẢNH BÁO</b> để ngắt kết nối</li>
                    <li>Hệ thống dừng mọi chức năng giám sát</li>
                    <li>Reset toàn bộ trạng thái nội bộ</li>
                </ul>
            </li>
        </ul>

        <h3>Phạm Vi Ứng Dụng</h3>
        <ul>
            <li>Phần mềm chỉ có chức năng <b>GIÁM SÁT VÀ CẢNH BÁO</b></li>
            <li>Không can thiệp điều khiển trực tiếp thiết bị</li>
            <li>Mọi xử lý sự cố cần thực hiện trên hệ thống chính và tại hiện trường</li>
        </ul>
        """)
        tab_widget.addTab(detail_tab, "Chi tiết")

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        close_btn = button_box.button(QDialogButtonBox.Close)
        if close_btn:
            close_btn.clicked.connect(self.reject)

        main_layout.addWidget(button_box)

    def _create_scroll_tab(self, html: str) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(10, 10, 10, 10)
        inner_layout.setSpacing(10)

        label = QLabel()
        label.setTextFormat(Qt.RichText)
        label.setWordWrap(True)
        label.setText(html)

        inner_layout.addWidget(label)
        inner_layout.addStretch()

        scroll.setWidget(inner)
        layout.addWidget(scroll)

        return tab

class LoadingScreen(QWidget):
    finished = Signal()

    def __init__(
        self,
        img1: str,
        img2: str,
        switch_ms: int = 1000,
        total_ms: int = 2500,
        version: str = "2.0.0",
        author: str = "Ngô Tôn Quyền"
    ):
        super().__init__()

        self.img1 = img1
        self.img2 = img2
        self.switch_ms = switch_ms
        self.total_ms = total_ms
        self.version = version
        self.author = author
        self.elapsed = 0
        self.switched = False
        self.tips = [
            "Giám sát OHT, AGV, STK, Buffer, Port theo thời gian thực.",
            "Nhấp vào thiết bị Down để xem chi tiết lỗi.",
            "Cấu hình danh sách thiết bị để tối ưu cảnh báo.",
            "Hệ thống hoạt động ổn định trên Windows 10+ và không cần cài đặt.",
        ]
        self.tip_index = 0
        self._build_ui()
        self.main_timer = QTimer(self)
        self.main_timer.setInterval(50)
        self.main_timer.timeout.connect(self._tick)
        self.tip_timer = QTimer(self)
        self.tip_timer.setInterval(2500)
        self.tip_timer.timeout.connect(self._next_tip)
        self.fade = QPropertyAnimation(self, b"windowOpacity")
        self.fade.setDuration(700)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.OutCubic)

    def _build_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            #card {
                background: rgba(20, 27, 45, 1.0);
                border-radius: 22px;
                border: 1px solid rgba(255, 255, 255, 0.12);
            }
            QLabel { color: #e5e7eb; }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        root.addWidget(card)

        main = QVBoxLayout(card)
        main.setContentsMargins(26, 24, 26, 24)
        main.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(12)

        logo = QLabel("FA")
        logo.setFixedSize(46, 46)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0ea5e9,
                    stop:1 #6366f1
                );
                border-radius: 23px;
                font-size: 22px;
                font-weight: bold;
                color: white;
            }
        """)

        titlebox = QVBoxLayout()
        title = QLabel("HỆ THỐNG CẢNH BÁO LỖI MCS")
        title.setFont(QFont("Segoe UI", 13, QFont.Bold))

        self.tagline = QLabel("Giám sát vận hành • cảnh báo real-time • tối ưu xử lý sự cố")
        self.tagline.setFont(QFont("Segoe UI", 9))
        self.tagline.setStyleSheet("color: #9ca3af;")

        titlebox.addWidget(title)
        titlebox.addWidget(self.tagline)

        self.small_status = QLabel("Đang khởi động…")
        self.small_status.setAlignment(Qt.AlignCenter)
        self.small_status.setStyleSheet("""
            QLabel {
                background: rgba(37, 99, 235, 0.25);
                color: #bfdbfe;
                border-radius: 999px;
                padding: 5px 12px;
                font-size: 10px;
            }
        """)

        header.addWidget(logo)
        header.addLayout(titlebox)
        header.addStretch()
        header.addWidget(self.small_status)

        main.addLayout(header)

        img_frame = QFrame()
        img_frame.setObjectName("imgframe")
        img_frame.setStyleSheet("""
            #imgframe {
                background: rgba(255,255,255,0.03);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.06);
            }
        """)

        img_layout = QVBoxLayout(img_frame)
        img_layout.setContentsMargins(12, 12, 12, 12)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)

        img_layout.addWidget(self.image_label)
        main.addWidget(img_frame)

        self._set_image(self.img1, initial=True)

        tags = QHBoxLayout()

        version_tag = QLabel(f"Phiên bản {self.version}")
        version_tag.setAlignment(Qt.AlignCenter)
        version_tag.setStyleSheet("""
            QLabel {
                background: rgba(59,130,246,0.18);
                color: #93c5fd;
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 10px;
            }
        """)

        author_tag = QLabel(f"Phát triển: {self.author}")
        author_tag.setAlignment(Qt.AlignCenter)
        author_tag.setStyleSheet("""
            QLabel {
                background: rgba(16,185,129,0.18);
                color: #6ee7b7;
                border-radius: 999px;
                padding: 4px 12px;
                font-size: 10px;
            }
        """)

        tags.addStretch()
        tags.addWidget(version_tag)
        tags.addWidget(author_tag)
        tags.addStretch()

        main.addLayout(tags)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #0f172a;
                border-radius: 9px;
                height: 18px;
                text-align: center;
                color: #e5e7eb;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #22c55e,
                    stop:1 #14b8a6
                );
                border-radius: 9px;
            }
        """)

        main.addWidget(self.progress)

        self.status = QLabel("Đang khởi động hệ thống giám sát…")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setFont(QFont("Segoe UI", 9))
        self.status.setStyleSheet("color: #d1d5db;")
        main.addWidget(self.status)

        self.tip_label = QLabel(self.tips[0])
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setFont(QFont("Segoe UI", 8))
        self.tip_label.setStyleSheet("color: #9ca3af;")
        main.addWidget(self.tip_label)

        self.resize(700, 520)

    def _set_image(self, path: str, initial=False):
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaled(
                380, 260,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        self.image_label.setPixmap(pix)

    def start(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

        self.elapsed = 0
        self.switched = False
        self.progress.setValue(0)
        self.setWindowOpacity(1.0)
        self.show()
        self.fade.start()
        self.main_timer.start()
        self.tip_timer.start()

    def _next_tip(self):
        self.tip_index = (self.tip_index + 1) % len(self.tips)
        self.tip_label.setText(self.tips[self.tip_index])

    def _tick(self):
        self.elapsed += self.main_timer.interval()

        if not self.switched and self.elapsed >= self.switch_ms:
            self.switched = True
            self._set_image(self.img2)

        ratio = min(1.0, self.elapsed / self.total_ms)
        self.progress.setValue(int(ratio * 100))

        if ratio < 0.33:
            self.status.setText("Đang tải cấu hình thiết bị…")
            self.small_status.setText("Khởi động…")
        elif ratio < 0.66:
            self.status.setText("Đang kết nối MCS & OMS…")
            self.small_status.setText("Kết nối…")
        else:
            self.status.setText("Chuẩn bị mở giao diện chính…")
            self.small_status.setText("Sẵn sàng")

        if self.elapsed >= self.total_ms:
            self.main_timer.stop()
            self.tip_timer.stop()
            self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        self.alert_enabled = False
        self.ws_worker = None
        self.sound_cache = {}
        self.sound_queue = []
        self.current_player = None
        self.last_funny_sound_time = 0
        self.funny_sound_list = [
            "HoiReset.mp3",
            "ResetGiup.mp3",
            "GoiKySu.mp3",
            "DeToiXuLy.mp3"
        ]
        self.funny_sound_index = 0
        self.zone_full_state: dict[str, bool] = {}
        self.zone_usage_percent: dict[str, float] = {}
        self.last_down_event_ts: dict[str, float] = {}
        self.down_history: dict[str, list[float]] = {}
        self.last_alarm_by_unit: dict[str, dict] = {}
        self.config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "MCSMonitor")
        os.makedirs(self.config_dir, exist_ok=True)
        if hasattr(sys, "_MEIPASS"):
            self.base_dir = sys._MEIPASS 
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.enabled_oht_down = set(OHT_DOWN_EQUIPMENTS)
        self.enabled_agv_down = set(AGV_DOWN_EQUIPMENTS)
        self.enabled_stk_down = set(STK_DOWN_EQUIPMENTS)
        self.enabled_port_down = set(PORT_DOWN_EQUIPMENTS)
        self.enabled_buffer_down = set(BUFFER_DOWN_EQUIPMENTS)
        self.enabled_oht_jam = set(OHT_DOWN_EQUIPMENTS)
        self.enabled_port_delay_5 = set(PORT_DELAY_EQUIPMENTS)
        self.enabled_port_delay_10 = set(PORT_DELAY_EQUIPMENTS)
        self.enabled_buffer_unknown = set(BUFFER_UNKNOWN_EQUIPMENTS)
        self.enabled_port_unknown = set(PORT_DELAY_EQUIPMENTS)
        self.enabled_stk_full = set(STK_STATUS_EQUIPMENTS)
        self.enabled_oht_status = set(OHT_STATUS_EQUIPMENTS)
        self.enabled_agv_status = set(AGV_STATUS_EQUIPMENTS)
        self.enabled_stk_status = set(STK_STATUS_EQUIPMENTS)
        self.oms_workers: list[OmsSiteWorker] = []

        self.oht_jam_info: dict[str, dict] = {}
        
        self.oht_jam_threshold_by_controller = {
            "HNMOHV01": 50,
            "HNMOHV02": 50,
            "HNMOHV03": 35,
            "HNMOHV04": 35,
            "HNMOHV05": 35,
        }
        self.oht_jam_threshold_default = 50

        self.oht_jam_sound_cooldown: float = 60.0
        self.oht_jam_global_mute_until: float = 0.0
        self.oht_unit_by_controller: dict[str, list[str]] = {}
        for site in OMS_SITES:
            name = site.get("name")
            unit = site.get("unit") or []
            if name:
                self.oht_unit_by_controller[name] = list(unit)

        self.oht_jam_blocked_controllers: dict[str, bool] = {}
        self.down_equipments: set[str] = set()
        self.oht_oms_connected: dict[str, bool] = {}
        self.lost_tray_locations: set[str] = set()
        self.lost_tray_recover_deadline: dict[str, float] = {}
        self.device_error_rows: list[dict] = []
        self._initialize_ui()
        self._setup_connections()
        self._setup_error_duration_timer()
        self._setup_oht_jam_timer()
        self._recalculate_total_devices()
        self.stats_widget.set_lost_tray_count(0)
        self.stats_widget.set_stk_near_full_count(0)
        self.stats_widget.set_error_devices_count(0)

    def play_welcome_sound(self):
        filename = "welcome.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "System", filename)
        cache_key = "SYSTEM-WELCOME"
        self._play_sound_file(cache_key, "[ÂM THANH HỆ THỐNG]", sound_path)

    def play_bye_sound(self):
        filename = "bye.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "System", filename)
        cache_key = "SYSTEM-BYE"
        self._play_sound_file(cache_key, "[ÂM THANH HỆ THỐNG]", sound_path)

    def play_disconnect_sound(self):
        filename = "disconnect.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "System", filename)
        cache_key = "SYSTEM-DISCONNECT"
        self._play_sound_file(cache_key, "[ÂM THANH MẤT KẾT NỐI]", sound_path)

    def _initialize_ui(self):
        self.setWindowTitle("HỆ THỐNG CẢNH BÁO LỖI MCS")
        self.resize(1200, 700)
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()

        title_label = QLabel("HỆ THỐNG CẢNH BÁO LỖI MCS")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.alert_button = QPushButton()
        self.alert_button.setFixedHeight(40)
        self._update_alert_button(False)
        self.status_label = QLabel("🔴 CHƯA KẾT NỐI")
        self.status_label.setFixedHeight(40)
        self._set_status_label_color("#e74c3c")

        header_layout.addWidget(self.alert_button)
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        self.stats_widget = StatisticsWidget()
        main_layout.addWidget(self.stats_widget)

        self.stats_widget.error_card_clicked.connect(self.show_error_devices_popup)
        self.stats_widget.stk_near_full_card_clicked.connect(self.show_stk_full_popup)
        self.stats_widget.lost_tray_card_clicked.connect(self.show_lost_tray_popup)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        self.control_panel = ControlPanel()
        content_layout.addWidget(self.control_panel, 1)

        self.device_status_widget = DeviceStatusWidget()
        content_layout.addWidget(self.device_status_widget, 2)

        main_layout.addLayout(content_layout)

        log_group = QGroupBox("📝 NHẬT KÝ HỆ THỐNG")
        log_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
            """
        )

        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 5, 10, 10) 
        log_layout.setSpacing(5)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                background-color: #f8f9fa;
            }
            """
        )
        log_layout.addWidget(self.log_display)

        main_layout.addWidget(log_group)

    def _update_alert_button(self, enabled: bool):
        if enabled:
            self.alert_button.setText("🔕 TẮT CẢNH BÁO")
            self.alert_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f1c40f, stop:1 #f39c12);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0px 10px 0px 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f39c12, stop:1 #d68910);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d68910, stop:1 #b9770e);
                }
            """)
        else:
            self.alert_button.setText("🔔 BẬT CẢNH BÁO")
            self.alert_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 0px 10px 0px 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2980b9, stop:1 #21618c);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #21618c, stop:1 #1b4f72);
                }
            """)

    def _set_status_label_color(self, bg_color: str):
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                background-color: {bg_color};
                border-radius: 6px;
            }}
        """)

    def open_device_list_dialog(self):
        feature_configs = [
            {"key": "oht_down",       "title": "OHT Down",        "devices": OHT_DOWN_EQUIPMENTS,       "selected": self.enabled_oht_down},
            {"key": "agv_down",       "title": "AGV Down",        "devices": AGV_DOWN_EQUIPMENTS,       "selected": self.enabled_agv_down},
            {"key": "stk_down",       "title": "STK Down",        "devices": STK_DOWN_EQUIPMENTS,       "selected": self.enabled_stk_down},
            {"key": "port_down",      "title": "Port Down",       "devices": PORT_DOWN_EQUIPMENTS,      "selected": self.enabled_port_down},
            {"key": "buffer_down",    "title": "Buffer Down",     "devices": BUFFER_DOWN_EQUIPMENTS,    "selected": self.enabled_buffer_down},
            {"key": "delay_5",        "title": "Delay 5 Phút",    "devices": PORT_DELAY_EQUIPMENTS,     "selected": self.enabled_port_delay_5},
            {"key": "delay_10",       "title": "Delay 10 Phút",   "devices": PORT_DELAY_EQUIPMENTS,     "selected": self.enabled_port_delay_10},
            {"key": "buffer_unknown", "title": "Buffer mất lệnh", "devices": BUFFER_UNKNOWN_EQUIPMENTS, "selected": self.enabled_buffer_unknown},
            {"key": "port_unknown",   "title": "Port mất lệnh",   "devices": PORT_DELAY_EQUIPMENTS,     "selected": self.enabled_port_unknown},
            {"key": "stk_full",       "title": "STK Gần đầy",     "devices": STK_STATUS_EQUIPMENTS,     "selected": self.enabled_stk_full},
            {"key": "oht_status",     "title": "Trạng thái OHT",  "devices": OHT_STATUS_EQUIPMENTS,     "selected": self.enabled_oht_status},
            {"key": "agv_status",     "title": "Trạng thái AGV",  "devices": AGV_STATUS_EQUIPMENTS,     "selected": self.enabled_agv_status},
            {"key": "stk_status",     "title": "Trạng thái STK",  "devices": STK_STATUS_EQUIPMENTS,     "selected": self.enabled_stk_status},
            {"key": "oht_jam",        "title": "OHT Tắc đường",   "devices": OHT_DOWN_EQUIPMENTS,       "selected": self.enabled_oht_jam},
        ]

        dlg = DeviceSelectionDialog(self, feature_configs)
        if dlg.exec():
            selected = dlg.get_selected()

            self.enabled_oht_down       = selected.get("oht_down", set())
            self.enabled_agv_down       = selected.get("agv_down", set())
            self.enabled_stk_down       = selected.get("stk_down", set())
            self.enabled_port_down      = selected.get("port_down", set())
            self.enabled_buffer_down    = selected.get("buffer_down", set())
            self.enabled_port_delay_5   = selected.get("delay_5", set())
            self.enabled_port_delay_10  = selected.get("delay_10", set())
            self.enabled_buffer_unknown = selected.get("buffer_unknown", set())
            self.enabled_port_unknown   = selected.get("port_unknown", set())
            self.enabled_stk_full       = selected.get("stk_full", set())
            self.enabled_oht_status     = selected.get("oht_status", set())
            self.enabled_agv_status     = selected.get("agv_status", set())
            self.enabled_stk_status     = selected.get("stk_status", set())
            self.enabled_oht_jam        = selected.get("oht_jam", set())

            self._recalculate_total_devices()
            self.append_log("Đã cập nhật danh sách thiết bị!")
            self._update_stk_near_full_stat()
            self._refresh_down_equipments_after_config()

    def _recalculate_total_devices(self):
        total = (
            len(self.enabled_oht_down) +
            len(self.enabled_agv_down) +
            len(self.enabled_stk_down) +
            len(self.enabled_port_down) +
            len(self.enabled_buffer_down)
        )

        self.stats_widget.set_total_devices(total)

    def _update_lost_tray_stat(self):
        count = len(self.lost_tray_locations)
        self.stats_widget.set_lost_tray_count(count)

    def _add_lost_tray(self, location: str):
        if location not in self.lost_tray_locations:
            self.lost_tray_locations.add(location)
            if hasattr(self, "lost_tray_recover_deadline"):
                self.lost_tray_recover_deadline.pop(location, None)

            self._update_lost_tray_stat()

    def _remove_lost_tray(self, location: str):
        if location in self.lost_tray_locations:
            self.lost_tray_locations.remove(location)

        if hasattr(self, "lost_tray_recover_deadline"):
            self.lost_tray_recover_deadline.pop(location, None)

        self._update_lost_tray_stat()

    def _schedule_lost_tray_recover(self, location: str, delay_seconds: float, reason: str):
        if location not in self.lost_tray_locations:
            return

        now_ts = time.monotonic()
        deadline = now_ts + delay_seconds

        if not hasattr(self, "lost_tray_recover_deadline"):
            self.lost_tray_recover_deadline = {}

        self.lost_tray_recover_deadline[location] = deadline
        self.debug_log(
            f"[TRAY-RECOVER-SCHEDULE] {location} được lên lịch khôi phục sau {int(delay_seconds)}s ({reason})."
        )

    def _process_lost_tray_recover(self):
        if not hasattr(self, "lost_tray_recover_deadline"):
            return

        if not self.lost_tray_recover_deadline:
            return

        now_ts = time.monotonic()
        for loc, deadline in list(self.lost_tray_recover_deadline.items()):
            if now_ts >= deadline:
                self.debug_log(
                    f"[TRAY-RECOVER-DO] Thực hiện khôi phục cho {loc} sau khi chờ đủ thời gian."
                )
                self._remove_lost_tray(loc)

    def _update_stk_near_full_stat(self):
        count = 0
        for eqp, is_full in self.zone_full_state.items():
            if is_full and eqp in self.enabled_stk_full:
                count += 1
        self.stats_widget.set_stk_near_full_count(count)

    def _update_error_stat(self):
        self.stats_widget.set_error_devices_count(len(self.down_equipments))

    def _add_down_equipment(self, unit_id: str):
        if unit_id and unit_id not in self.down_equipments:
            self.down_equipments.add(unit_id)
            self._update_error_stat()
            self.debug_log(f"[ERROR-ADD] {unit_id} được đánh dấu là đang lỗi (Down)")
            self.check_spam_reset(unit_id)
            self.maybe_play_funny_sound()

    def check_spam_reset(self, unit_id: str):
        now = time.time()

        if unit_id not in self.down_history:
            self.down_history[unit_id] = []

        history = self.down_history[unit_id]

        history.append(now)

        history = [t for t in history if now - t <= 30]
        self.down_history[unit_id] = history

        if len(history) >= 3:
            sound_path = os.path.join(
                self.base_dir,
                "sound",
                "Funny",
                "SpamReset.mp3"
            )

            self._play_sound_file(
                f"SPAM-RESET-{unit_id}",
                "[RESET LIÊN TỤC]",
                sound_path
            )

            self.down_history[unit_id] = []

    def _remove_down_equipment(self, unit_id: str):
        if unit_id in self.down_equipments:
            self.down_equipments.remove(unit_id)
            self._update_error_stat()
            self.debug_log(f"[ERROR-RECOVER] {unit_id} đã khắc phục, xoá khỏi danh sách THIẾT BỊ ĐANG LỖI")

    def _refresh_down_equipments_after_config(self):
        valid: set[str] = set()
        for unit in self.down_equipments:
            if (
                unit in self.enabled_oht_down
                or unit in self.enabled_agv_down
                or unit in self.enabled_stk_down
                or unit in self.enabled_port_down
                or unit in self.enabled_buffer_down
            ):
                valid.add(unit)
        self.down_equipments = valid
        self._update_error_stat()

    def open_user_guide(self):
        dlg = UserGuideDialog(self)
        dlg.exec()

    def _mark_device_error_recovered(self, unit_id: str, new_state: str):
        if not self.device_error_rows:
            return

        for info in reversed(self.device_error_rows):
            if info.get("equipment_unit_id") != unit_id:
                continue
            if not info.get("active", False):
                continue

            labels = info["labels"]
            labels["state"].setText(new_state)
            labels["action"].setText("✅ Đã sửa")
            info["active"] = False
            break

    def start_oms_websockets(self):
        if self.oms_workers: 
            return
        for site_cfg in OMS_SITES:
            worker = OmsSiteWorker(site_cfg)
            worker.rvc_received.connect(self.handle_oms_rvc)
            self.oms_workers.append(worker)
            worker.start()
            self.append_log(f"[OMS] BẮT ĐẦU KẾT NỐI OMS {site_cfg['name']}")

    def stop_oms_websockets(self):
        for w in self.oms_workers:
            try:
                w.stop()
            except Exception:
                pass
        self.oms_workers.clear()
        self.append_log("[OMS] ĐÃ DỪNG TẤT CẢ KẾT NỐI OMS")
        self.oht_jam_info.clear()
        self.oht_oms_connected.clear()

    def _set_oht_jam_block_by_controller(self, controller_id: str, blocked: bool):
        self.oht_jam_blocked_controllers[controller_id] = blocked
        state_text = "BỊ CHẶN" if blocked else "ĐƯỢC PHÉP"
        self.append_log(f"[OHT-JAM] Controller {controller_id} {state_text} đếm tắc đường")

    def handle_oms_rvc(self, site_name: str, rvc_list: list[dict]):
        if not self.alert_enabled:
            return

        now = time.monotonic()

        for vc in rvc_list:
            try:
                vc_id = int(vc.get("Id", 0))
            except Exception:
                continue
            if vc_id <= 0:
                continue

            unit_id = map_oms_id_to_unit_id(site_name, vc_id)
            if not unit_id:
                continue

            if unit_id not in OHT_DOWN_EQUIPMENTS:
                continue

            connected = bool(vc.get("Connected", False))
            prev_connected = self.oht_oms_connected.get(unit_id)

            if prev_connected is None:
                self.oht_oms_connected[unit_id] = connected
                if not connected:
                    self.append_log(
                        f"[OHT-VCS] {unit_id} đang ở trạng thái Disconnected, phát cảnh báo."
                    )
                    self.play_oht_disconnected_sound(unit_id)
            else:
                if prev_connected and not connected:
                    self.append_log(
                        f"[OHT-VCS] {unit_id} MẤT KẾT NỐI VCS, phát cảnh báo Disconnected."
                    )
                    self.play_oht_disconnected_sound(unit_id)
                    self.oht_oms_connected[unit_id] = False
                elif not prev_connected and connected:
                    self.append_log(
                        f"[OHT-VCS] {unit_id} ĐÃ KẾT NỐI LẠI VCS."
                    )
                    self.oht_oms_connected[unit_id] = True
                else:
                    pass

            self._update_oht_jam_from_vc(unit_id, vc, now)

    def _update_oht_jam_from_vc(self, unit_id: str, vc: dict, now_ts: float):
        if unit_id not in self.enabled_oht_jam:
            return
    
        controller_id = unit_id.split("-")[0] if "-" in unit_id else unit_id

        def clear_info(reason_log: str | None = None):
            info = self.oht_jam_info.get(unit_id)
            if info is None:
                return
            if reason_log and (info.get("last_sensor_state") or info.get("jam_triggered")):
                self.append_log(reason_log)
            info["last_sensor_state"] = False
            info["sensor_start_ts"] = 0.0
            info["jam_triggered"] = False
            info["cur_node"] = 0
            info["target_node"] = 0

        if self.oht_jam_blocked_controllers.get(controller_id, False):
            clear_info(None)
            return

        if self._controller_has_down_oht(controller_id):
            clear_info(
                f"[OHT] Bỏ qua đếm tắc đường cho {unit_id} vì trong {controller_id} đang có OHT Down."
            )
            return

        if unit_id in self.down_equipments:
            clear_info(None)
            return

        raw_sensor = vc.get("SensorStopped")
        if raw_sensor is None:
            raw_sensor = vc.get("sensorStopped")
        if raw_sensor is None:
            raw_sensor = vc.get("SENSORSTOPPED")
        sensor_stopped = bool(raw_sensor)

        try:
            cur_node = int(vc.get("CurNode") or vc.get("curnode") or 0)
        except Exception:
            cur_node = 0

        try:
            target_node = int(vc.get("TargetNode") or vc.get("targetnode") or 0)
        except Exception:
            target_node = 0

        info = self.oht_jam_info.get(unit_id)
        if info is None:
            info = {
                "last_sensor_state": False,
                "sensor_start_ts": 0.0,
                "jam_triggered": False,
                "cur_node": cur_node,
                "target_node": target_node,
            }
            self.oht_jam_info[unit_id] = info

        last_state = bool(info.get("last_sensor_state", False))

        info["cur_node"] = cur_node
        info["target_node"] = target_node

        if not sensor_stopped:
            if last_state:
                self.debug_log(
                    f"[OHT-JAM-RECOVER] {unit_id} SensorStopped=False - dừng đếm tắc đường "
                    f"(CurNode={cur_node}, TargetNode={target_node})."
                )
            info["last_sensor_state"] = False
            info["sensor_start_ts"] = 0.0
            info["jam_triggered"] = False
            return

        if not last_state:
            info["last_sensor_state"] = True
            info["sensor_start_ts"] = now_ts
            info["jam_triggered"] = False
            self.debug_log(
                f"[OHT-JAM] {unit_id} SensorStopped=True - bắt đầu đếm thời gian tắc đường "
                f"(CurNode={cur_node}, TargetNode={target_node})."
            )
        else:
            info["last_sensor_state"] = True

    def _controller_has_down_oht(self, controller_id: str) -> bool:
        unit = self.oht_unit_by_controller.get(controller_id, [])
        for u in unit:
            if u in self.down_equipments:
                return True
        return False

    def _setup_connections(self):
        self.alert_button.clicked.connect(self.toggle_alert)
        self.control_panel.sound_test_btn.clicked.connect(self.test_sound)
        self.control_panel.device_list_btn.clicked.connect(self.open_device_list_dialog)
        self.control_panel.user_guide_btn.clicked.connect(self.open_user_guide)
        self.device_status_widget.device_list.itemClicked.connect(
            self.on_device_history_item_clicked
        )

    def start_websocket(self):
        if self.ws_worker is not None:
            return

        url = "ws://10.121.61.174:8090/mcsMonitoring"
        self.ws_worker = WebSocketWorker(url)
        self.ws_worker.message_received.connect(self.handle_ws_message)
        self.ws_worker.status_changed.connect(self.update_connection_status)
        self.ws_worker.start()

    def stop_websocket(self):
        if self.ws_worker is not None:
            try:
                self.ws_worker.stop()
            except Exception:
                pass
            self.ws_worker = None
            self.append_log("ĐÃ DỪNG KẾT NỐI WebSocket")

        self.update_connection_status(False, "🔴 CHƯA KẾT NỐI")
        self.alert_enabled = False
        self.oht_jam_info.clear()
        self.zone_full_state.clear()
        self.zone_usage_percent.clear()
        self.lost_tray_locations.clear()
        self.stats_widget.set_lost_tray_count(0)
        self.stats_widget.set_stk_near_full_count(0)
        self.down_equipments.clear()
        self.stats_widget.set_error_devices_count(0)
        self.last_alarm_by_unit.clear()

    def _setup_error_duration_timer(self):
        self.error_duration_timer = QTimer(self)
        self.error_duration_timer.setInterval(1000)
        self.error_duration_timer.timeout.connect(self._update_error_durations)
        self.error_duration_timer.start()

        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.setInterval(5 * 60 * 1000)
        self.cleanup_timer.timeout.connect(self._cleanup_runtime_cache)
        self.cleanup_timer.start()

    def _setup_oht_jam_timer(self):
        self.oht_jam_timer = QTimer(self)
        self.oht_jam_timer.setInterval(1000)
        self.oht_jam_timer.timeout.connect(self._check_oht_jam_timeout)
        self.oht_jam_timer.start()

    def _check_oht_jam_timeout(self):
        if not self.alert_enabled:
            return

        now_ts = time.monotonic()

        for unit_id, info in list(self.oht_jam_info.items()):
            if not info.get("last_sensor_state", False):
                continue

            start_ts = info.get("sensor_start_ts") or 0.0
            if start_ts <= 0.0:
                continue

            if info.get("jam_triggered", False):
                continue

            controller_id = unit_id.split("-")[0] if "-" in unit_id else unit_id

            if self.oht_jam_blocked_controllers.get(controller_id, False):
                continue

            if self._controller_has_down_oht(controller_id):
                continue

            if unit_id in self.down_equipments:
                continue

            elapsed = now_ts - start_ts

            threshold = getattr(self, "oht_jam_threshold_by_controller", {}).get(
                controller_id,
                getattr(self, "oht_jam_threshold_default", 50)
            )

            if elapsed < threshold:
                continue

            self._trigger_oht_jam(unit_id, info, now_ts)

    def _trigger_oht_jam(self, unit_id: str, info: dict, now_ts: float):
        if info.get("jam_triggered", False):
            return

        info["jam_triggered"] = True

        cur_node = info.get("cur_node", 0)
        target_node = info.get("target_node", 0)
        start_ts = info.get("sensor_start_ts") or now_ts
        elapsed = now_ts - start_ts

        enabled_for_jam = unit_id in self.enabled_oht_jam

        if now_ts < getattr(self, "oht_jam_global_mute_until", 0.0):
            self.append_log(
                f"[OHT-STOPPED] {unit_id} TẮC ĐƯỜNG: SensorStopped=True trong {int(elapsed)}s "
                f"(TRONG COOLDOWN âm thanh, chỉ ghi log)."
            )
            return

        self.oht_jam_global_mute_until = now_ts + self.oht_jam_sound_cooldown

        if not enabled_for_jam:
            self.append_log(
                f"[OHT-STOPPED] {unit_id} TẮC ĐƯỜNG: SensorStopped=True trong {int(elapsed)}s "
                f"(đang TẮT cảnh báo OHT TẮC ĐƯỜNG trong cấu hình)."
            )
            return

        self.append_log(
            f"[OHT] Thiết bị {unit_id} có thể thị tắc đường, Sensor Stopped bật liên tục trong {int(elapsed)}s "
            f"tại CurNode={cur_node}, TargetNode={target_node}."
        )
        self.play_oht_stopped_sound(unit_id)           

    def _update_error_durations(self):
        if not self.device_error_rows:
            return
        now = datetime.now()
        need_alert_5 = False
        need_alert_10 = False
        need_alert_30 = False
        need_alert_60 = False

        for info in self.device_error_rows:
            if not info.get("active", False):
                continue
            start_time = info.get("start_time")
            if not start_time:
                continue
            delta = now - start_time
            total_seconds = delta.total_seconds()
            minutes = int(total_seconds // 60)
            duration_label = info["labels"]["duration"]
            duration_label.setText(f"{minutes} phút")
            eqp_id = info.get("equipment_unit_id")
            if not eqp_id:
                continue
            if (
                eqp_id in OHT_DOWN_EQUIPMENTS
                or eqp_id in AGV_DOWN_EQUIPMENTS
                or eqp_id in STK_DOWN_EQUIPMENTS
                or eqp_id in PORT_DOWN_EQUIPMENTS
                or eqp_id in BUFFER_DOWN_EQUIPMENTS
            ):
                if minutes >= 5 and not info.get("warn_5", False):

                    if (
                        eqp_id in OHT_DOWN_EQUIPMENTS
                        or eqp_id in AGV_DOWN_EQUIPMENTS
                        or eqp_id in STK_DOWN_EQUIPMENTS
                    ):
                        info["warn_5"] = True
                        need_alert_5 = True

                        self.append_log(
                            f"[LỖI 5 PHÚT] {eqp_id} thuộc nhóm cảnh báo, phát âm thanh."
                        )

                if minutes >= 10 and not info.get("warn_10", False):
                    info["warn_10"] = True
                    need_alert_10 = True
                    self.append_log(
                        f"[LỖI 10 PHÚT] {eqp_id} lỗi ≥ 10 phút, phát cảnh báo."
                    )
                if minutes >= 30 and not info.get("warn_30", False):
                    info["warn_30"] = True
                    need_alert_30 = True
                    self.append_log(
                        f"[LỖI 30 PHÚT] {eqp_id} lỗi ≥ 30 phút, phát cảnh báo."
                    )
                if minutes >= 60 and not info.get("warn_60", False):
                    info["warn_60"] = True
                    need_alert_60 = True
                    self.append_log(
                        f"[LỖI 60 PHÚT] {eqp_id} lỗi ≥ 60 phút, phát cảnh báo."
                    )
        self._process_lost_tray_recover()

        if need_alert_5:
            self.play_error_duration_sound(5)

        if need_alert_10:
            self.play_error_duration_sound(10)

        if need_alert_30:
            self.play_error_duration_sound(30)

        if need_alert_60:
            self.play_error_duration_sound(60)

    def _cleanup_runtime_cache(self):

        if len(self.last_alarm_by_unit) > 500:
            self.last_alarm_by_unit.clear()
            self.debug_log("[CLEANUP] Clear last_alarm_by_unit")

        if len(self.last_down_event_ts) > 500:
            self.last_down_event_ts.clear()
            self.debug_log("[CLEANUP] Clear last_down_event_ts")

        if len(self.oht_jam_info) > 200:
            self.oht_jam_info.clear()
            self.debug_log("[CLEANUP] Clear oht_jam_info")

        if hasattr(self, "lost_tray_recover_deadline"):
            if len(self.lost_tray_recover_deadline) > 200:
                self.lost_tray_recover_deadline.clear()
                self.debug_log("[CLEANUP] Clear lost_tray_recover_deadline")

        if len(self.zone_usage_percent) > 200:
            self.zone_usage_percent.clear()
            self.debug_log("[CLEANUP] Clear zone_usage_percent")

    def _trim_device_history_rows(self):
        max_rows = 100
        list_widget = self.device_status_widget.device_list

        while len(self.device_error_rows) > max_rows:
            oldest = self.device_error_rows.pop(0)

            item = oldest.get("item")
            widget = oldest.get("widget")

            if widget:
                widget.deleteLater()

            if item:
                row = list_widget.row(item)
                if row >= 0:
                    list_widget.takeItem(row)

    def debug_log(self, text: str):
        print(text)

    def append_log(self, text: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] {text}"

        self.log_display.append(line)

        max_lines = 100
        if self.log_display.document().blockCount() > max_lines:
            self.log_display.clear()
            self.log_display.append(
                "[LOG] Nhật ký đã được làm mới để tiết kiệm bộ nhớ."
            )

    def show_error_devices_popup(self):

        dlg = QDialog(self)
        dlg.setWindowTitle("THIẾT BỊ ĐANG LỖI")
        dlg.setWindowIcon(QIcon(APP_ICON_PATH))
        dlg.resize(520, 380)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header_label = QLabel("Danh sách thiết bị đang ở trạng thái Down và CHƯA được khắc phục:")
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        layout.addWidget(header_label)

        rows: list[tuple[str, str, str, str]] = []

        for info in self.device_error_rows:
            if not info.get("active", False):
                continue

            unit_id = info.get("equipment_unit_id")
            if not unit_id:
                continue

            if unit_id not in self.down_equipments:
                continue

            if unit_id in OHT_DOWN_EQUIPMENTS:
                eq_type = "OHT"
            elif unit_id in AGV_DOWN_EQUIPMENTS:
                eq_type = "AGV"
            elif unit_id in STK_DOWN_EQUIPMENTS:
                eq_type = "STK"
            elif unit_id in PORT_DOWN_EQUIPMENTS:
                eq_type = "PORT"
            elif unit_id in BUFFER_DOWN_EQUIPMENTS:
                eq_type = "BUFFER"
            else:
                eq_type = "Khác"

            labels = info.get("labels", {})
            duration_text = labels.get("duration").text() if labels.get("duration") else ""
            action_text = labels.get("action").text() if labels.get("action") else "Chưa sửa"

            rows.append((unit_id, eq_type, duration_text, action_text))

        if not rows:
            empty_label = QLabel("Hiện không có thiết bị nào đang ở trạng thái Down.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 20px;")
            layout.addWidget(empty_label)
        else:
            table = QTableWidget()
            table.setColumnCount(4)
            table.setRowCount(len(rows))
            table.setHorizontalHeaderLabels(["THIẾT BỊ", "LOẠI", "THỜI GIAN LỖI", "HÀNH ĐỘNG"])

            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setDefaultSectionSize(110)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)

            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    background-color: #f8f9fa;
                    font-size: 11px;
                }
                QHeaderView::section {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2c3e50, stop:1 #34495e);
                    color: white;
                    padding: 4px;
                    border: none;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

            for row_idx, (unit_id, eq_type, duration_text, action_text) in enumerate(rows):
                item0 = QTableWidgetItem(unit_id)
                item1 = QTableWidgetItem(eq_type)
                item2 = QTableWidgetItem(duration_text)
                item3 = QTableWidgetItem(action_text)

                item0.setTextAlignment(Qt.AlignCenter)
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)
                item3.setTextAlignment(Qt.AlignCenter)

                table.setItem(row_idx, 0, item0)
                table.setItem(row_idx, 1, item1)
                table.setItem(row_idx, 2, item2)
                table.setItem(row_idx, 3, item3)

            layout.addWidget(table)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dlg.reject)
        close_btn = button_box.button(QDialogButtonBox.Close)
        if close_btn:
            close_btn.setText("Đóng")
        layout.addWidget(button_box)

        dlg.exec()

    def show_stk_full_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("STOCKER GẦN ĐẦY")
        dlg.setWindowIcon(QIcon(APP_ICON_PATH))
        dlg.resize(520, 380)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header_label = QLabel(
            "Danh sách Stocker đang trong trạng thái GẦN ĐẦY (>= 90%) và đang được giám sát:"
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        layout.addWidget(header_label)

        rows: list[tuple[str, str, str]] = []

        for eqp, is_full in sorted(self.zone_full_state.items()):
            if not is_full:
                continue
            if eqp not in self.enabled_stk_full:
                continue

            usage = self.zone_usage_percent.get(eqp)
            if usage is None:
                continue

            stocker_id = eqp
            status_text = f"{usage:.1f}%" 
            note_text = "Đang được giám sát"

            rows.append((stocker_id, status_text, note_text))

        if not rows:
            empty_label = QLabel("Hiện không có Stocker nào đang trong trạng thái gần đầy (>= 90%).")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 20px;")
            layout.addWidget(empty_label)
        else:
            table = QTableWidget()
            table.setColumnCount(3)
            table.setRowCount(len(rows))
            table.setHorizontalHeaderLabels(["STOCKER", "ĐÃ SỬ DỤNG", "GHI CHÚ"])

            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setDefaultSectionSize(150)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)

            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    background-color: #f8f9fa;
                    font-size: 11px;
                }
                QHeaderView::section {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2c3e50, stop:1 #34495e);
                    color: white;
                    padding: 4px;
                    border: none;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

            for row_idx, (stocker_id, status_text, note_text) in enumerate(rows):
                item0 = QTableWidgetItem(stocker_id)
                item1 = QTableWidgetItem(status_text)
                item2 = QTableWidgetItem(note_text)

                item0.setTextAlignment(Qt.AlignCenter)
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)

                table.setItem(row_idx, 0, item0)
                table.setItem(row_idx, 1, item1)
                table.setItem(row_idx, 2, item2)

            layout.addWidget(table)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dlg.reject)
        close_btn = button_box.button(QDialogButtonBox.Close)
        if close_btn:
            close_btn.setText("Đóng")
        layout.addWidget(button_box)

        dlg.exec()

    def show_lost_tray_popup(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("TRAY MẤT LỆNH DI CHUYỂN")
        dlg.setWindowIcon(QIcon(APP_ICON_PATH))
        dlg.resize(520, 380)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header_label = QLabel(
            "Danh sách BUFFER/PORT có Tray bị mất lệnh di chuyển:"
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        layout.addWidget(header_label)

        rows: list[tuple[str, str, str]] = []

        for loc in sorted(self.lost_tray_locations):
            if loc in BUFFER_DOWN_EQUIPMENTS or loc in BUFFER_UNKNOWN_EQUIPMENTS:
                eq_type = "BUFFER"
            elif loc in PORT_DOWN_EQUIPMENTS or loc in PORT_DELAY_EQUIPMENTS:
                eq_type = "PORT"
            else:
                eq_type = "Khác"

            status_text = "Mất lệnh di chuyển"
            rows.append((loc, eq_type, status_text))

        if not rows:
            empty_label = QLabel("Hiện không có BUFFER/PORT nào đang bị mất lệnh di chuyển.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 20px;")
            layout.addWidget(empty_label)
        else:
            table = QTableWidget()
            table.setColumnCount(3)
            table.setRowCount(len(rows))
            table.setHorizontalHeaderLabels(["LOCATION", "LOẠI", "TRẠNG THÁI"])

            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setDefaultSectionSize(150)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)

            table.setStyleSheet("""
                QTableWidget {
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                    background-color: #f8f9fa;
                    font-size: 11px;
                }
                QHeaderView::section {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2c3e50, stop:1 #34495e);
                    color: white;
                    padding: 4px;
                    border: none;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

            for row_idx, (loc, eq_type, status_text) in enumerate(rows):
                item0 = QTableWidgetItem(loc)
                item1 = QTableWidgetItem(eq_type)
                item2 = QTableWidgetItem(status_text)

                item0.setTextAlignment(Qt.AlignCenter)
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)

                table.setItem(row_idx, 0, item0)
                table.setItem(row_idx, 1, item1)
                table.setItem(row_idx, 2, item2)

            layout.addWidget(table)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dlg.reject)
        close_btn = button_box.button(QDialogButtonBox.Close)
        if close_btn:
            close_btn.setText("Đóng")
        layout.addWidget(button_box)

        dlg.exec()

    def on_device_history_item_clicked(self, item: QListWidgetItem):
        target_info = None
        for info in self.device_error_rows:
            if info.get("item") is item:
                target_info = info
                break

        if not target_info:
            return

        unit_id = target_info.get("equipment_unit_id")
        if not unit_id:
            return
        self._show_alarm_detail_popup(unit_id)

    def _show_alarm_detail_popup(self, unit_id: str):
        if unit_id in OHT_DOWN_EQUIPMENTS:
            eq_type = "OHT"
        elif unit_id in AGV_DOWN_EQUIPMENTS:
            eq_type = "AGV"
        elif unit_id in STK_DOWN_EQUIPMENTS:
            eq_type = "STK"
        elif unit_id in PORT_DOWN_EQUIPMENTS:
            eq_type = "Port"
        else:
            eq_type = "UNKNOWN"

        alarm_info = getattr(self, "last_alarm_by_unit", {}).get(unit_id)
        if not alarm_info:
            dlg = QDialog(self)
            dlg.setWindowTitle(f"CHI TIẾT LỖI - {unit_id}")
            dlg.setWindowIcon(QIcon(APP_ICON_PATH))
            dlg.resize(420, 220)

            dlg.setStyleSheet("""
                QDialog {
                    background-color: #ecf0f1;
                }
                QLabel {
                    font-size: 11px;
                    color: #2c3e50;
                }
            """)

            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(10)

            header = QLabel(f"🔎 CHI TIẾT LỖI THIẾT BỊ - {unit_id}")
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 5px 10px;
                    border-radius: 8px;
                }
            """)
            layout.addWidget(header)

            msg = QLabel(
                "Hiện tại chưa có thông tin chi tiết (AlarmReport) cho thiết bị này.\n"
                "Có thể MCS chưa gửi bản tin AlarmReport tương ứng."
            )
            msg.setAlignment(Qt.AlignCenter)
            msg.setWordWrap(True)
            msg.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 15px 10px;")
            layout.addWidget(msg)

            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(dlg.reject)
            close_btn = button_box.button(QDialogButtonBox.Close)
            if close_btn:
                close_btn.setText("Đóng")
            layout.addWidget(button_box)

            dlg.exec()
            return

        eqp_id_raw = alarm_info.get("equipment_id", "") or ""
        alarm_id_raw = alarm_info.get("alarm_id", "") or ""
        prefilled_alarm_name = alarm_info.get("alarm_name", None)
        raw_alarm_text = alarm_info.get("alarm_text", None)
        alarm_time = alarm_info.get("time", "") or "-"

        equipment_id = str(eqp_id_raw).strip()
        alarm_id = str(alarm_id_raw).strip()

        if isinstance(raw_alarm_text, str) and raw_alarm_text.strip():
            alarm_name = self._build_alarm_display_name(
                eq_type,
                equipment_id,
                alarm_id,
                raw_alarm_text
            )
        else:
            mapped = self._get_alarm_name(eq_type, equipment_id, alarm_id)
            if mapped:
                alarm_name = mapped
            else:
                if prefilled_alarm_name and str(prefilled_alarm_name).strip():
                    alarm_name = str(prefilled_alarm_name).strip()
                else:
                    alarm_name = f"ALARM {alarm_id} (chưa có mô tả)"

        if isinstance(raw_alarm_text, str) and raw_alarm_text.strip():
            alarm_text_to_show = raw_alarm_text.strip()
        else:
            mapped = self._get_alarm_name(eq_type, equipment_id, alarm_id)
            if mapped:
                alarm_text_to_show = mapped
            else:
                alarm_text_to_show = alarm_name

        dlg = QDialog(self)
        dlg.setWindowTitle(f"CHI TIẾT LỖI - {unit_id}")
        dlg.setWindowIcon(QIcon(APP_ICON_PATH))
        dlg.resize(520, 340)

        dlg.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
            }
            QLabel {
                font-size: 11px;
                color: #2c3e50;
            }
        """)

        main_layout = QVBoxLayout(dlg)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        header = QLabel(f"🔎 CHI TIẾT LỖI THIẾT BỊ - {unit_id}")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 10px;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(header)

        info_card = QFrame()
        info_card.setFrameShape(QFrame.StyledPanel)
        info_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)
        grid = QGridLayout(info_card)
        grid.setContentsMargins(12, 10, 12, 10)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(4)

        def add_row(row, label_text, value_text, bold_value=False):
            lb = QLabel(label_text)
            lb.setStyleSheet("font-weight: bold; color: #7f8c8d;")
            val = QLabel(value_text or "-")
            val.setTextInteractionFlags(Qt.TextSelectableByMouse)
            if bold_value:
                val.setStyleSheet("font-weight: bold; color: #2c3e50;")
            grid.addWidget(lb, row, 0)
            grid.addWidget(val, row, 1)

        add_row(0, "ID thiết bị:", equipment_id, bold_value=True)
        add_row(1, "Loại thiết bị:", eq_type)
        add_row(2, "Mã lỗi (ALARM_ID):", alarm_id, bold_value=True)
        add_row(3, "Tên lỗi:", alarm_name)
        add_row(4, "Thời gian:", alarm_time)

        main_layout.addWidget(info_card)

        desc_frame = QFrame()
        desc_frame.setFrameShape(QFrame.StyledPanel)
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(10, 8, 10, 8)
        desc_layout.setSpacing(6)

        desc_label = QLabel("Mô tả chi tiết từ ALARM_TEXT:")
        desc_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        desc_layout.addWidget(desc_label)

        raw_text = QTextEdit()
        raw_text.setReadOnly(True)
        raw_text.setPlainText(alarm_text_to_show)
        raw_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                background-color: #f8f9fa;
                font-size: 11px;
            }
        """)
        raw_text.setMinimumHeight(90)
        desc_layout.addWidget(raw_text)

        main_layout.addWidget(desc_frame)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dlg.reject)
        close_btn = button_box.button(QDialogButtonBox.Close)
        if close_btn:
            close_btn.setText("Đóng")
        main_layout.addWidget(button_box)

        dlg.exec()

    def toggle_alert(self):
        if not self.alert_enabled:
            self.alert_enabled = True
            self._update_alert_button(True)
            self.append_log("Đã bật cảnh báo, đang kết nối đến Server!")

            self.play_welcome_sound()

            self.start_websocket()
            self.start_oms_websockets()

        else:
            self.append_log(
                "Người dùng TẮT CẢNH BÁO - dừng kết nối WebSocket và ngừng toàn bộ chức năng"
            )

            self.play_bye_sound()

            self._update_alert_button(False)
            self.stop_websocket()
            self.stop_oms_websockets()
            self.alert_enabled = False

    def update_connection_status(self, connected: bool, message: str):
        self.status_label.setText(message)

        bg_color = "#e74c3c"

        if "ĐANG KẾT NỐI" in message:
            bg_color = "#f1c40f"
        if "ĐÃ KẾT NỐI" in message:
            bg_color = "#27ae60"
        if "CHƯA KẾT NỐI" in message:
            bg_color = "#e74c3c"

        self._set_status_label_color(bg_color)
        self.append_log(message)

        if "MẤT KẾT NỐI" in message:
            now = time.monotonic()

            if not hasattr(self, "_last_disconnect_sound"):
                self._last_disconnect_sound = 0

            if now - self._last_disconnect_sound > 60:
                self._last_disconnect_sound = now
                self.play_disconnect_sound()

    def _normalize_equipment_type(self, eq_type_raw: str) -> str:
        t = (eq_type_raw or "").strip()
        if t.upper().startswith("OHT"):
            return "OHT"
        if t.upper().startswith("AGV"):
            return "AGV"
        if t.upper() in ("CRANE", "STK", "STOCKER"):
            return "STK"
        if t.upper().startswith("PORT"):
            return "Port"
        return t or "UNKNOWN"

    def _map_alarm_equipment_id_to_unit_id(self, eq_type: str, eq_id_raw: str) -> str | None:
        eq_id = (eq_id_raw or "").strip()
        if not eq_id:
            return None

        if eq_type in ("OHT", "AGV") and len(eq_id) > 2:
            base = eq_id[:-2]
            suffix = eq_id[-2:]
            try:
                idx = int(suffix)
                return f"{base}-{idx}"
            except ValueError:
                return eq_id

        if eq_type in ("STK", "Port"):
            return eq_id

        return eq_id

    def _get_alarm_name(self, eq_type: str, equipment_id: str, alarm_id: str) -> str | None:
        alarm_id = (alarm_id or "").strip()
        if not alarm_id:
            return None

        if eq_type == "OHT":
            return OHT_ALARM_NAMES.get(alarm_id)

        if eq_type == "AGV":
            return AGV_ALARM_NAMES.get(alarm_id)

        if eq_type == "STK":
            eqp = (equipment_id or "").strip()
            if eqp in STK_ALARM_GROUP1_EQUIPMENTS:
                return STK_ALARM_NAMES_GROUP1.get(alarm_id)
            if eqp in STK_ALARM_GROUP2_EQUIPMENTS:
                return STK_ALARM_NAMES_GROUP2.get(alarm_id)
            return None

        return None

    def _build_alarm_display_name(self, eq_type: str, equipment_id: str,
                                  alarm_id: str, alarm_text: str) -> str:
        import re

        text = (alarm_text or "").strip()
        if text:
            if eq_type == "Port":
                m = re.search(r"(\[[^\]]+\][^\[]*)\s*$", text)
                if m:
                    return m.group(1).strip()

                last_idx = text.rfind("[")
                if last_idx != -1:
                    return text[last_idx:].strip()

            m = re.search(r"\]\s*(.+)$", text)
            if m:
                return m.group(1).strip()

            if not (text.startswith("[") and text.endswith("]")):
                return text

        mapped = self._get_alarm_name(eq_type, equipment_id, alarm_id)
        if mapped:
            return mapped

        return f"ALARM {alarm_id} (chưa có mô tả cấu hình)"

    def handle_ws_message(self, data: dict):
        if not self.alert_enabled:
            return
        event_id = data.get("EVENTID")

        equipment_type = data.get("EQUIPMENTTYPE")
        equipment_unit_id = data.get("EQUIPMENTUNITID")
        state = data.get("STATE")
        controller_id = data.get("CONTROLLERID")
        equipment_id = data.get("EQUIPMENTID")
        location = data.get("LOCATION")
        carrier_type = data.get("CARRIERTYPE")
        transfer_state = data.get("TRANSFER_STATE")
        zone_equipment_id = data.get("EQUIPMENT_ID")
        max_capacity = data.get("MAX_CAPACITY")
        used_capacity = data.get("USED_CAPACITY")

        if not event_id:
            return

        if event_id == "EquipmentunittateChange":
            if not state:
                return

            unit_id = equipment_unit_id

            if state == "Down" and unit_id and unit_id in self.down_equipments:
                self.debug_log(f"[IGNORE-DOWN] Bỏ qua Down lặp lại cho {unit_id} (đã đang lỗi)")
                return

            if state == "Down" and unit_id:
                if unit_id in STK_DOWN_EQUIPMENTS or unit_id in PORT_DOWN_EQUIPMENTS:
                    now_ts = time.monotonic()
                    last_ts = self.last_down_event_ts.get(unit_id)
                    if last_ts is not None and (now_ts - last_ts) < 1.0:
                        self.debug_log(f"[DEBOUNCE] Bỏ qua Down lặp lại quá nhanh cho {unit_id}")
                        return
                    self.last_down_event_ts[unit_id] = now_ts

            good_recover_states = ("Idle", "Run", "LoadRequest", "UnLoadRequest")

            if unit_id in SPECIAL_WAIT_ONLY_OHT:
                if state == "Wait":
                    self._remove_down_equipment(unit_id)
                    self._mark_device_error_recovered(unit_id, state)
            else:
                good_recover_states = ("Idle", "Run", "LoadRequest", "UnLoadRequest")
                if unit_id and state in good_recover_states:
                    self._remove_down_equipment(unit_id)
                    self._mark_device_error_recovered(unit_id, state)

            if not equipment_id or not equipment_type:
                return

            if equipment_type == "OHT":
                if unit_id in self.enabled_oht_down and state == "Down":
                    self.append_log(f"[OHT] Thiết bị {unit_id} đang ở trạng thái Down")
                    self.play_oht_down_sound(unit_id)
                    self.add_device_history_row(unit_id, state)
                    self._add_down_equipment(unit_id)

            elif equipment_type == "AGV":
                if unit_id in self.enabled_agv_down and state == "Down":
                    self.append_log(f"[AGV] Thiết bị {unit_id} đang ở trạng thái Down")
                    self.play_agv_down_sound(unit_id)
                    self.add_device_history_row(unit_id, state)
                    self._add_down_equipment(unit_id)

                elif unit_id in self.enabled_agv_down and state == "Manual":
                    self.debug_log(
                        f"[AGV] Thiết bị {unit_id} chuyển sang chế độ Manual"
                    )
                    self.add_device_history_row(unit_id, state)

            elif equipment_type == "Stocker":
                if unit_id in self.enabled_stk_down and state == "Down":
                    self.append_log(f"[STK] Thiết bị {unit_id} đang ở trạng thái Down")
                    self.play_stk_down_sound(unit_id)
                    self.add_device_history_row(unit_id, state)
                    self._add_down_equipment(unit_id)

                elif unit_id in self.enabled_port_down and state == "Down":
                    self.append_log(f"[PORT] Thiết bị {unit_id} đang ở trạng thái Down")
                    self.play_port_down_sound(unit_id)
                    self.add_device_history_row(unit_id, state)
                    self._add_down_equipment(unit_id)

                if state in ("Idle", "Run"):
                    self._remove_lost_tray(equipment_unit_id)

            elif equipment_type == "Process":
                if unit_id in self.enabled_buffer_down and state == "Down":
                    self.append_log(f"[BUFFER] Thiết bị {unit_id} đang ở trạng thái Down")
                    self.play_buffer_down_sound(unit_id)
                    self.add_device_history_row(unit_id, state)
                    self._add_down_equipment(unit_id)

                if state in ("LoadRequest", "UnLoadRequest"):
                    self._schedule_lost_tray_recover(
                        equipment_unit_id,
                        60.0,
                        f"Process state = {state}"
                    )

            return

        if event_id == "ControlStateChange":
            if not controller_id or not state:
                return

            if controller_id in self.enabled_oht_status and state in ("Auto", "Offline"):
                self.append_log(
                    f"[OHT-STATUS] {controller_id} state = {state}, phát cảnh báo âm thanh"
                )
                self.play_oht_status_sound(controller_id, state)
                self.add_device_history_row(controller_id, state)

            if controller_id in OHT_STATUS_EQUIPMENTS:
                if state == "Offline":
                    self._set_oht_jam_block_by_controller(controller_id, True)
                elif state == "Auto":
                    self._set_oht_jam_block_by_controller(controller_id, False)

            if controller_id in self.enabled_agv_status and state in ("Auto", "Paused", "Offline"):
                self.append_log(
                    f"[AGV-STATUS] {controller_id} state = {state}, phát cảnh báo âm thanh"
                )
                self.play_agv_status_sound(controller_id, state)
                self.add_device_history_row(controller_id, state)

            if controller_id in self.enabled_stk_status and state in ("Auto", "Offline"):
                self.append_log(
                    f"[STK-STATUS] {controller_id} state = {state}, phát cảnh báo âm thanh"
                )
                self.play_stk_status_sound(controller_id, state)
                self.add_device_history_row(controller_id, state)

            return

        if event_id == "EquipmentStateChange":
            if not equipment_id or not state:
                return

            if equipment_id in self.enabled_oht_status and state == "Paused":
                self.append_log(
                    f"[OHT-STATUS] {equipment_id} state = {state}, phát cảnh báo âm thanh"
                )
                self.play_oht_status_sound(equipment_id, state)
                self.add_device_history_row(equipment_id, state)

            if equipment_id in OHT_STATUS_EQUIPMENTS and state == "Paused":
                self._set_oht_jam_block_by_controller(equipment_id, True)

            return

        if event_id == "AlarmReport":
            eq_type_raw = data.get("EQUIPMENT_TYPE") or data.get("EQUIPMENTTYPE") or ""
            eq_id_raw = data.get("EQUIPMENT_ID") or data.get("EQUIPMENTID") or ""
            alarm_id_raw = data.get("ALARM_ID") or ""
            raw_alarm_text = data.get("ALARM_TEXT")
            alarm_time = data.get("TIME", "")

            if isinstance(raw_alarm_text, str):
                alarm_text = raw_alarm_text.strip()
            else:
                alarm_text = ""

            eq_type = self._normalize_equipment_type(eq_type_raw)
            equipment_id = (eq_id_raw or "").strip()
            alarm_id = str(alarm_id_raw).strip()

            if equipment_id and alarm_id:
                unit_key = self._map_alarm_equipment_id_to_unit_id(eq_type, equipment_id)

                valid = False
                if eq_type == "OHT" and unit_key in OHT_DOWN_EQUIPMENTS:
                    valid = True
                elif eq_type == "AGV" and unit_key in AGV_DOWN_EQUIPMENTS:
                    valid = True
                elif eq_type == "STK" and unit_key in STK_DOWN_EQUIPMENTS:
                    valid = True
                elif eq_type == "Port" and unit_key in PORT_DOWN_EQUIPMENTS:
                    valid = True

                if valid and unit_key:
                    display_name = self._build_alarm_display_name(
                        eq_type,
                        equipment_id,
                        alarm_id,
                        alarm_text,
                    )
                    self.last_alarm_by_unit[unit_key] = {
                        "unit_id": unit_key,
                        "eq_type": eq_type,
                        "equipment_id": equipment_id,
                        "alarm_id": alarm_id,
                        "alarm_name": display_name,
                        "alarm_text": alarm_text,
                        "time": alarm_time,
                    }

            import re
            matches = re.findall(r"\[([A-Za-z0-9\-]+)\]", alarm_text)

            if len(matches) < 2:
                return

            port_id = matches[1].strip()

            if port_id not in PORT_DELAY_EQUIPMENTS:
                return

            delay_tag = None
            if "No Transfer after Wait OUT 5 Min" in alarm_text:
                delay_tag = "5Phut"
            elif "No Transfer after Wait OUT 10 Min" in alarm_text:
                delay_tag = "10Phut"

            if not delay_tag:
                return

            if delay_tag == "5Phut" and port_id not in self.enabled_port_delay_5:
                return
            if delay_tag == "10Phut" and port_id not in self.enabled_port_delay_10:
                return

            self.append_log(
                f"[PORT-DELAY] {port_id} bị treo lệnh {delay_tag} - AlarmReport"
            )

            self.play_port_delay_sound(port_id, delay_tag)
            self.add_device_history_row(port_id, f"Delay {delay_tag}")

            return

        if event_id == "CarrierLocationChange":
            if not location:
                return

            loc = location.strip()
            ct = (carrier_type or "").strip()
            ts = (transfer_state or "").strip()

            ct_norm = ct.lower()
            ts_norm = ts.lower()

            if loc in self.enabled_buffer_unknown:

                if loc in BUFFER_UNKNOWN_EXCLUDE_unit:
                    self.debug_log(
                        f"[BUFFER-UNKNOWN-SKIP] {loc} nằm trong danh sách loại trừ UnKnown"
                    )
                    return

                if ct_norm == "unknown":
                    if loc in self.lost_tray_locations:
                        self.debug_log(
                            f"[BUFFER-UNKNOWN-IGNORE] {loc} đã mất lệnh, bỏ qua cảnh báo lặp"
                        )
                    else:
                        self.append_log(
                            f"[BUFFER] {loc} có tray UnKnown, phát cảnh báo mất lệnh"
                        )
                        self.play_buffer_unknown_sound(loc)
                        self.add_device_history_row(loc, "UnKnown")
                        self._add_lost_tray(loc)
                else:
                    self.debug_log(
                        f"[BUFFER-UNKNOWN-SKIP] {loc} CARRIERTYPE={ct} ≠ UnKnown"
                    )

            valid_port_carrier_types = {"unknown", "full", "empty"}

            if loc in self.enabled_port_unknown:
                if (
                    ts_norm in ("not_trasnferring", "not_transferring")
                    and ct_norm in valid_port_carrier_types
                ):
                    if loc in self.lost_tray_locations:
                        self.debug_log(
                            f"[PORT-UNKNOWN-IGNORE] {loc} đã mất lệnh, bỏ qua cảnh báo lặp"
                        )
                    else:
                        self.append_log(
                            f"[PORT] {loc} có tray mất lệnh di chuyển "
                            f"(CarrierType={ct}, TransferState={ts})"
                        )
                        self.play_port_unknown_state_sound(loc, ts)
                        self.add_device_history_row(loc, ts)
                        self._add_lost_tray(loc)
                else:
                    self.debug_log(
                        f"[PORT-UNKNOWN-SKIP] {loc} CarrierType={ct}, TransferState={ts}"
                    )

            if loc in self.lost_tray_locations and ts_norm in (
                "eq_transferring",
                "transferring",
            ):
                self._schedule_lost_tray_recover(
                    loc,
                    60.0,
                    f"TRANSFER_STATE = {ts}",
                )

            return

        if event_id == "ZoneCapacityChange":
            if not zone_equipment_id or max_capacity is None or used_capacity is None:
                return

            eqp = str(zone_equipment_id).strip()

            if eqp not in STK_STATUS_EQUIPMENTS:
                return

            try:
                max_cap_val = float(max_capacity)
                used_cap_val = float(used_capacity)
            except (TypeError, ValueError):
                return

            if max_cap_val <= 0:
                return

            usage_percent = used_cap_val / max_cap_val * 100.0

            self.zone_usage_percent[eqp] = usage_percent

            prev_full = self.zone_full_state.get(eqp, False)

            if usage_percent >= 90.0 and not prev_full:
                self.zone_full_state[eqp] = True

                if eqp in self.enabled_stk_full:
                    self.append_log(
                        f"[STK] {eqp} đã sử dụng {usage_percent:.1f}%/100%, phát cảnh báo gần đầy"
                    )
                    self.play_stk_full_sound(eqp)
                    self.add_device_history_row(eqp, f"Full {usage_percent:.1f}%")

                self._update_stk_near_full_stat()

            elif usage_percent <= 86.0 and prev_full:
                self.zone_full_state[eqp] = False
                self.append_log(
                    f"[STK] Thiết bị {eqp} giảm xuống {usage_percent:.1f}%/100%, reset trạng thái"
                )
                self._update_stk_near_full_stat()
            return

        return

    def _play_sound_file(self, cache_key: str, log_prefix: str, sound_path: str):
        if not self.alert_enabled:
            self.append_log(f"{log_prefix} nhưng cảnh báo đang TẮT, không phát âm thanh")
            return

        if not os.path.exists(sound_path):
            self.append_log(f"{log_prefix} KHÔNG TÌM THẤY FILE: {sound_path}")
            return

        self.sound_queue.append((cache_key, log_prefix, sound_path))
        self.debug_log(f"{log_prefix} Thêm vào hàng đợi: {sound_path}")

        if self.current_player is None:
            self._start_next_sound()

    def _start_next_sound(self):
        if not self.sound_queue:
            self.current_player = None
            return

        cache_key, log_prefix, sound_path = self.sound_queue.pop(0)

        audio_output = QAudioOutput(self)
        player = QMediaPlayer(self)
        player.setAudioOutput(audio_output)
        player.setSource(QUrl.fromLocalFile(sound_path))
        audio_output.setVolume(1.0)

        self.current_player = (player, audio_output, cache_key)
        self.sound_cache[cache_key] = (player, audio_output)

        from PySide6.QtMultimedia import QMediaPlayer as _QMP

        def _on_state_changed(state):
            if state == _QMP.StoppedState:
                try:
                    player.playbackStateChanged.disconnect(_on_state_changed)
                except Exception:
                    pass

                if cache_key in self.sound_cache:
                    del self.sound_cache[cache_key]

                self.current_player = None
                self._start_next_sound()

        player.playbackStateChanged.connect(_on_state_changed)
        player.play()
        self.debug_log(f"{log_prefix} ĐANG PHÁT: {sound_path}")

    def maybe_play_funny_sound(self):
        current_time = time.time()

        if current_time - self.last_funny_sound_time < 300:
            return

        if random.random() > 0.05:
            return

        selected_file = self.funny_sound_list[self.funny_sound_index]

        self.funny_sound_index += 1

        if self.funny_sound_index >= len(self.funny_sound_list):
            self.funny_sound_index = 0

        sound_path = os.path.join(
            self.base_dir,
            "sound",
            "Funny",
            selected_file
        )

        self._play_sound_file(
            "FUNNY-RESET",
            "[ÂM THANH VUI]",
            sound_path
        )

        self.last_funny_sound_time = current_time

    def play_oht_down_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Down.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "OHT-Down", filename)
        cache_key = f"OHT-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH OHT]", sound_path)

    def play_oht_status_sound(self, equipment_id: str, state: str):
        filename = f"{equipment_id}-{state}.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "OHT-Status", filename)
        cache_key = f"OHT-STATUS-{equipment_id}-{state}"
        self._play_sound_file(cache_key, "[ÂM THANH OHT-STATUS]", sound_path)

    def play_oht_stopped_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Stopped.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "OHT-Stopped", filename)
        cache_key = f"OHT-STOPPED-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH OHT-STOPPED]", sound_path)

    def play_oht_disconnected_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Disconnected.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "OHT-Disconnected", filename)
        cache_key = f"OHT-DISCONNECTED-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH OHT-DISCONNECTED]", sound_path)

    def play_agv_down_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Down.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "AGV-Down", filename)
        cache_key = f"AGV-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH AGV]", sound_path)

    def play_agv_status_sound(self, controller_id: str, state: str):
        filename = f"{controller_id}-{state}.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "AGV-Status", filename)
        cache_key = f"AGV-STATUS-{controller_id}-{state}"
        self._play_sound_file(cache_key, "[ÂM THANH AGV-STATUS]", sound_path)

    def play_stk_down_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Down.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "STK-Down", filename)
        cache_key = f"STK-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH STOCKER]", sound_path)

    def play_stk_status_sound(self, controller_id: str, state: str):
        filename = f"{controller_id}-{state}.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "STK-Status", filename)
        cache_key = f"STK-STATUS-{controller_id}-{state}"
        self._play_sound_file(cache_key, "[ÂM THANH STK-STATUS]", sound_path)

    def play_stk_full_sound(self, equipment_id: str):
        filename = f"{equipment_id}-Full.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "STK-Full", filename)
        cache_key = f"STK-FULL-{equipment_id}"
        self._play_sound_file(cache_key, "[ÂM THANH STK-FULL]", sound_path)

    def play_port_down_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Down.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "PORT-Down", filename)
        cache_key = f"PORT-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH PORT]", sound_path)

    def play_port_delay_sound(self, port_id: str, delay_tag: str):
        filename = f"{port_id}-{delay_tag}.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "PORT-Delay", filename)
        cache_key = f"PORT-DELAY-{port_id}-{delay_tag}"
        self._play_sound_file(cache_key, "[ÂM THANH PORT-DELAY]", sound_path)

    def play_port_unknown_state_sound(self, location: str, transfer_state: str):
        filename = f"{location}-{transfer_state}.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "PORT-UnKnown", filename)
        cache_key = f"PORT-UNKNOWN-{location}-{transfer_state}"
        self._play_sound_file(cache_key, "[ÂM THANH PORT-UNKNOWN]", sound_path)

    def play_buffer_down_sound(self, equipment_unit_id: str):
        filename = f"{equipment_unit_id}-Down.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "BUFFER-Down", filename)
        cache_key = f"BUFFER-{equipment_unit_id}"
        self._play_sound_file(cache_key, "[ÂM THANH BUFFER]", sound_path)

    def play_buffer_unknown_sound(self, location: str):
        filename = f"{location}-UnKnown.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "BUFFER-UnKnown", filename)
        cache_key = f"BUFFER-UNKNOWN-{location}"
        self._play_sound_file(cache_key, "[ÂM THANH BUFFER-UNKNOWN]", sound_path)

    def play_error_duration_sound(self, minutes: int):
        if minutes not in (5, 10, 30, 60):
            return

        filename = f"Loi{minutes}p.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "Error-Phut", filename)
        cache_key = f"ERROR-PHUT-{minutes}"

        filename = f"Loi{minutes}p.mp3"
        sound_path = os.path.join(self.base_dir, "sound", "Error-Phut", filename)
        cache_key = f"ERROR-PHUT-{minutes}"

        self._play_sound_file(cache_key, "[ÂM THANH ERROR-PHUT-CHUNG]", sound_path)

    def add_device_history_row(self, equipment_unit_id: str, state: str):
        if state not in ("Down", "Manual"):
            return

        for info in self.device_error_rows:
            if (
                info.get("equipment_unit_id") == equipment_unit_id
                and info.get("active", False)
            ):
                self.debug_log(
                    f"[DEVICE-HISTORY-IGNORE] Bỏ qua tạo dòng mới cho {equipment_unit_id} vì vẫn đang lỗi (chưa sửa)."
                )
                return

        if equipment_unit_id in OHT_DOWN_EQUIPMENTS:
            equipment_type = "OHT"
        elif equipment_unit_id in AGV_DOWN_EQUIPMENTS:
            equipment_type = "AGV"
        elif equipment_unit_id in STK_DOWN_EQUIPMENTS or equipment_unit_id in PORT_DOWN_EQUIPMENTS:
            equipment_type = "Stocker"
        elif equipment_unit_id in BUFFER_DOWN_EQUIPMENTS:
            equipment_type = "Process"
        else:
            return

        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")

        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(15, 4, 15, 4)
        layout.setSpacing(0)

        time_label = QLabel(time_str)
        equip_label = QLabel(equipment_unit_id)
        type_label = QLabel(equipment_type)
        state_label = QLabel(state)
        duration_label = QLabel("0 phút")
        action_label = QLabel("❌Chưa sửa")

        labels = [
            time_label,
            equip_label,
            type_label,
            state_label,
            duration_label,
            action_label,
        ]

        for lbl in labels:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                """
                QLabel {
                    font-size: 11px;
                    padding: 4px 2px;
                    color: #2c3e50;
                }
                """
            )
            layout.addWidget(lbl, 1)

        list_item = QListWidgetItem(self.device_status_widget.device_list)
        list_item.setSizeHint(item_widget.sizeHint())
        self.device_status_widget.device_list.addItem(list_item)
        self.device_status_widget.device_list.setItemWidget(list_item, item_widget)

        row_info = {
            "equipment_unit_id": equipment_unit_id,
            "item": list_item,
            "widget": item_widget,
            "labels": {
                "time": time_label,
                "equipment": equip_label,
                "type": type_label,
                "state": state_label,
                "duration": duration_label,
                "action": action_label,
            },
            "start_time": now,
            "active": True,
            "warn_10": False,
            "warn_30": False,
            "warn_60": False,
        }

        self.device_error_rows.append(row_info)
        self._trim_device_history_rows()
        self.device_status_widget.device_list.scrollToBottom()

    def test_sound(self):
        sample_id = "HNMOHV01-1" 
        self.append_log(f"TEST ÂM THANH với thiết bị {sample_id}")
        if not self.alert_enabled:
            self.append_log("Cảnh báo đang TẮT, tự bật tạm để test âm thanh")
            self.alert_enabled = True
        self.play_oht_down_sound(sample_id)

    def closeEvent(self, event):
        try:
            if hasattr(self, "ws_worker") and self.ws_worker is not None:
                self.ws_worker.stop()
        except Exception:
            pass

        try:
            self.stop_oms_websockets()
        except Exception:
            pass

        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app_icon = QIcon(APP_ICON_PATH)
    app.setWindowIcon(app_icon)

    oht_img = resource_path("oht.png")
    agv_img = resource_path("agv.png")

    splash = LoadingScreen(
        oht_img,
        agv_img,
        switch_ms=1000,
        total_ms=2500,
        version="2.0.0",
        author="Ngô Tôn Quyền",
    )
    splash.start()

    window = MainWindow()

    def on_splash_finished():
        splash.close()

        window.show()

        window.raise_()
        window.activateWindow()

        window.setWindowState(
            window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
        )

        QTimer.singleShot(100, window.activateWindow)

    splash.finished.connect(on_splash_finished)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
