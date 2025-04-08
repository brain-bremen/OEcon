from enum import Enum


class VStimEventCode(Enum):
    NullEvent = 0

    # System / VStim
    SystemWarning = 1  # reserved, not yet used
    SystemError = 2  # reserved, not yet used,
    SystemMessage = 3  # reserved, not yet used,
    UserMessage = 4  # reserved, not yet used,
    VStimStarted = 5  # reserved, not yet used,
    VStimEnded = 6  # reserved, not yet used,
    NewConfigLoaded = 7
    ResponseRequested = 8

    # Digital Inputs: lever / button / lick
    LeverPressed = 10
    LeverPressed1 = 11
    LeverPressed2 = 12
    LeverPressed3 = 13

    LeverReleased = 20
    LeverReleased1 = 21
    LeverReleased2 = 22
    LeverReleased3 = 23

    # Eye Position
    EyeWentInWindow = 30
    EyeReachedTarget1 = 31
    EyeReachedTarget2 = 32
    EyeReachedTarget3 = 33
    EyeReachedTarget4 = 34
    EyeReachedTarget5 = 35
    EyeReachedTarget6 = 36
    EyeReachedTarget7 = 37
    EyeReachedTarget8 = 38
    EyeReachedTarget9 = 39

    EyeWentOutWindow = 40
    EyeLeftTarget1 = 41

    # trial outcome: 50-59
    TrialEnded = 49
    TrialEndedWithNotStarted = 50
    TrialEndedWithHit = 51
    TrialEndedWithWrongResponse = 52
    TrialEndedWithEarlyHit = 53
    TrialEndedWithEarlyWrongResponse = 54
    TrialEndedWithEarly = 55
    TrialEndedWithLate = 56
    TrialEndedWithEyeErr = 57
    TrialEndedWithInexpectedStartSignal = 58
    TrialEndedWithWrongStartSignal = 59
    TrialWasCancelledByUser = 60

    # Trial Type Sets
    NewTrialTypeSetLoaded = 61
    LoadedTrialTypeSet1 = 61
    LoadedTrialTypeSet2 = 62
    LoadedTrialTypeSet3 = 63
    LoadedTrialTypeSet4 = 64
    LoadedTrialTypeSet5 = 65
    LoadedTrialTypeSet6 = 66
    LoadedTrialTypeSet7 = 67
    LoadedTrialTypeSet8 = 68
    LoadedTrialTypeSet9 = 69

    TrialTypeConfigChanged = 70
    IntervalConfigChanged = 71
    TrialTypeNumberChanged = 72
    TrialTypeManagerConfigChanged = 73
    RoundStarted = 74
    RoundEnded = 75
    TrialOutcomeCounterUpdated = 76  # reserved, not yet used
    TrialOutcomeCounterWereReset = 77
    TdrRecordingStarted = 80
    TdrRecordingPaused = 81
    TdrRecordingResumed = 82
    TdrRecordingEnded = 83

    # interval starts: 100-199
    IntervalStarted = 100
    Interval1Started = 101
    Interval2Started = 102
    Interval3Started = 103
    Interval4Started = 104
    Interval5Started = 105
    Interval6Started = 106
    Interval7Started = 107
    Interval8Started = 108
    Interval9Started = 109
    Interval10Started = 110
    Interval11Started = 111
    Interval12Started = 112
    Interval13Started = 113
    Interval14Started = 114
    Interval15Started = 115
    Interval16Started = 116
    Interval17Started = 117
    Interval18Started = 118
    Interval19Started = 119
    Interval20Started = 120

    # interval ends: 200-299
    IntervalEnded = 200
    Interval1Ended = 201
    Interval2Ended = 202
    Interval3Ended = 203
    Interval4Ended = 204
    Interval5Ended = 205
    Interval6Ended = 206
    Interval7Ended = 207
    Interval8Ended = 208
    Interval9Ended = 209
    Interval10Ended = 210
    Interval11Ended = 211
    Interval12Ended = 212
    Interval13Ended = 213
    Interval14Ended = 214
    Interval15Ended = 215
    Interval16Ended = 216
    Interval17Ended = 217
    Interval18Ended = 218
    Interval19Ended = 219
    Interval20Ended = 220

    # experiment controller
    ExperimentControllerStarted = 300
    ExperimentControllerStopped = 301  # reserved, not yet used
    ExperimentControllerStopAfterSequenceRequested = 302
    ExperimentControllerStopImmediatelyRequested = 303
    ExperimentControllerStartRequested = 304  # reserved not yet used
    ExperimentControllerConfigChanged = 305
    TimeSequenceChanged = 306
    TimeSequenceConfigChanged = 307  # reserved. not yet used
    TrialStarted = 310
    PerfectSubjectEnabled = 311
    PerfectSubjectDisabled = 312

    RewardRequested = 320
    RewardOn = 321
    RewardOff = 322
    TotalRewardWasReset = 323
    FreeRewardRequested = 324

    ReactionTimeWasUpdated = 325

    # rendering
    FrameLoss = 400
    ObjectAdded = 401
    ObjectRemoved = 402
    ObjectReplaced = 403
    ObjectConfigChangeAccepted = 404  # not yet always used in the dialogs
    ObjectConfigChanged = 405
    ObjectVisibilityChanged = 406  # on, off, reason: user/system
    ObjectPositionChanged = 407  # reserved
    ObjectSizeChanged = 408  # reserved
    ObjectRotationChanged = 409  # reserved
    ObjectColorChanged = 410  # reserved
    SelectedObjectChanged = 411
    BackgroundColorChanged = 412

    # Virtual Trigger Lines On: 1000-1099
    VtlOn = 1000
    Vtl1On = 1001
    Vtl2On = 1002
    Vtl3On = 1003
    Vtl4On = 1004
    Vtl5On = 1005
    Vtl6On = 1006
    Vtl7On = 1007
    Vtl8On = 1008
    Vtl9On = 1009
    Vtl10On = 1010
    Vtl11On = 1011
    Vtl12On = 1012
    Vtl13On = 1013
    Vtl14On = 1014
    Vtl15On = 1015
    Vtl16On = 1016
    Vtl17On = 1017
    Vtl18On = 1018
    Vtl19On = 1019
    Vtl20On = 1020
    Vtl21On = 1021
    Vtl22On = 1022
    Vtl23On = 1023
    Vtl24On = 1024
    Vtl25On = 1025
    Vtl26On = 1026
    Vtl27On = 1027
    Vtl28On = 1028
    Vtl29On = 1029
    Vtl30On = 1030
    Vtl31On = 1031
    Vtl32On = 1032
    Vtl33On = 1033
    Vtl34On = 1034
    Vtl35On = 1035
    Vtl36On = 1036
    Vtl37On = 1037
    Vtl38On = 1038
    Vtl39On = 1039
    Vtl40On = 1040
    Vtl41On = 1041
    Vtl42On = 1042
    Vtl43On = 1043
    Vtl44On = 1044
    Vtl45On = 1045
    Vtl46On = 1046
    Vtl47On = 1047
    Vtl48On = 1048
    Vtl49On = 1049
    Vtl50On = 1050
    Vtl51On = 1051
    Vtl52On = 1052
    Vtl53On = 1053
    Vtl54On = 1054
    Vtl55On = 1055
    Vtl56On = 1056
    Vtl57On = 1057
    Vtl58On = 1058
    Vtl59On = 1059
    Vtl60On = 1060
    Vtl61On = 1061
    Vtl62On = 1062
    Vtl63On = 1063
    Vtl64On = 1064
    Vtl65On = 1065
    Vtl66On = 1066
    Vtl67On = 1067
    Vtl68On = 1068
    Vtl69On = 1069
    Vtl70On = 1070
    Vtl71On = 1071
    Vtl72On = 1072
    Vtl73On = 1073
    Vtl74On = 1074
    Vtl75On = 1075
    Vtl76On = 1076
    Vtl77On = 1077
    Vtl78On = 1078
    Vtl79On = 1079
    Vtl80On = 1080
    Vtl81On = 1081
    Vtl82On = 1082
    Vtl83On = 1083
    Vtl84On = 1084
    Vtl85On = 1085
    Vtl86On = 1086
    Vtl87On = 1087
    Vtl88On = 1088
    Vtl89On = 1089
    Vtl90On = 1090
    Vtl91On = 1091
    Vtl92On = 1092
    Vtl93On = 1093
    Vtl94On = 1094
    Vtl95On = 1095
    Vtl96On = 1096
    Vtl97On = 1097
    Vtl98On = 1098
    Vtl99On = 1099

    # Virtual Trigger Lines Off: 1100-1199
    VtlOff = 1100
    Vtl1Off = 1101
    Vtl2Off = 1102
    Vtl3Off = 1103
    Vtl4Off = 1104
    Vtl5Off = 1105
    Vtl6Off = 1106
    Vtl7Off = 1107
    Vtl8Off = 1108
    Vtl9Off = 1109
    Vtl10Off = 1110
    Vtl11Off = 1111
    Vtl12Off = 1112
    Vtl13Off = 1113
    Vtl14Off = 1114
    Vtl15Off = 1115
    Vtl16Off = 1116
    Vtl17Off = 1117
    Vtl18Off = 1118
    Vtl19Off = 1119
    Vtl20Off = 1120
    Vtl21Off = 1121
    Vtl22Off = 1122
    Vtl23Off = 1123
    Vtl24Off = 1124
    Vtl25Off = 1125
    Vtl26Off = 1126
    Vtl27Off = 1127
    Vtl28Off = 1128
    Vtl29Off = 1129
    Vtl30Off = 1130
    Vtl31Off = 1131
    Vtl32Off = 1132
    Vtl33Off = 1133
    Vtl34Off = 1134
    Vtl35Off = 1135
    Vtl36Off = 1136
    Vtl37Off = 1137
    Vtl38Off = 1138
    Vtl39Off = 1139
    Vtl40Off = 1140
    Vtl41Off = 1141
    Vtl42Off = 1142
    Vtl43Off = 1143
    Vtl44Off = 1144
    Vtl45Off = 1145
    Vtl46Off = 1146
    Vtl47Off = 1147
    Vtl48Off = 1148
    Vtl49Off = 1149
    Vtl50Off = 1150
    Vtl51Off = 1151
    Vtl52Off = 1152
    Vtl53Off = 1153
    Vtl54Off = 1154
    Vtl55Off = 1155
    Vtl56Off = 1156
    Vtl57Off = 1157
    Vtl58Off = 1158
    Vtl59Off = 1159
    Vtl60Off = 1160
    Vtl61Off = 1161
    Vtl62Off = 1162
    Vtl63Off = 1163
    Vtl64Off = 1164
    Vtl65Off = 1165
    Vtl66Off = 1166
    Vtl67Off = 1167
    Vtl68Off = 1168
    Vtl69Off = 1169
    Vtl70Off = 1170
    Vtl71Off = 1171
    Vtl72Off = 1172
    Vtl73Off = 1173
    Vtl74Off = 1174
    Vtl75Off = 1175
    Vtl76Off = 1176
    Vtl77Off = 1177
    Vtl78Off = 1178
    Vtl79Off = 1179
    Vtl80Off = 1180
    Vtl81Off = 1181
    Vtl82Off = 1182
    Vtl83Off = 1183
    Vtl84Off = 1184
    Vtl85Off = 1185
    Vtl86Off = 1186
    Vtl87Off = 1187
    Vtl88Off = 1188
    Vtl89Off = 1189
    Vtl90Off = 1190
    Vtl91Off = 1191
    Vtl92Off = 1192
    Vtl93Off = 1193
    Vtl94Off = 1194
    Vtl95Off = 1195
    Vtl96Off = 1196
    Vtl97Off = 1197
    Vtl98Off = 1198
    Vtl99Off = 1199

    # physical TTLs (reserved)
    TtlOutputWordUpdated = 1199
    TtlOn = 1200
    TtlOff = 1300

    MaxSystemEventCode = 0xFFFF

    @classmethod
    def get_event_name(cls, code):
        for event in cls:
            if event.value[0] == code:
                return event.name
        return None

    @classmethod
    def asdict(cls):
        return {event.name: event.value for event in cls}
